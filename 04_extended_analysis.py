#!/usr/bin/env python3
"""
拓展分析：MK突变检验 + 小波分析 + 极端气候指数
生成拓展图表并输出分析结果
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats, signal
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "SimHei",
    "axes.unicode_minus": False,
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False,
})

COLORS = {"兰州": "#e74c3c", "西安": "#3498db", "西宁": "#2ecc71"}
CITIES = ["兰州", "西安", "西宁"]

# ───── 加载数据 ─────
df = pd.read_csv("tidy_climate_data.csv")
annual = pd.read_csv("annual_summary.csv")
print("=" * 60)
print("拓展分析：MK突变检验 + 小波分析 + 极端气候指数")
print("=" * 60)

# ═══════════════════════════════════════════
# 1. MK 突变检验 (Mann-Kendall Mutation Test)
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("【1】MK 突变检验")
print("=" * 60)

def mk_mutation_test(data):
    """MK突变检验：计算UF和UB统计量，返回UF, UB, 突变点"""
    n = len(data)
    # 顺序统计量 UF
    s = np.zeros(n)
    for k in range(1, n):
        for j in range(k):
            s[k] += np.sign(data[k] - data[j])
    var = np.array([k * (k - 1) * (2 * k + 5) / 18 for k in range(1, n + 1)])
    UF = np.zeros(n)
    UF[1:] = (s[1:] - np.sign(s[1:])) / np.sqrt(var[1:])

    # 逆序统计量 UB
    data_rev = data[::-1]
    s_rev = np.zeros(n)
    for k in range(1, n):
        for j in range(k):
            s_rev[k] += np.sign(data_rev[k] - data_rev[j])
    UB_rev = np.zeros(n)
    UB_rev[1:] = (s_rev[1:] - np.sign(s_rev[1:])) / np.sqrt(var[1:])
    UB = -UB_rev[::-1]

    # 突变点：UF和UB的交点（在±1.96置信区间内）
    mutation_years = []
    for i in range(1, n - 1):
        if (UF[i] - UB[i]) * (UF[i + 1] - UB[i + 1]) < 0:
            if abs(UF[i]) < 1.96:
                mutation_years.append(i)

    return UF, UB, mutation_years


fig, axes = plt.subplots(2, 3, figsize=(16, 10))
significance_level = 1.96

for idx, city in enumerate(CITIES):
    # ── 气温 ──
    ax_t = axes[0, idx]
    temp_data = annual[annual["城市"] == city]["年均温"].dropna().values
    years_temp = annual[annual["城市"] == city]["年"].dropna().values[:len(temp_data)]
    years_temp = years_temp.astype(int)

    if len(temp_data) >= 5:
        UF_t, UB_t, mut_t = mk_mutation_test(temp_data)
        x = np.arange(len(temp_data))
        ax_t.plot(x, UF_t, 'b-', linewidth=1.5, label='UF')
        ax_t.plot(x, UB_t, 'r--', linewidth=1.5, label='UB')
        ax_t.axhline(significance_level, color='gray', linestyle=':', linewidth=0.8)
        ax_t.axhline(-significance_level, color='gray', linestyle=':', linewidth=0.8)
        ax_t.axhline(0, color='black', linewidth=0.5)
        ax_t.fill_between(x, -significance_level, significance_level, alpha=0.05, color='gray')

        for m in mut_t:
            ax_t.axvline(m, color='purple', linestyle=':', linewidth=1, alpha=0.6)
            ax_t.annotate(str(years_temp[m]), (m, significance_level),
                         fontsize=7, color='purple', ha='center')

        ax_t.set_xticks(x)
        ax_t.set_xticklabels(years_temp, rotation=45, fontsize=7)
    ax_t.set_title(f"{city} 年均温", fontsize=11, color=COLORS[city], fontweight='bold')
    ax_t.legend(fontsize=7)
    ax_t.set_ylabel("UF/UB", fontsize=9)

    # ── 降水 ──
    ax_p = axes[1, idx]
    prec_data = annual[annual["城市"] == city]["年降水"].dropna().values
    years_prec = annual[annual["城市"] == city]["年"].dropna().values[:len(prec_data)]
    years_prec = years_prec.astype(int)

    if len(prec_data) >= 5:
        UF_p, UB_p, mut_p = mk_mutation_test(prec_data)
        x = np.arange(len(prec_data))
        ax_p.plot(x, UF_p, 'b-', linewidth=1.5, label='UF')
        ax_p.plot(x, UB_p, 'r--', linewidth=1.5, label='UB')
        ax_p.axhline(significance_level, color='gray', linestyle=':', linewidth=0.8)
        ax_p.axhline(-significance_level, color='gray', linestyle=':', linewidth=0.8)
        ax_p.axhline(0, color='black', linewidth=0.5)
        ax_p.fill_between(x, -significance_level, significance_level, alpha=0.05, color='gray')

        for m in mut_p:
            ax_p.axvline(m, color='purple', linestyle=':', linewidth=1, alpha=0.6)
            ax_p.annotate(str(years_prec[m]), (m, significance_level),
                         fontsize=7, color='purple', ha='center')

        ax_p.set_xticks(x)
        ax_p.set_xticklabels(years_prec, rotation=45, fontsize=7)
    ax_p.set_title(f"{city} 年降水", fontsize=11, color=COLORS[city], fontweight='bold')
    ax_p.legend(fontsize=7)
    ax_p.set_ylabel("UF/UB", fontsize=9)

    # 输出突变点
    t_mut_str = ', '.join([str(years_temp[m]) for m in mut_t]) if mut_t else '无'
    p_mut_str = ', '.join([str(years_prec[m]) for m in mut_p]) if mut_p else '无'
    print(f"  {city}: 气温突变年={t_mut_str} | 降水突变年={p_mut_str}")

fig.suptitle("拓展图A: Mann-Kendall 突变检验 (UF/UB曲线)", fontsize=14, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("ext_figA_MK突变检验.png", dpi=150)
plt.close(fig)
print("  ✅ 已保存: ext_figA_MK突变检验.png")


# ═══════════════════════════════════════════
# 2. 小波分析 (Morlet Continuous Wavelet Transform)
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("【2】小波分析（Morlet CWT）")
print("=" * 60)

def morlet_cwt(data, dt=1.0, scales=None):
    """Morlet 连续小波变换"""
    n = len(data)
    if scales is None:
        scales = np.arange(2, min(n // 2, 7))
    
    data_norm = (data - np.mean(data)) / np.std(data)
    n_scales = len(scales)
    cwt_matrix = np.zeros((n_scales, n), dtype=complex)
    
    # 频域计算
    fft_data = np.fft.fft(data_norm)
    freqs = np.fft.fftfreq(n, d=dt)
    
    for i, scale in enumerate(scales):
        # Morlet wavelet in frequency domain
        omega0 = 6.0  # central frequency
        s = scale * 1.0
        # Morlet: psi_hat(s*w) = pi^(-1/4) * H(w) * exp(-(s*w - omega0)^2 / 2)
        xi = s * 2 * np.pi * np.abs(freqs)
        morlet_fft = np.pi ** (-0.25) * np.exp(-0.5 * (xi - omega0) ** 2)
        morlet_fft[freqs <= 0] = 0  # Heaviside
        cwt_matrix[i] = np.fft.ifft(fft_data * morlet_fft * np.sqrt(s))
    
    power = np.abs(cwt_matrix) ** 2
    return scales, power, cwt_matrix

fig_wave, axes_wave = plt.subplots(2, 3, figsize=(16, 10))

for idx, city in enumerate(CITIES):
    # ── 气温 ──
    ax_t = axes_wave[0, idx]
    temp_data = annual[annual["城市"] == city]["年均温"].dropna().values
    years = annual[annual["城市"] == city]["年"].dropna().values[:len(temp_data)].astype(int)
    
    if len(temp_data) >= 6:
        scales, power, _ = morlet_cwt(temp_data, scales=np.arange(2, min(len(temp_data)//2, 6)))
        levels = np.linspace(0, np.max(power) * 0.9, 20)
        cf = ax_t.contourf(years, 2**scales, power, levels=levels, cmap='jet', extend='both')
        plt.colorbar(cf, ax=ax_t, label='Power', shrink=0.8)
        ax_t.set_yscale('log', base=2)
        ax_t.set_ylabel("周期 (年)", fontsize=9)
    ax_t.set_title(f"{city} 年均温", fontsize=11, color=COLORS[city], fontweight='bold')
    ax_t.set_xlabel("年份", fontsize=8)

    # ── 降水 ──
    ax_p = axes_wave[1, idx]
    prec_data = annual[annual["城市"] == city]["年降水"].dropna().values
    
    if len(prec_data) >= 6:
        scales, power, _ = morlet_cwt(prec_data, scales=np.arange(2, min(len(prec_data)//2, 6)))
        levels = np.linspace(0, np.max(power) * 0.9, 20)
        cf = ax_p.contourf(years, 2**scales, power, levels=levels, cmap='jet', extend='both')
        plt.colorbar(cf, ax=ax_p, label='Power', shrink=0.8)
        ax_p.set_yscale('log', base=2)
        ax_p.set_ylabel("周期 (年)", fontsize=9)
    ax_p.set_title(f"{city} 年降水", fontsize=11, color=COLORS[city], fontweight='bold')
    ax_p.set_xlabel("年份", fontsize=8)

    # 输出显著周期
    mean_power = np.mean(power, axis=1)
    dominant = scales[np.argmax(mean_power)]
    print(f"  {city}: 气温主周期≈{2**dominant:.0f}年 | 降水主周期≈{2**scales[np.argmax(np.mean(power, axis=1))]:.0f}年")

fig_wave.suptitle("拓展图B: Morlet 小波功率谱 (检测周期信号)", fontsize=14, fontweight='bold')
fig_wave.tight_layout(rect=[0, 0, 1, 0.96])
fig_wave.savefig("ext_figB_小波分析.png", dpi=150)
plt.close(fig_wave)
print("  ✅ 已保存: ext_figB_小波分析.png")


# ═══════════════════════════════════════════
# 3. 极端气候指数
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("【3】极端气候指数")
print("=" * 60)

# 基于月值数据，定义极端指数
extreme_results = []

for city in CITIES:
    city_data = df[df["城市"] == city].copy()
    
    # 计算阈值（基于整个时段）
    temp_90 = city_data["月均温"].quantile(0.90)
    temp_10 = city_data["月均温"].quantile(0.10)
    prec_95 = city_data["月降水量"].quantile(0.95)
    prec_dry = 5.0  # 干旱月阈值 (mm)
    
    # 年度极端指数
    for year in sorted(city_data["年"].unique()):
        ydata = city_data[city_data["年"] == year]
        
        warm_months = (ydata["月均温"] > temp_90).sum()      # 异常暖月
        cold_months = (ydata["月均温"] < temp_10).sum()      # 异常冷月
        wet_months = (ydata["月降水量"] > prec_95).sum()     # 异常湿月
        dry_months = (ydata["月降水量"] < prec_dry).sum()    # 干旱月
        max_month_temp = ydata["月均温"].max()               # 年最高月均温
        max_month_prec = ydata["月降水量"].max()             # 年最大月降水
        summer_prec = ydata[ydata["月"].isin([6,7,8])]["月降水量"].sum()  # 夏季降水
        
        extreme_results.append({
            "城市": city, "年": year,
            "异常暖月数": warm_months, "异常冷月数": cold_months,
            "异常湿月数": wet_months, "干旱月数(降水<5mm)": dry_months,
            "年最高月均温": max_month_temp, "年最大月降水": max_month_prec,
            "夏季总降水": summer_prec
        })

ext_df = pd.DataFrame(extreme_results)

# 极端指数趋势
print("\n【极端指数趋势（线性回归）】")
for city in CITIES:
    city_ext = ext_df[ext_df["城市"] == city]
    print(f"\n  {city}:")
    for col in ["异常暖月数", "异常冷月数", "异常湿月数", "干旱月数(降水<5mm)", "年最大月降水"]:
        x = city_ext["年"].values.astype(float)
        y = city_ext[col].values
        mask = ~np.isnan(y)
        if sum(mask) >= 5:
            slope, _, r, p, _ = stats.linregress(x[mask], y[mask])
            sign = "+" if slope >= 0 else ""
            sig = "**" if p < 0.05 else "*" if p < 0.1 else ""
            print(f"    {col}: {sign}{slope:.3f}/yr R²={r**2:.3f} {sig}")

# 极端指数可视化
fig_ext, axes_ext = plt.subplots(2, 3, figsize=(16, 10))

titles = [
    ("异常暖月数", "异常暖月数 (>90%分位)"),
    ("异常冷月数", "异常冷月数 (<10%分位)"),
    ("异常湿月数", "异常湿月数 (>95%分位)"),
    ("干旱月数(降水<5mm)", "干旱月数 (降水<5mm)"),
    ("年最大月降水", "年最大月降水量 (mm)"),
    ("夏季总降水", "夏季总降水 (6-8月, mm)"),
]

for i, (col, title) in enumerate(titles):
    ax = axes_ext[i // 3, i % 3]
    for city in CITIES:
        city_ext = ext_df[ext_df["城市"] == city]
        ax.plot(city_ext["年"], city_ext[col], 'o-', color=COLORS[city],
                linewidth=1.5, markersize=4, label=city, alpha=0.8)
        # 趋势线
        x = city_ext["年"].values.astype(float)
        y = city_ext[col].values
        slope, intercept, _, _, _ = stats.linregress(x, y)
        ax.plot(x, slope * x + intercept, '--', color=COLORS[city], linewidth=1, alpha=0.4)
    ax.set_title(title, fontsize=9, fontweight='bold')
    ax.legend(fontsize=7, loc='best')
    ax.set_xlabel("年份", fontsize=7)

fig_ext.suptitle("拓展图C: 极端气候指数年际变化 (2015–2025)", fontsize=14, fontweight='bold')
fig_ext.tight_layout(rect=[0, 0, 1, 0.96])
fig_ext.savefig("ext_figC_极端气候指数.png", dpi=150)
plt.close(fig_ext)
print("\n  ✅ 已保存: ext_figC_极端气候指数.png")


# ═══════════════════════════════════════════
# 汇总
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("✅ 拓展分析全部完成！生成 3 张图：")
print("  ext_figA_MK突变检验.png")
print("  ext_figB_小波分析.png")
print("  ext_figC_极端气候指数.png")
