#!/usr/bin/env python3
"""
v3: +置信区间 + Theil-Sen + 小波显著性(红噪声/COI/全局谱)
统一 Open-Meteo ERA5 | 1960-2025
"""

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

# ═══════════════════════════════
# 改进的回归函数
# ═══════════════════════════════
def theil_sen(x, y):
    """Theil-Sen 斜率估计 (稳健,不受自相关偏差影响)"""
    n = len(x); slopes = []
    for i in range(n):
        for j in range(i+1, n):
            if x[j] != x[i]:
                slopes.append((y[j]-y[i])/(x[j]-x[i]))
    return np.median(slopes)

def bootstrap_ci(x, y, n_boot=2000, alpha=0.05):
    """Bootstrap 95% 置信区间 for Theil-Sen slope"""
    n = len(x); slopes = np.zeros(n_boot)
    rng = np.random.default_rng(42)
    for b in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        slopes[b] = theil_sen(x[idx], y[idx])
    return np.percentile(slopes, [100*alpha/2, 100*(1-alpha/2)])

def analyze_trend(x, y, label=""):
    """完整趋势分析：OLS + Theil-Sen + Bootstrap CI"""
    m = ~(np.isnan(x)|np.isnan(y)); xc,yc = x[m],y[m]
    if len(xc) < 10: return {}
    
    # OLS
    s_ols, i_ols, r, p_ols, _ = stats.linregress(xc, yc)
    r2 = r**2
    
    # Theil-Sen
    s_ts = theil_sen(xc, yc)
    ci_lo, ci_hi = bootstrap_ci(xc, yc)
    
    if label:
        print(f"  {label}: OLS={s_ols:+.4f}/yr R²={r2:.3f} p={p_ols:.4f}  "
              f"TS={s_ts:+.4f} 95%CI=[{ci_lo:+.4f}, {ci_hi:+.4f}]")
    
    return {"ols_slope": s_ols, "ols_intercept": i_ols, "ols_r2": r2, "ols_p": p_ols,
            "ts_slope": s_ts, "ts_ci_lo": ci_lo, "ts_ci_hi": ci_hi,
            "x": xc, "y": yc}

# ═══════════════════════════════
# 小波显著性检验 + COI + 全局谱
# ═══════════════════════════════
def wavelet_significance(data, scales, dt=1.0, alpha=0.05, n_sim=300):
    """Morlet CWT + 红噪声显著性检验 + COI"""
    n = len(data)
    # 去趋势 + 标准化
    data_detrend = data - np.polyval(np.polyfit(np.arange(n), data, 1), np.arange(n))
    dn = data_detrend / np.std(data_detrend)
    
    # CWT
    fft = np.fft.fft(dn); freqs = np.fft.fftfreq(n, d=dt)
    cwt = np.zeros((len(scales), n), dtype=complex)
    for i, s in enumerate(scales):
        xi = s * 2 * np.pi * np.abs(freqs)
        mf = np.pi**(-.25) * np.exp(-.5 * (xi - 6)**2); mf[freqs <= 0] = 0
        cwt[i] = np.fft.ifft(fft * mf * np.sqrt(s))
    power = np.abs(cwt)**2
    
    # 红噪声背景 (AR1)
    ar1 = np.corrcoef(dn[:-1], dn[1:])[0,1] if len(dn)>1 else 0
    # 模拟 n_sim 个红噪声序列的功率谱分位数
    rng = np.random.default_rng(42)
    sim_power = np.zeros((n_sim, len(scales)))
    for sim in range(n_sim):
        rn = np.zeros(n+100); rn[0] = rng.normal()
        for t in range(1, n+100):
            rn[t] = ar1 * rn[t-1] + rng.normal() * np.sqrt(1-ar1**2)
        rn = rn[100:] / np.std(rn)
        fft_rn = np.fft.fft(rn)
        for i, s in enumerate(scales):
            xi = s * 2 * np.pi * np.abs(freqs)
            mf = np.pi**(-.25) * np.exp(-.5 * (xi - 6)**2); mf[freqs <= 0] = 0
            sim_power[sim, i] = np.mean(np.abs(np.fft.ifft(fft_rn * mf * np.sqrt(s)))**2)
    
    # 95% 显著性水平（各尺度）
    sig_level = np.percentile(sim_power, 100*(1-alpha), axis=0)
    
    # 功率比 (power / sig_level) — >1 表示显著
    power_ratio = power / sig_level[:, np.newaxis]
    
    # COI (cone of influence) — for each time point, max reliable scale
    coi_val = scales / np.sqrt(2)  # per scale
    # At each time t, scales where s*sqrt(2) < min(t, n-t) are reliable
    time_axis = np.arange(n)
    coi_boundary = np.array([np.min(coi_val[coi_val < min(t, n-1-t)]) if any(coi_val < min(t, n-1-t)) else coi_val[-1] for t in time_axis])
    
    # 全局小波谱
    global_ws = np.mean(power, axis=1)
    global_sig = sim_power.mean(axis=0)
    
    return {"power": power, "power_ratio": power_ratio, "sig_level": sig_level,
            "coi_boundary": coi_boundary, "scales": scales, "n": n,
            "global_ws": global_ws, "global_sig": global_sig, "ar1": ar1}


print("="*60+"\nv3: Theil-Sen + CI + 小波显著性\n"+"="*60)

# ===== Fig1: 年均温 (Theil-Sen) =====
print("\n[年均温趋势]")
fig,ax=plt.subplots(figsize=(12,6))
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年均温"])
    x,y=d["年"].values.astype(float),d["年均温"].values
    ax.plot(x,y,"o-",color=COL[c],lw=1.5,ms=3,label=c,zorder=3)
    res=analyze_trend(x,y,f"{c}年均温")
    if res:
        # Theil-Sen 趋势线
        ts_line = res["ts_slope"]*res["x"] + np.mean(y) - res["ts_slope"]*np.mean(res["x"])
        ax.plot(res["x"], ts_line, "--", color=COL[c], lw=1.5, alpha=.7)
        sig="**" if res["ols_p"]<.05 else "*" if res["ols_p"]<.1 else ""
        ci_str = f"[{res['ts_ci_lo']:+.3f}, {res['ts_ci_hi']:+.3f}]"
        ax.annotate(f"TS={res['ts_slope']:+.3f}/yr\n95%CI {ci_str}\nR²={res['ols_r2']:.3f}{sig}",
                    (res["x"][-1],res["y"][-1]),
                    textcoords="offset points",xytext=(5,-15),fontsize=7,color=COL[c])
ax.set(xlabel="年份",ylabel="年均温 (°C)",title="图1: 年均温变化趋势 (1960–2025, Theil-Sen slope + 95% CI)")
ax.legend(); fig.tight_layout(); fig.savefig("fig1_年均温趋势.png",dpi=150); plt.close()
print("  ✅ fig1")

# ===== Fig2: 年降水 =====
print("\n[年降水趋势]")
fig,ax=plt.subplots(figsize=(12,6))
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年降水"])
    x,y=d["年"].values.astype(float),d["年降水"].values
    ax.bar(x,y,color=COL[c],alpha=.25,label=f"{c}",width=.8)
    res=analyze_trend(x,y,f"{c}年降水")
    if res:
        ts_line = res["ts_slope"]*res["x"] + np.mean(y) - res["ts_slope"]*np.mean(res["x"])
        ax.plot(res["x"], ts_line, "-", color=COL[c], lw=2, alpha=.8)
        ax.annotate(f"TS={res['ts_slope']:+.1f}mm/yr\n95%CI [{res['ts_ci_lo']:+.1f},{res['ts_ci_hi']:+.1f}]",
                    (res["x"][-1],res["y"][-1]),textcoords="offset points",
                    xytext=(5,0),fontsize=7,color=COL[c])
ax.set(xlabel="年份",ylabel="年降水量 (mm)",title="图2: 年降水变化趋势 (1960–2025, Theil-Sen slope + 95% CI)")
ax.legend(); fig.tight_layout(); fig.savefig("fig2_年降水趋势.png",dpi=150); plt.close()
print("  ✅ fig2")

# ===== Fig3: 季节箱线 (不变) =====
fig,axes=plt.subplots(1,3,figsize=(14,5),sharey=True)
for i,c in enumerate(["兰州","西安","西宁"]):
    cd=df[df["城市"]==c].dropna(subset=["月均温"])
    bp=axes[i].boxplot([cd[cd["季节"]==s]["月均温"].dropna() for s in SEASONS],
                       labels=SEASONS,patch_artist=True,widths=.5)
    for p,s in zip(bp["boxes"],SEASONS): p.set_facecolor(SC[s]); p.set_alpha(.6)
    axes[i].set_title(c,color=COL[c],fontweight="bold")
    if i==0: axes[i].set_ylabel("月均温 (°C)")
fig.suptitle("图3: 季节气温分布 (1960–2025)",fontweight="bold")
fig.tight_layout(); fig.savefig("fig3_季节气温箱线图.png",dpi=150); plt.close()
print("  ✅ fig3")

# ===== Fig4: 季节降水 =====
fig,ax=plt.subplots(figsize=(10,6))
sp=df.dropna(subset=["月降水量"]).groupby(["城市","季节"])["月降水量"].mean().unstack(0)
sp=sp.reindex(SEASONS); w=.2; x=np.arange(4)
for i,(c,co) in enumerate(COL.items()):
    b=ax.bar(x+(i-1)*w,sp[c],w,label=c,color=co,alpha=.8)
    for bar,v in zip(b,sp[c]): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,
                                        f"{v:.0f}",ha="center",fontsize=7)
ax.set(xticks=x,xticklabels=SEASONS,ylabel="月均降水量 (mm)",title="图4: 季节降水对比 (1960–2025)")
ax.legend(); fig.tight_layout(); fig.savefig("fig4_季节降水对比.png",dpi=150); plt.close()
print("  ✅ fig4")

# ===== Fig5: 综合 (不变) =====
fig=plt.figure(figsize=(12,9))
ax=fig.add_subplot(2,2,1)
cm=annual.groupby("城市")[["年均温","年降水"]].mean()
ax2=ax.twinx(); xp=np.arange(3)
for i,(c,co) in enumerate(COL.items()):
    ax.bar(xp[i]-.15,cm.loc[c,"年均温"],.3,color=co,alpha=.8)
    ax2.bar(xp[i]+.15,cm.loc[c,"年降水"],.3,color="gray",alpha=.4)
    ax.text(xp[i]-.15,cm.loc[c,"年均温"]+.2,f"{cm.loc[c,'年均温']:.1f}°C",ha="center",fontsize=8)
    ax2.text(xp[i]+.15,cm.loc[c,"年降水"]+15,f"{cm.loc[c,'年降水']:.0f}mm",ha="center",fontsize=8)
ax.set(xticks=xp,xticklabels=list(COL.keys()),ylabel="年均温 (°C)")
ax2.set_ylabel("年降水 (mm)"); ax.set_title("(a) 均值 (1960–2025)",fontweight="bold")

ax=fig.add_subplot(2,2,2); ax.axis("off")
mk_rows=[]
for c in ["兰州","西安","西宁"]:
    for vn,col in [("年均温","年均温"),("年降水","年降水")]:
        d=annual[(annual["城市"]==c)][col].dropna().values
        n=len(d); s=sum(np.sign(d[j]-d[i]) for i in range(n-1) for j in range(i+1,n))
        v=n*(n-1)*(2*n+5)/18
        z=(s-1)/np.sqrt(v) if s>0 else (s+1)/np.sqrt(v) if s<0 else 0
        p=2*(1-stats.norm.cdf(abs(z))); trend="↑" if s>0 else "↓"
        sig="**" if p<.05 else "*" if p<.1 else ""
        mk_rows.append([c,vn,trend,f"{z:.2f}",f"{p:.4f}",sig])
tab=ax.table(cellText=mk_rows,colLabels=["城市","变量","趋势","Z","p","显著"],
             cellLoc="center",loc="center"); tab.auto_set_font_size(False); tab.set_fontsize(8)
tab.scale(1,1.4)
for i,r in enumerate(mk_rows):
    if r[-1]=="**":
        for j in range(6): tab[i+1,j].set_facecolor("#d4edda")
ax.set_title("(b) M-K趋势检验",fontweight="bold")

ax=fig.add_subplot(2,2,3)
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年均温"])
    ax.plot(d["年"],d["年均温"],"o-",color=COL[c],lw=1,ms=2,label=c)
ax.set(xlabel="年份",ylabel="年均温 (°C)",title="(c) 逐年年均温"); ax.legend(fontsize=7)

ax=fig.add_subplot(2,2,4)
for c in ["兰州","西安","西宁"]:
    d=annual[annual["城市"]==c].dropna(subset=["年降水"])
    ax.plot(d["年"],d["年降水"],"o-",color=COL[c],lw=1,ms=2,label=c)
ax.set(xlabel="年份",ylabel="年降水 (mm)",title="(d) 逐年降水"); ax.legend(fontsize=7)
fig.suptitle("图5: 综合对比 (1960–2025)",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig("fig5_综合对比.png",dpi=150); plt.close()
print("  ✅ fig5")

# ===== ExtA: MK突变 (不变) =====
print("\n[ExtA: MK突变]")
fig,axes=plt.subplots(2,3,figsize=(16,10))
for i,c in enumerate(["兰州","西安","西宁"]):
    for row,var,label in [(0,"年均温","气温"),(1,"年降水","降水")]:
        ax=axes[row,i]
        d=annual[annual["城市"]==c][var].dropna().values
        yrs=annual[annual["城市"]==c]["年"].dropna().values[:len(d)].astype(int)
        if len(d)>=5:
            n=len(d); UF=np.zeros(n)
            for k in range(1,n):
                ss=sum(np.sign(d[k]-d[j]) for j in range(k))
                UF[k]=(ss-np.sign(ss))/np.sqrt(k*(k-1)*(2*k+5)/18)
            dr=d[::-1]; UB_r=np.zeros(n)
            for k in range(1,n):
                ss=sum(np.sign(dr[k]-dr[j]) for j in range(k))
                UB_r[k]=(ss-np.sign(ss))/np.sqrt(k*(k-1)*(2*k+5)/18)
            UB=-UB_r[::-1]
            x=np.arange(n)
            ax.plot(x,UF,'b-',lw=1,label='UF'); ax.plot(x,UB,'r--',lw=1,label='UB')
            ax.axhline(1.96,color='gray',ls=':',lw=.5); ax.axhline(-1.96,color='gray',ls=':',lw=.5)
            ax.axhline(0,color='k',lw=.3)
            ax.set_xticks(x[::10]); ax.set_xticklabels(yrs[::10],rotation=45,fontsize=6)
        ax.set_title(f"{c} {label}",color=COL[c],fontweight="bold",fontsize=10); ax.legend(fontsize=6)
fig.suptitle("拓展图A: MK突变检验",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig("ext_figA_MK突变检验.png",dpi=150); plt.close()
print("  ✅ extA")

# ===== ExtB: 小波+显著性+COI+全局谱 =====
print("\n[ExtB: 小波显著性检验]")
fig=plt.figure(figsize=(18,14))
plot_idx = 0
for ci, c in enumerate(["兰州","西安","西宁"]):
    for vi, (var,label) in enumerate([("年均温","气温"),("年降水","降水")]):
        d = annual[annual["城市"]==c][var].dropna().values
        yrs = annual[annual["城市"]==c]["年"].dropna().values[:len(d)].astype(int)
        if len(d) < 20: continue
        
        sc_max = min(len(d)//2, 50)
        scales = np.arange(2, sc_max)
        ws = wavelet_significance(d, scales)
        
        # 主功率图
        ax = fig.add_subplot(3, 4, plot_idx*2 + 1)
        levels = np.linspace(0, np.max(ws["power"])*.9, 20)
        cf = ax.contourf(yrs, 2**scales, ws["power"], levels=levels, cmap='jet', extend='both')
        
        # 显著性轮廓 (95%)
        ax.contour(yrs, 2**scales, ws["power_ratio"], levels=[1.0],
                   colors='black', linewidths=1.5, linestyles='-')
        
        # COI
        coi_yrs = yrs[0] + np.arange(len(yrs))
        ax.fill_between(coi_yrs, 2**ws["coi_boundary"], 2**scales[-1],
                        color='white', alpha=0.3, hatch='///', edgecolor='gray', linewidth=0)
        ax.plot(coi_yrs, 2**np.minimum(ws["coi_boundary"], scales[-1]), 'k--', lw=1)
        
        ax.set_yscale('log', base=2)
        ax.set_ylabel("周期 (年)", fontsize=8)
        ax.set_title(f"{c} {label}", color=COL[c], fontweight="bold", fontsize=10)
        plt.colorbar(cf, ax=ax, label='Power', shrink=.8)
        
        # 全局小波谱
        ax2 = fig.add_subplot(3, 4, plot_idx*2 + 2)
        ax2.plot(ws["global_ws"], 2**scales, 'b-', lw=1.5, label='观测')
        ax2.plot(ws["global_sig"], 2**scales, 'r--', lw=1, label='95%红噪声')
        ax2.set_yscale('log', base=2)
        ax2.set_xlabel("平均功率", fontsize=7)
        ax2.set_title(f"全局谱 (AR1={ws['ar1']:.2f})", fontsize=8)
        ax2.legend(fontsize=6)
        ax2.fill_betweenx(2**scales, 0, ws["global_sig"], color='red', alpha=0.05)
        
        plot_idx += 1

fig.suptitle("拓展图B: Morlet小波功率谱 + 95%显著性 + COI + 全局谱", fontweight="bold", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig("ext_figB_小波分析.png", dpi=150); plt.close()
print("  ✅ extB (with significance + COI)")

# ===== ExtC: 极端指数 =====
print("\n[ExtC: 极端指数]")
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
titles=[("暖月","异常暖月数"),("冷月","异常冷月数"),("湿月","异常湿月数"),
        ("旱月","干旱月数 (<5mm)"),("最大月降水","年最大月降水 (mm)")]
for i,(col,title) in enumerate(titles):
    ax=axes[i//3,i%3]
    for c in ["兰州","西安","西宁"]:
        cd=edf[edf["城市"]==c]
        ax.plot(cd["年"],cd[col],"o-",color=COL[c],lw=1,ms=2,label=c,alpha=.8)
        x=cd["年"].values.astype(float);y=cd[col].values
        # Theil-Sen trend
        ts = theil_sen(x, y)
        ax.plot(x, ts*x + np.mean(y) - ts*np.mean(x), "--", color=COL[c], lw=1, alpha=.4)
    ax.set_title(title,fontsize=9,fontweight="bold"); ax.legend(fontsize=6)
axes[1,2].axis("off")
fig.suptitle("拓展图C: 极端气候指数 (月值分位数定义, 非标准ETCCDI)",fontweight="bold")
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig("ext_figC_极端气候指数.png",dpi=150); plt.close()
print("  ✅ extC")

# ===== 统计汇总 =====
print("\n"+"="*60+"\n最终统计汇总 (Theil-Sen)\n"+"="*60)
for c in ["兰州","西安","西宁"]:
    for var in ["年均温","年降水"]:
        d=annual[annual["城市"]==c].dropna(subset=[var])
        x,y=d["年"].values.astype(float),d[var].values
        res=analyze_trend(x,y,f"{c} {var}")
        if not res: continue
        unit="°C/yr" if var=="年均温" else "mm/yr"
        print(f"\n{c} {var}: {np.mean(y):.1f}{unit[-4:-2]}")

print("\n✅ 8图完成 (v3: TS+CI+小波显著性)")
