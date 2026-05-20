#!/usr/bin/env python3
"""
Phase 4: 数据可视化 — 5 张高质量 matplotlib 图表
包含：线性回归、R²、p值、季节分析、M-K 检验（加分项）
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ───── 全局样式设置 ─────
plt.rcParams.update({
    "font.family": "SimHei",
    "axes.unicode_minus": False,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

COLORS = {"兰州": "#e74c3c", "西安": "#3498db", "西宁": "#2ecc71"}
SEASON_ORDER = ["春季", "夏季", "秋季", "冬季"]
SEASON_COLORS = {"春季": "#27ae60", "夏季": "#e74c3c", "秋季": "#f39c12", "冬季": "#3498db"}

# ───── 加载数据 ─────
df = pd.read_csv("tidy_climate_data.csv")
annual = pd.read_csv("annual_summary.csv")

print("=" * 60)
print("Phase 4: 数据可视化 + 趋势分析")
print("=" * 60)

# ───── 辅助函数 ─────
def linear_regression(x, y, label=None):
    """线性回归，返回斜率、R²、p值"""
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean, y_clean = x[mask], y[mask]
    if len(x_clean) < 3:
        return np.nan, np.nan, np.nan, [], []
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
    r2 = r_value ** 2
    trend_line = slope * x_clean + intercept
    if label:
        print(f"  {label}: slope={slope:.3f}/yr, R²={r2:.3f}, p={p_value:.4f}")
    return slope, r2, p_value, x_clean, trend_line


def mk_test(data):
    """Mann-Kendall 趋势检验（加分项）"""
    n = len(data)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(data[j] - data[i])
    var_s = n * (n - 1) * (2 * n + 5) / 18
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return s, z, p_value


# ───── 图1: 年均温变化趋势折线图 ─────
print("\n【图1】年均温变化趋势")
fig, ax = plt.subplots(figsize=(10, 6))

for city in ["兰州", "西安", "西宁"]:
    data = annual[annual["城市"] == city].dropna(subset=["年均温"])
    # 回归只用完整年份（排除2025部分数据）
    data_full = data[data["年"] < 2025]
    x = data["年"].values
    y = data["年均温"].values
    ax.plot(x, y, "o-", color=COLORS[city], linewidth=2, markersize=6, label=city, zorder=3)
    x_reg = data_full["年"].values.astype(float)
    y_reg = data_full["年均温"].values
    slope, r2, p, x_fit, y_fit = linear_regression(
        x_reg, y_reg, label=f"{city}年均温"
    )
    if len(x_fit) > 0:
        ax.plot(x_fit, y_fit, "--", color=COLORS[city], linewidth=1, alpha=0.7)
        sign = "+" if slope >= 0 else ""
        ax.annotate(
            f"{sign}{slope:.3f}°C/yr\nR²={r2:.3f}",
            xy=(x_fit[-1], y_fit[-1]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            color=COLORS[city],
            alpha=0.8,
        )

ax.set_xlabel("年份", fontsize=12)
ax.set_ylabel("年均温 (°C)", fontsize=12)
ax.set_title("图1: 兰州-西安-西宁 年均温变化趋势 (2015–2025)", fontsize=14, fontweight="bold")
ax.legend(fontsize=10, loc="upper left")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
fig.tight_layout()
fig.savefig("fig1_年均温趋势.png", dpi=150)
plt.close(fig)
print("  ✅ 已保存: fig1_年均温趋势.png")


# ───── 图2: 年降水量变化趋势 ─────
print("\n【图2】年降水量变化趋势")
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()  # 副轴用于标注趋势

bar_width = 0.25
years_full = sorted(annual["年"].unique())
n_cities = 3
x_positions = np.arange(len(years_full))

for idx, (city, color) in enumerate(COLORS.items()):
    data = annual[annual["城市"] == city].dropna(subset=["年降水"])
    x_offset = x_positions + (idx - 1) * bar_width
    bars = ax1.bar(x_offset, np.zeros(len(years_full)), bar_width,
                   label=city, color=color, alpha=0.85, edgecolor="white", linewidth=0.5)

    for i, year in enumerate(years_full):
        row = data[data["年"] == year]
        if len(row) > 0:
            bars[i].set_height(row["年降水"].values[0])

    # 线性趋势
    x = data["年"].values.astype(float)
    y = data["年降水"].values
    slope, r2, p, x_reg, y_reg = linear_regression(
        x, y, label=f"{city}年降水"
    )
    if len(x_reg) > 0:
        sign = "+" if slope >= 0 else ""
        ax2.plot(x_reg, y_reg, "-", color=color, linewidth=2, alpha=0.5)

ax1.set_xlabel("年份", fontsize=12)
ax1.set_ylabel("年降水量 (mm)", fontsize=12)
ax2.set_ylabel("")  # hide twin axis label
ax1.set_title("图2: 兰州-西安-西宁 年降水量变化趋势 (2015–2025)", fontsize=14, fontweight="bold")
ax1.set_xticks(x_positions)
ax1.set_xticklabels(years_full)
ax1.legend(fontsize=10, loc="upper left")
fig.tight_layout()
fig.savefig("fig2_年降水趋势.png", dpi=150)
plt.close(fig)
print("  ✅ 已保存: fig2_年降水趋势.png")


# ───── 图3: 季节气温分布箱线图 ─────
print("\n【图3】季节气温分布")
fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)

for idx, city in enumerate(["兰州", "西安", "西宁"]):
    ax = axes[idx]
    city_data = df[df["城市"] == city].dropna(subset=["月均温"])
    box_data = [city_data[city_data["季节"] == s]["月均温"].dropna().values
                for s in SEASON_ORDER]
    bp = ax.boxplot(box_data, labels=SEASON_ORDER, patch_artist=True,
                    widths=0.5, showfliers=True, flierprops={"marker": "o", "markersize": 3, "alpha": 0.5})

    for patch, season in zip(bp["boxes"], SEASON_ORDER):
        patch.set_facecolor(SEASON_COLORS[season])
        patch.set_alpha(0.6)

    ax.set_title(city, fontsize=13, fontweight="bold", color=COLORS[city])
    ax.set_ylabel("月均温 (°C)" if idx == 0 else "")
    ax.tick_params(axis="x", rotation=30)

fig.suptitle("图3: 三城市季节气温分布箱线图 (2015–2025)", fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig("fig3_季节气温箱线图.png", dpi=150)
plt.close(fig)
print("  ✅ 已保存: fig3_季节气温箱线图.png")


# ───── 图4: 季节降水分布对比 ─────
print("\n【图4】季节降水对比")
fig, ax = plt.subplots(figsize=(10, 6))

# 计算各城市季节降水均值
season_prec = df.dropna(subset=["月降水量"]).groupby(["城市", "季节"])["月降水量"].mean().unstack(0)
season_prec = season_prec.reindex(SEASON_ORDER)

bar_width = 0.2
x = np.arange(len(SEASON_ORDER))
for idx, (city, color) in enumerate(COLORS.items()):
    offset = (idx - 1) * bar_width
    bars = ax.bar(x + offset, season_prec[city], bar_width,
                  label=city, color=color, alpha=0.8, edgecolor="white")

    for bar, val in zip(bars, season_prec[city]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.0f}", ha="center", va="bottom", fontsize=7, color=color)

ax.set_xticks(x)
ax.set_xticklabels(SEASON_ORDER, fontsize=11)
ax.set_ylabel("月均降水量 (mm)", fontsize=12)
ax.set_title("图4: 三城市季节月均降水量对比 (2015–2025)", fontsize=14, fontweight="bold")
ax.legend(fontsize=10)
fig.tight_layout()
fig.savefig("fig4_季节降水对比.png", dpi=150)
plt.close(fig)
print("  ✅ 已保存: fig4_季节降水对比.png")


# ───── 图5: 城市气候综合对比 + M-K 检验 ─────
print("\n【图5】综合对比 + M-K 检验")
fig = plt.figure(figsize=(12, 9))

# ── 子图 (a): 三城气候均值对比 ──
ax_a = fig.add_subplot(2, 2, 1)
city_means = annual[annual["年"] < 2025].groupby("城市")[["年均温", "年降水"]].mean()
ax2_twin = ax_a.twinx()
x_pos = np.arange(3)
bars_t = ax_a.bar(x_pos - 0.15, city_means["年均温"], 0.3,
                   color=[COLORS[c] for c in city_means.index], alpha=0.8, label="年均温(°C)")
bars_p = ax2_twin.bar(x_pos + 0.15, city_means["年降水"], 0.3,
                       color="lightgray", alpha=0.6, label="年降水(mm)")

ax_a.set_xticks(x_pos)
ax_a.set_xticklabels(city_means.index, fontsize=11)
ax_a.set_ylabel("年均温 (°C)", fontsize=10)
ax2_twin.set_ylabel("年降水 (mm)", fontsize=10)
ax_a.set_title("(a) 三城 10年均温/降水均值", fontsize=11, fontweight="bold")

# 标注数值
for bar, val in zip(bars_t, city_means["年均温"]):
    ax_a.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
              f"{val:.1f}°C", ha="center", fontsize=8)
for bar, val in zip(bars_p, city_means["年降水"]):
    ax2_twin.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                  f"{val:.0f}mm", ha="center", fontsize=8)

# ── 子图 (b): M-K 检验表 ──
ax_b = fig.add_subplot(2, 2, 2)
ax_b.axis("off")
mk_results = []
for city in ["兰州", "西安", "西宁"]:
    for var_name, col in [("年均温", "年均温"), ("年降水", "年降水")]:
        data = annual[(annual["城市"] == city) & (annual["年"] < 2025)][col].dropna().values
        if len(data) >= 3:
            s, z, p = mk_test(data)
            trend = "↑ 上升" if s > 0 else "↓ 下降" if s < 0 else "→ 稳定"
            sig = "**" if p < 0.05 else "*" if p < 0.1 else ""
            mk_results.append([city, var_name, trend, f"{z:.3f}", f"{p:.4f}", sig])

mk_df = pd.DataFrame(mk_results, columns=["城市", "变量", "趋势", "Z值", "p值", "显著性"])
table = ax_b.table(cellText=mk_df.values, colLabels=mk_df.columns,
                   cellLoc="center", loc="center")
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1.0, 1.4)
# 按照显著性着色
for i in range(len(mk_results)):
    sig = mk_results[i][-1]
    if sig == "**":
        for j in range(6):
            table[(i+1, j)].set_facecolor("#d4edda")
    elif sig == "*":
        for j in range(6):
            table[(i+1, j)].set_facecolor("#fff3cd")

ax_b.set_title("(b) Mann-Kendall 趋势检验结果", fontsize=11, fontweight="bold")

# ── 子图 (c): 逐年对比 — 年均温 ──
ax_c = fig.add_subplot(2, 2, 3)
for city in ["兰州", "西安", "西宁"]:
    data = annual[annual["城市"] == city].dropna(subset=["年均温"])
    ax_c.plot(data["年"], data["年均温"], "o-", color=COLORS[city], linewidth=1.5, markersize=4, label=city)
ax_c.set_xlabel("年份", fontsize=10)
ax_c.set_ylabel("年均温 (°C)", fontsize=10)
ax_c.set_title("(c) 逐年年均温", fontsize=11, fontweight="bold")
ax_c.legend(fontsize=8)

# ── 子图 (d): 逐年对比 — 年降水 ──
ax_d = fig.add_subplot(2, 2, 4)
for city in ["兰州", "西安", "西宁"]:
    data = annual[annual["城市"] == city].dropna(subset=["年降水"])
    ax_d.plot(data["年"], data["年降水"], "o-", color=COLORS[city], linewidth=1.5, markersize=4, label=city)
ax_d.set_xlabel("年份", fontsize=10)
ax_d.set_ylabel("年降水 (mm)", fontsize=10)
ax_d.set_title("(d) 逐年降水", fontsize=11, fontweight="bold")
ax_d.legend(fontsize=8)

fig.suptitle("图5: 三城市气候综合对比分析", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("fig5_综合对比.png", dpi=150)
plt.close(fig)
print("  ✅ 已保存: fig5_综合对比.png")


# ───── 汇总报告 ─────
print("\n" + "=" * 60)
print("【趋势分析汇总】")
print("=" * 60)

print("\n年均温趋势（线性回归）:")
for city in ["兰州", "西安", "西宁"]:
    data = annual[(annual["城市"] == city) & (annual["年"] < 2025)]["年均温"].dropna()
    x = data.index.values.astype(float) if len(data) > 0 else np.array([])
    y = data.values
    if len(y) >= 3:
        slope, r2, p, _, _ = linear_regression(
            2015 + np.arange(len(y)), y,
            label=f"{city}年均温"
        )
        print(f"  {city}: 变化率 {slope:+.3f}°C/yr, R²={r2:.3f}, p={p:.4f}")

print("\n年降水趋势（线性回归）:")
for city in ["兰州", "西安", "西宁"]:
    data = annual[(annual["城市"] == city) & (annual["年"] < 2025)]["年降水"].dropna()
    y = data.values
    if len(y) >= 3:
        slope, r2, p, _, _ = linear_regression(
            2015 + np.arange(len(y)), y,
            label=f"{city}年降水"
        )
        print(f"  {city}: 变化率 {slope:+.2f}mm/yr, R²={r2:.3f}, p={p:.4f}")

print("\n✅ 可视化完成！生成 5 张图：")
print("  fig1_年均温趋势.png")
print("  fig2_年降水趋势.png")
print("  fig3_季节气温箱线图.png")
print("  fig4_季节降水对比.png")
print("  fig5_综合对比.png")
