#!/bin/bash
# 一键复现：兰州及周边城市气候变化特征对比分析
# 用法: bash run.sh

set -e
echo "========================================"
echo " 兰州及周边城市气候变化特征对比分析"
echo " 数据源: Open-Meteo ERA5 (1960-2025)"
echo "========================================"

echo ""
echo "[1/3] 下载数据..."
python3 01_fetch_data.py

echo ""
echo "[2/3] 清洗合并..."
python3 02_clean_and_merge.py

echo ""
echo "[3/3] 分析+可视化 (8张图)..."
python3 03_analyze_and_viz.py

echo ""
echo "========================================"
echo " ✅ 全部完成！"
echo " 图表: fig1-5_*.png + ext_figA-C_*.png"
echo " 数据: tidy_climate_data.csv + annual_summary.csv"
echo " 报告: 报告_*.md"
echo "========================================"
