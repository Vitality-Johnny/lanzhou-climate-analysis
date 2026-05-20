# 🌍 Lanzhou Climate Comparison (1960–2025)

Multi-city climate change analysis: **Lanzhou · Xi'an · Xining** — 66 years, unified ERA5 source.

## Key Findings (v2 — unified data source)

| City | Temp Trend | Precip Trend |
|------|-----------|-------------|
| Xi'an (14°C) | 📈 **+0.030°C/yr** (p<0.001) | 📉 −6.2 mm/yr (p<0.001) |
| Lanzhou (10°C) | 📈 **+0.034°C/yr** (p<0.001) | 📉 −2.4 mm/yr (p<0.001) |
| Xining (6°C) | 📈 **+0.038°C/yr** (p<0.001) | 📉 −4.1 mm/yr (p<0.001) |

> ⚠️ An earlier version using mixed data sources (GHCN + lishi.tianqi) falsely suggested Lanzhou was cooling. Switching to a single unified ERA5 source revealed the true warming signal — a lesson in data consistency.

## Methods
- 📊 Linear regression with R²/p-values
- 🔬 Mann-Kendall trend + mutation test
- 🌊 Morlet wavelet periodicity analysis
- 🌡️ Extreme climate indices

## Quick Start
```bash
pip install -r requirements.txt
bash run.sh
```

## Full Report
[📄 报告_兰州及周边城市气候变化特征对比分析.md](报告_兰州及周边城市气候变化特征对比分析.md)
