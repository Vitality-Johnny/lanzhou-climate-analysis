# 🌍 兰州及周边城市气候变化特征对比分析（2015–2025）

> **作者：** 陶彦霖 | **院系：** 兰州大学 · 大气科学学院 · 大一  
> **数据源：** GHCN-Daily + lishi.tianqi.com + Open-Meteo (ERA5)  
> **方法：** 线性回归 · Mann-Kendall 趋势检验 · matplotlib 可视化

## 📊 项目概述

对比分析 **兰州、西安、西宁** 三个城市 2015–2025 年的月均温和月降水量变化特征。

## 🔑 核心发现

| 城市 | 年均温趋势 | 年降水趋势 |
|------|-----------|-----------|
| 西安 | 📈 +0.127°C/yr (p<0.05) | → 波动大 (2021年1053mm) |
| 兰州 | 📉 -0.177°C/yr (p<0.01) | → 略减 |
| 西宁 | → 不显著 | 📉 -20.0mm/yr (p<0.05) |

## 📁 文件结构

```
├── data/                    # 6 个 CSV 原始数据
├── tidy_climate_data.csv    # 合并长表 (396行)
├── annual_summary.csv       # 年度汇总
├── fig1-5_*.png             # 5 张 matplotlib 可视化图
├── 01_clean_and_merge.py    # 数据清洗+合并
├── 02_visualize.py          # 可视化+趋势分析
├── 03_fill_missing_temps.py # Open-Meteo 补全缺失值
└── 报告_*.md                # 完整分析报告
```

## 🛠 技术栈

Python 3.12 · pandas · matplotlib · scipy · requests

## 📝 报告

详见 [`报告_兰州及周边城市气候变化特征对比分析.md`](报告_兰州及周边城市气候变化特征对比分析.md)
