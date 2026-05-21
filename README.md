# 🌍 兰州及周边城市气候变化特征对比分析 (1960–2025)

兰州·西安·西宁三城 66 年气候变化对比分析，统一 ERA5 数据源。

> 完整报告 → [报告_兰州及周边城市气候变化特征对比分析.md](报告_兰州及周边城市气候变化特征对比分析.md)

## 主要发现

| 城市 | 年均温 | 趋势 | 年降水 | 趋势 |
|------|:-----:|------|:-----:|------|
| 西安 | 14°C | 📈 **+0.030°C/yr** (p<0.001) | 888 mm | 📉 −6.4 mm/yr |
| 兰州 | 10°C | 📈 **+0.034°C/yr** (p<0.001) | 457 mm | 📉 −2.3 mm/yr |
| 西宁 | 6°C | 📈 **+0.038°C/yr** (p<0.001) | 717 mm | 📉 −4.2 mm/yr |

> ⚠️ v1 使用混合数据源（GHCN + lishi.tianqi）错误得出"兰州降温"。v2 统一 ERA5 后三城一致变暖——数据源一致性至关重要。

## 分析方法

- 📊 线性回归 + Theil-Sen 稳健趋势 + 95% 置信区间
- 🔬 Mann-Kendall 趋势检验 + 突变检验
- 🌊 Morlet 小波周期分析 + 红噪声显著性 + COI
- 🌡️ 极端气候指数（暖月/冷月/湿月/旱月）
- 🔗 三城 Pearson/Spearman 相关性矩阵
- 🗺️ 地理标注地图（folium 交互式）

## 数据来源

所有气象数据来自 **ERA5** 再分析，通过 [Open-Meteo API](https://open-meteo.com/) 获取。

| 参数 | 覆盖范围 | 分辨率 |
|------|----------|--------|
| 2m 气温 | 1960-01–2025-12 | 月均 |
| 总降水量 | 1960-01–2025-12 | 月均 |

### 引用

> Hersbach, H., Bell, B., Berrisford, P., et al. (2020): The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049. DOI: [10.1002/qj.3803](https://doi.org/10.1002/qj.3803)

数据通过 Copernicus Climate Data Store 获取：[cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/)

## 快速开始

```bash
pip install -r requirements.txt
bash run.sh
```
