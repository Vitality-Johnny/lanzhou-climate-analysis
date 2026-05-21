# 🌍 兰州及周边城市气候变化特征对比分析 (1960–2025)

兰州·西安·西宁三城 66 年气候变化对比分析，统一 ERA5 数据源。

> 完整报告 → [报告_兰州及周边城市气候变化特征对比分析.md](报告_兰州及周边城市气候变化特征对比分析.md)

## 📈 结果预览

### 年均温变化趋势

![年均温趋势](fig1_年均温趋势.png)

*三城年均温均显著上升（Theil-Sen + 95% CI），西宁增幅最大（+0.038°C/yr）*

### 年降水变化趋势

![年降水趋势](fig2_年降水趋势.png)

*三城降水均显著下降，西安最剧烈（−6.4 mm/yr）*

### 三城气候相关性矩阵

![相关性矩阵](fig6_相关性矩阵.png)

*气温高度同步（兰州-西宁 r=0.88），降水协同较弱；升温与降水负相关（西安 r=−0.62）*

## 主要发现

| 城市 | 年均温 | 趋势 (Theil-Sen) | 年降水 | 趋势 (Theil-Sen) |
|------|:-----:|------|:-----:|------|
| 西安 | 14°C | 📈 **+0.029°C/yr** [0.022, 0.037] | 888 mm | 📉 **−6.4 mm/yr** [−9.0, −4.0] |
| 兰州 | 10°C | 📈 **+0.034°C/yr** [0.026, 0.041] | 457 mm | 📉 **−2.3 mm/yr** [−3.5, −1.4] |
| 西宁 | 6°C | 📈 **+0.038°C/yr** [0.031, 0.046] | 717 mm | 📉 **−4.2 mm/yr** [−5.7, −2.8] |

> ⚠️ v1 使用混合数据源（GHCN + lishi.tianqi）错误得出"兰州降温"。v2 统一 ERA5 后三城一致变暖——数据源一致性至关重要。

## 分析方法

1. **数据获取与清洗** — ERA5 再分析数据通过 Open-Meteo API 获取，统一处理缺失值与异常值
2. **趋势分析** — 线性回归 + Theil-Sen 稳健斜率（`scipy.stats.theilslopes`）+ Bootstrap 95% 置信区间
3. **突变检验** — Mann-Kendall 趋势检验 + 正向/反向序列突变点检测（UF/UB）
4. **周期分析** — Morlet 连续小波变换 + 红噪声显著性检验 + COI 边界遮罩 + 全局小波谱
5. **极端指数** — 基于月值分位数定义的暖月/冷月/湿月/旱月指数
6. **空间相关** — 三城 Pearson/Spearman 相关性矩阵
7. **地理可视化** — folium 交互式地图标注三城位置及海拔

## 数据来源

所有气象数据来自 **ERA5** 再分析，通过 [Open-Meteo API](https://open-meteo.com/) 免费获取。

| 参数 | 覆盖范围 | 分辨率 |
|------|----------|--------|
| 2m 气温 | 1960-01–2025-12 | 月均 |
| 总降水量 | 1960-01–2025-12 | 月均 |

### 引用

> Hersbach, H., Bell, B., Berrisford, P., et al. (2020): The ERA5 global reanalysis. *Q. J. R. Meteorol. Soc.*, 146(730), 1999–2049. [DOI: 10.1002/qj.3803](https://doi.org/10.1002/qj.3803)

数据通过 Copernicus CDS 获取：[cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/)

## 项目结构

```
├── 01_fetch_data.py          # 数据获取
├── 02_clean_and_merge.py     # 数据清洗与合并
├── 02b_visualize.py          # 基础可视化（旧版）
├── 03_analyze_and_viz.py     # 核心分析 + 8 张图（Theil-Sen, MK, 小波, 极端指数）
├── 04_extended_analysis.py   # 扩展分析
├── 05_correlation_analysis.py # 三城相关性矩阵
├── 06_map_visualization.py   # 地图可视化
├── figures/                  # 输出图表
├── data/                     # 原始数据（ERA5）
├── requirements.txt
├── run.sh
└── README.md
```

## 快速开始

```bash
pip install -r requirements.txt
bash run.sh
```

## 后续方向

| 优先级 | 方向 | 说明 |
|:--:|------|------|
| 🥇 | **xarray + netCDF4** | 原生 ERA5 网格数据处理，替代 CSV 中间格式 |
| 🥇 | **cartopy 空间可视化** | 加载地形、省份边界，学术出版级地图（当前为 folium） |
| 🥈 | **EOF 分析** | 三城气温/降水时空模态分解，提取主导变率 |
| 🥈 | **更长时段** | ERA5 回溯至 1940 年，跨度量翻倍至 85 年 |
| 🥉 | **更多城市** | 加入成都、银川构建西北城市气候网络 |
