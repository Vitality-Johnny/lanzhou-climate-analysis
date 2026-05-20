#!/usr/bin/env python3
"""全部分析+可视化 — 8图 + 统计检验 | 统一Open-Meteo ERA5 1960-2025"""

import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt; from scipy import stats; import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({"font.family":"SimHei","axes.unicode_minus":False,
    "figure.dpi":150,"savefig.dpi":150,"savefig.bbox":"tight",
    "axes.grid":True,"grid.alpha":0.3,"axes.spines.top":False,"axes.spines.right":False})

COL = {"兰州":"#e74c3c","西安":"#3498db","西宁":"#2ecc71"}
SEASONS = ["春","夏","秋","冬"]
SC = {"春":"#27ae60","夏":"#e74c3c","秋":"#f39c12","冬":"#3498db"}

df = pd.read_csv("tidy_climate_data.csv")
annual = pd.read_csv("annual_summary.csv")

def lr(x,y,lab=""):
    m = ~(np.isnan(x)|np.isnan(y)); xc,yc = x[m],y[m]
    if len(xc)<3: return np.nan,np.nan,np.nan,[],[]
    s,i,r,p,_ = stats.linregress(xc,yc); r2=r**2
    if lab: print(f"  {lab}: {s:+.3f}/yr R²={r2:.3f} p={p:.4f}")
    return s,r2,p,xc,s*xc+i

def mk_test(d):
    n=len(d); s=sum(np.sign(d[j]-d[i]) for i in range(n-1) for j in range(i+1,n))
    v=n*(n-1)*(2*n+5)/18; z=(s-1)/np.sqrt(v) if s>0 else (s+1)/np.sqrt(v) if s<0 else 0
    return s,z,2*(1-stats.norm.cdf(abs(z)))

def mk_mut(d):
    n=len(d); UF=np.zeros(n)
    for k in range(1,n):
        ss=sum(np.sign(d[k]-d[j]) for j in range(k))
        UF[k]=(ss-np.sign(ss))/np.sqrt(k*(k-1)*(2*k+5)/18)
    dr=d[::-1]; UB_r=np.zeros(n)
    for k in range(1,n):
        ss=sum(np.sign(dr[k]-dr[j]) for j in range(k))
        UB_r[k]=(ss-np.sign(ss))/np.sqrt(k*(k-1)*(2*k+5)/18)
    UB=-UB_r[::-1]
    mut=[i for i in range(1,n-1) if (UF[i]-UB[i])*(UF[i+1]-UB[i+1])<0 and abs(UF[i])<1.96]
    return UF,UB,mut

def morlet_cwt(data,scales=None):
    n=len(data); dn=(data-np.mean(data))/np.std(data)
    if scales is None: scales=np.arange(2,min(n//2,40))
    fft=np.fft.fft(dn); freqs=np.fft.fftfreq(n)
    cwt=np.zeros((len(scales),n),dtype=complex)
    for i,s in enumerate(scales):
        xi=s*2*np.pi*np.abs(freqs); mf=np.pi**(-.25)*np.exp(-.5*(xi-6)**2); mf[freqs<=0]=0
        cwt[i]=np.fft.ifft(fft*mf*np.sqrt(s))
    return scales,np.abs(cwt)**2

# ===== 分析参数 =====
PERIOD = "1960–2025"  # 全文统一用完整时段

print("="*60+"\n全时段分析 (1960–2025)\n"+"="*60)

# ---- Fig1: 年均温 ----
print("\n[年均温]")
fig,ax=plt.subplots(figsize=(12,6))
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年均温"])
    x,y=d["年"].values,d["年均温"].values
    ax.plot(x,y,"o-",color=COL[c],lw=1.5,ms=3,label=c,zorder=3)
    s,r2,p,xf,yf=lr(x.astype(float),y,f"{c}")
    if len(xf): ax.plot(xf,yf,"--",color=COL[c],lw=1,alpha=.5)
    sig="**" if p<0.05 else "*" if p<0.1 else ""
    ax.annotate(f"{s:+.3f}°C/yr R²={r2:.3f}{sig}",(xf[-1],yf[-1]),
                textcoords="offset points",xytext=(5,5),fontsize=7,color=COL[c])
ax.set(xlabel="年份",ylabel="年均温 (°C)",title=f"图1: 年均温变化趋势 ({PERIOD})")
ax.legend(); fig.tight_layout(); fig.savefig("fig1_年均温趋势.png",dpi=150); plt.close()
print("  ✅ fig1")

# ---- Fig2: 年降水 ----
print("\n[年降水]")
fig,ax=plt.subplots(figsize=(12,6))
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年降水"])
    x,y=d["年"].values,d["年降水"].values
    ax.bar(x,y,color=COL[c],alpha=.3,label=f"{c} (柱)",width=.8)
    s,r2,p,xf,yf=lr(x.astype(float),y,f"{c}")
    if len(xf): ax.plot(xf,yf,"-",color=COL[c],lw=2,alpha=.8)
    ax.annotate(f"{s:+.1f}mm/yr",(xf[-1],yf[-1]),textcoords="offset points",
                xytext=(5,0),fontsize=7,color=COL[c])
ax.set(xlabel="年份",ylabel="年降水量 (mm)",title=f"图2: 年降水变化趋势 ({PERIOD})")
ax.legend(); fig.tight_layout(); fig.savefig("fig2_年降水趋势.png",dpi=150); plt.close()
print("  ✅ fig2")

# ---- Fig3: 季节箱线 ----
fig,axes=plt.subplots(1,3,figsize=(14,5),sharey=True)
for i,c in enumerate(["兰州","西安","西宁"]):
    cd=df[df["城市"]==c].dropna(subset=["月均温"])
    bp=axes[i].boxplot([cd[cd["季节"]==s]["月均温"].dropna() for s in SEASONS],
                       labels=SEASONS,patch_artist=True,widths=.5)
    for p,s in zip(bp["boxes"],SEASONS): p.set_facecolor(SC[s]); p.set_alpha(.6)
    axes[i].set_title(c,color=COL[c],fontweight="bold")
    if i==0: axes[i].set_ylabel("月均温 (°C)")
fig.suptitle(f"图3: 季节气温分布 ({PERIOD})",fontweight="bold")
fig.tight_layout(); fig.savefig("fig3_季节气温箱线图.png",dpi=150); plt.close()
print("  ✅ fig3")

# ---- Fig4: 季节降水 ----
fig,ax=plt.subplots(figsize=(10,6))
sp=df.dropna(subset=["月降水量"]).groupby(["城市","季节"])["月降水量"].mean().unstack(0)
sp=sp.reindex(SEASONS); w=.2; x=np.arange(4)
for i,(c,co) in enumerate(COL.items()):
    b=ax.bar(x+(i-1)*w,sp[c],w,label=c,color=co,alpha=.8)
    for bar,v in zip(b,sp[c]): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,
                                        f"{v:.0f}",ha="center",fontsize=7)
ax.set(xticks=x,xticklabels=SEASONS,ylabel="月均降水量 (mm)",
       title=f"图4: 季节降水对比 ({PERIOD})")
ax.legend(); fig.tight_layout(); fig.savefig("fig4_季节降水对比.png",dpi=150); plt.close()
print("  ✅ fig4")

# ---- Fig5: 综合 ----
fig=plt.figure(figsize=(12,9))
# (a) 均值
ax=fig.add_subplot(2,2,1)
cm=annual.groupby("城市")[["年均温","年降水"]].mean()
ax2=ax.twinx(); xp=np.arange(3)
for i,(c,co) in enumerate(COL.items()):
    ax.bar(xp[i]-.15,cm.loc[c,"年均温"],.3,color=co,alpha=.8)
    ax2.bar(xp[i]+.15,cm.loc[c,"年降水"],.3,color="gray",alpha=.4)
    ax.text(xp[i]-.15,cm.loc[c,"年均温"]+.2,f"{cm.loc[c,'年均温']:.1f}°C",ha="center",fontsize=8)
    ax2.text(xp[i]+.15,cm.loc[c,"年降水"]+15,f"{cm.loc[c,'年降水']:.0f}mm",ha="center",fontsize=8)
ax.set(xticks=xp,xticklabels=list(COL.keys()),ylabel="年均温 (°C)")
ax2.set_ylabel("年降水 (mm)"); ax.set_title("(a) 均值",fontweight="bold")
# (b) M-K表
ax=fig.add_subplot(2,2,2); ax.axis("off")
mk_rows=[]
for c in ["兰州","西安","西宁"]:
    for vn,col in [("年均温","年均温"),("年降水","年降水")]:
        d=annual[(annual["城市"]==c)&(annual["年"]<2025)][col].dropna().values
        s,z,p=mk_test(d); trend="↑" if s>0 else "↓"
        sig="**" if p<.05 else "*" if p<.1 else ""
        mk_rows.append([c,vn,trend,f"{z:.3f}",f"{p:.4f}",sig])
from matplotlib.table import Table
tab=ax.table(cellText=mk_rows,colLabels=["城市","变量","趋势","Z","p","显著"],
             cellLoc="center",loc="center"); tab.auto_set_font_size(False); tab.set_fontsize(8)
tab.scale(1,1.4)
for i,r in enumerate(mk_rows):
    if r[-1]=="**":
        for j in range(6): tab[i+1,j].set_facecolor("#d4edda")
    elif r[-1]=="*":
        for j in range(6): tab[i+1,j].set_facecolor("#fff3cd")
ax.set_title("(b) M-K趋势检验",fontweight="bold")
# (c) 逐年气温
ax=fig.add_subplot(2,2,3)
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年均温"])
    ax.plot(d["年"],d["年均温"],"o-",color=COL[c],lw=1,ms=2,label=c)
ax.set(xlabel="年份",ylabel="年均温 (°C)",title="(c) 逐年年均温"); ax.legend(fontsize=7)
# (d) 逐年降水
ax=fig.add_subplot(2,2,4)
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年降水"])
    ax.plot(d["年"],d["年降水"],"o-",color=COL[c],lw=1,ms=2,label=c)
ax.set(xlabel="年份",ylabel="年降水 (mm)",title="(d) 逐年降水"); ax.legend(fontsize=7)
fig.suptitle(f"图5: 综合对比 ({PERIOD})",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig("fig5_综合对比.png",dpi=150); plt.close()
print("  ✅ fig5")

# ---- ExtA: MK突变 ----
fig,axes=plt.subplots(2,3,figsize=(16,10))
for i,c in enumerate(["兰州","西安","西宁"]):
    for row,var,label in [(0,"年均温","气温"),(1,"年降水","降水")]:
        ax=axes[row,i]
        d=annual[annual["城市"]==c][var].dropna().values
        yrs=annual[annual["城市"]==c]["年"].dropna().values[:len(d)].astype(int)
        if len(d)>=5:
            UF,UB,mut=mk_mut(d); x=np.arange(len(d))
            ax.plot(x,UF,'b-',lw=1,label='UF'); ax.plot(x,UB,'r--',lw=1,label='UB')
            ax.axhline(1.96,color='gray',ls=':',lw=.5); ax.axhline(-1.96,color='gray',ls=':',lw=.5)
            ax.axhline(0,color='k',lw=.3)
            for m in mut: ax.axvline(m,color='purple',ls=':',lw=.8)
            ax.set_xticks(x[::5]); ax.set_xticklabels(yrs[::5],rotation=45,fontsize=6)
        ax.set_title(f"{c} {label}",color=COL[c],fontweight="bold",fontsize=10)
        ax.legend(fontsize=6)
fig.suptitle("拓展图A: MK突变检验",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig("ext_figA_MK突变检验.png",dpi=150); plt.close()
print("  ✅ extA")

# ---- ExtB: 小波 ----
fig,axes=plt.subplots(2,3,figsize=(16,10))
for i,c in enumerate(["兰州","西安","西宁"]):
    for row,var,label in [(0,"年均温","气温"),(1,"年降水","降水")]:
        ax=axes[row,i]
        d=annual[annual["城市"]==c][var].dropna().values
        yrs=annual[annual["城市"]==c]["年"].dropna().values[:len(d)].astype(int)
        if len(d)>=10:
            sc_max=min(len(d)//2,40)
            scales,pwr=morlet_cwt(d,scales=np.arange(2,sc_max))
            levels=np.linspace(0,np.max(pwr)*.9,20)
            cf=ax.contourf(yrs,2**scales,pwr,levels=levels,cmap='jet',extend='both')
            plt.colorbar(cf,ax=ax,label='Power',shrink=.8)
            ax.set_yscale('log',base=2); ax.set_ylabel("周期(年)",fontsize=8)
        ax.set_title(f"{c} {label}",color=COL[c],fontweight="bold",fontsize=10)
        ax.set_xlabel("年份",fontsize=7)
fig.suptitle("拓展图B: Morlet小波功率谱",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig("ext_figB_小波分析.png",dpi=150); plt.close()
print("  ✅ extB")

# ---- ExtC: 极端指数 ----
from collections import defaultdict
ext=defaultdict(list)
for c in ["兰州","西安","西宁"]:
    cd=df[df["城市"]==c].copy()
    t90,t10=cd["月均温"].quantile(.9),cd["月均温"].quantile(.1)
    p95=cd["月降水量"].quantile(.95)
    for yr in sorted(cd["年"].unique()):
        yd=cd[cd["年"]==yr]
        ext["城市"].append(c); ext["年"].append(yr)
        ext["暖月"].append((yd["月均温"]>t90).sum())
        ext["冷月"].append((yd["月均温"]<t10).sum())
        ext["湿月"].append((yd["月降水量"]>p95).sum())
        ext["旱月"].append((yd["月降水量"]<5).sum())
        ext["最大月降水"].append(yd["月降水量"].max())
edf=pd.DataFrame(ext)

fig,axes=plt.subplots(2,3,figsize=(16,10))
titles=[("暖月","异常暖月数 (>90%分位)"),("冷月","异常冷月数 (<10%分位)"),
        ("湿月","异常湿月数 (>95%分位)"),("旱月","干旱月数 (<5mm)"),
        ("最大月降水","年最大月降水 (mm)"),]
for i,(col,title) in enumerate(titles):
    ax=axes[i//3,i%3]
    for c in ["兰州","西安","西宁"]:
        cd=edf[edf["城市"]==c]
        ax.plot(cd["年"],cd[col],"o-",color=COL[c],lw=1,ms=2,label=c,alpha=.8)
        x=cd["年"].values.astype(float);y=cd[col].values
        ax.plot(x,np.polyval(np.polyfit(x,y,1),x),"--",color=COL[c],lw=1,alpha=.4)
    ax.set_title(title,fontsize=9,fontweight="bold"); ax.legend(fontsize=6)
axes[1,2].axis("off")  # empty slot
fig.suptitle("拓展图C: 极端气候指数",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig("ext_figC_极端气候指数.png",dpi=150); plt.close()
print("  ✅ extC")

# ===== 统计汇总 =====
print("\n"+"="*60+"\n统计汇总\n"+"="*60)
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年均温"])
    x,y=d["年"].values.astype(float),d["年均温"].values
    s,r2,p,_,_=lr(x,y,f"{c}年均温({PERIOD})")
    d2=annual[annual["城市"]==c].dropna(subset=["年降水"])
    x2,y2=d2["年"].values.astype(float),d2["年降水"].values
    s2,r22,p2,_,_=lr(x2,y2,f"{c}年降水({PERIOD})")
    # MK
    _,z_t,p_t=mk_test(y)
    _,z_p,p_p=mk_test(y2)
    print(f"\n{c}: 均温{np.mean(y):.1f}°C, 降水{np.mean(y2):.0f}mm")
    print(f"  气温趋势: {s:+.3f}°C/yr R²={r2:.3f} p={p:.3f} | MK Z={z_t:.2f} p={p_t:.3f}")
    print(f"  降水趋势: {s2:+.1f}mm/yr R²={r22:.3f} p={p2:.3f} | MK Z={z_p:.2f} p={p_p:.3f}")

print("\n✅ 8图+分析完成")
