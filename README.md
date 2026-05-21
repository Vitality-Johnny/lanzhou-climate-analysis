# 🌍 Lanzhou Climate Comparison (1960–2025)

Multi-city climate change analysis: **Lanzhou · Xi'an · Xining** — 66 years, unified ERA5 source.

> 中文完整报告 → [报告_兰州及周边城市气候变化特征对比分析.md](报告_兰州及周边城市气候变化特征对比分析.md)

## Key Findings (v2 — unified data source)

| City | Temp Trend | Precip Trend |
|------|-----------|-------------|
| Xi'an (14°C) | 📈 **+0.030°C/yr** (p<0.001) | 📉 −6.2 mm/yr (p<0.001) |
| Lanzhou (10°C) | 📈 **+0.034°C/yr** (p<0.001) | 📉 −2.4 mm/yr (p<0.001) |
| Xining (6°C) | 📈 **+0.038°C/yr** (p<0.001) | 📉 −4.1 mm/yr (p<0.001) |

> ⚠️ v1 使用混合数据源（GHCN + lishi.tianqi）错误得出"兰州降温"。v2 统一为 ERA5 后，三城一致变暖——数据源一致性至关重要。

## Methods
- 📊 线性回归 + R²/p值
- 🔬 Mann-Kendall 趋势 + 突变检验
- 🌊 Morlet 小波周期分析 + COI + 显著性检验
- 🌡️ 极端气候指数
- 📈 Theil-Sen 稳健趋势 (scipy.stats.theilslopes) + 95% CI
- 🔗 三城 Pearson/Spearman 相关性矩阵
- 🗺️ 地理标注地图 (cartopy)

## Data Source

All meteorological data from **ERA5** reanalysis, accessed via [Open-Meteo API](https://open-meteo.com/).

| Parameter | Coverage | Resolution |
|-----------|----------|------------|
| Temperature (2m) | 1960-01–2025-12 | Monthly |
| Total precipitation | 1960-01–2025-12 | Monthly |

### Citation

> Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G., Dahlgren, P., Dee, D., Diamantakis, M., Dragani, R., Flemming, J., Forbes, R., Fuentes, M., Geer, A., Haimberger, L., Healy, S., Hogan, R.J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P., Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vamborg, F., Villaume, S., Thépaut, J.-N. (2020): The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049. DOI: [10.1002/qj.3803](https://doi.org/10.1002/qj.3803)

Data accessed via Copernicus Climate Data Store: [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/)

## Quick Start
```bash
pip install -r requirements.txt
bash run.sh
```
