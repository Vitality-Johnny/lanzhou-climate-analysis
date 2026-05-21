#!/usr/bin/env python3
"""
城市间气候相关性分析: Pearson/Spearman 相关矩阵 + 热图
三城年均温、年降水的两两相关性
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "font.family": "SimHei",
    "axes.unicode_minus": False,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
})

# ───── 加载数据 ─────
annual = pd.read_csv("annual_summary.csv")
cities = ["兰州", "西安", "西宁"]
vars_ = ["年均温", "年降水"]
var_labels = {"年均温": "年均温 (°C)", "年降水": "年降水 (mm)"}

# ───── 构建三城 × 两变量相关矩阵 ─────
labels = []
for v in vars_:
    for c in cities:
        labels.append(f"{c}\n{v[:2]}")

n = len(labels)  # 6 × 6
pearson_mat = np.zeros((n, n))
spearman_mat = np.zeros((n, n))
p_pearson = np.zeros((n, n))
p_spearman = np.zeros((n, n))

# 提取各序列
series = {}
for v in vars_:
    for c in cities:
        d = annual[annual["城市"] == c].dropna(subset=[v])
        # 取公共年份交集
        series[(c, v)] = d.set_index("年")[v]

# 共享年份（取所有序列的交集年份）
all_years = series[("兰州", "年均温")].index
for key, s in series.items():
    all_years = all_years.intersection(s.index)

print(f"公共年份: {len(all_years)} 年 ({all_years[0]}-{all_years[-1]})")

# 计算相关矩阵
for i, (v1, c1) in enumerate([(v, c) for v in vars_ for c in cities]):
    for j, (v2, c2) in enumerate([(v, c) for v in vars_ for c in cities]):
        if i == j:
            pearson_mat[i, j] = 1.0
            spearman_mat[i, j] = 1.0
            p_pearson[i, j] = 0.0
            p_spearman[i, j] = 0.0
        else:
            s1 = series[(c1, v1)].loc[all_years]
            s2 = series[(c2, v2)].loc[all_years]
            r_p, p_p = stats.pearsonr(s1, s2)
            r_s, p_s = stats.spearmanr(s1, s2)
            pearson_mat[i, j] = r_p
            pearson_mat[j, i] = r_p
            spearman_mat[i, j] = r_s
            spearman_mat[j, i] = r_s
            p_pearson[i, j] = p_p
            p_spearman[i, j] = p_s

# ───── 画热图 ─────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, mat, p_mat, title in [
    (axes[0], pearson_mat, p_pearson, "Pearson 相关系数"),
    (axes[1], spearman_mat, p_spearman, "Spearman 秩相关系数"),
]:
    # mask上三角
    mask = np.triu(np.ones_like(mat, dtype=bool), k=1)
    mat_masked = np.ma.array(mat, mask=mask)

    im = ax.imshow(mat_masked, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")

    # 标注数值
    for i in range(n):
        for j in range(n):
            if i >= j:  # 下三角 + 对角线
                sig = "**" if p_mat[i, j] < 0.05 else "*" if p_mat[i, j] < 0.10 else ""
                text = f"{mat[i, j]:.2f}{sig}"
                color = "white" if abs(mat[i, j]) > 0.6 else "black"
                ax.text(j, i, text, ha="center", va="center", fontsize=9,
                        color=color, fontweight="bold" if sig else "normal")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, fontsize=8, rotation=45, ha="right")
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_title(title, fontweight="bold", fontsize=12)

    # 分组分隔线
    ax.axhline(2.5, color="gray", lw=1, ls="--", alpha=0.5)
    ax.axvline(2.5, color="gray", lw=1, ls="--", alpha=0.5)

    plt.colorbar(im, ax=ax, shrink=0.8, label="相关系数")

fig.suptitle("图6: 三城气候变量相关性矩阵 (1960–2025)", fontweight="bold", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("figures/fig6_相关性矩阵.png", dpi=150)
plt.close(fig)

# ───── 输出关键发现 ─────
print("\n" + "=" * 60)
print("关键相关发现 (|r| > 0.5)")
print("=" * 60)
for i in range(n):
    for j in range(i + 1, n):
        if abs(pearson_mat[i, j]) > 0.5 or abs(spearman_mat[i, j]) > 0.5:
            print(f"\n{labels[i].replace(chr(10), ' ')} ↔ {labels[j].replace(chr(10), ' ')}")
            print(f"  Pearson: r={pearson_mat[i,j]:.3f} (p={p_pearson[i,j]:.4f})")
            print(f"  Spearman: ρ={spearman_mat[i,j]:.3f} (p={p_spearman[i,j]:.4f})")

print(f"\n✅ fig6_相关性矩阵.png 已保存")
