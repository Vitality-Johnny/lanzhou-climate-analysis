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
- 🌊 Morlet 小波周期分析
- 🌡️ 极端气候指数

## Quick Start
```bash
pip install -r requirements.txt
bash run.sh
```
