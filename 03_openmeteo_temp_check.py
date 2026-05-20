#!/usr/bin/env python3
"""
补全 2025 年缺失的月均温数据
来源: Open-Meteo Archive API (daily temperature_2m_mean)
目标:
  - 兰州: 补 2025.9-12 (4个月)  ← 现有 lishi.tianqi 到 2025-08
  - 西安: 补 2025.8-12 (5个月)  ← 现有 GHCN 到 2025-07
  - 西宁: 补 2025.8-12 (5个月)  ← 现有 GHCN 到 2025-07
"""

import requests
import pandas as pd
import numpy as np
import time

CITIES = {
    "兰州": (36.05, 103.88),
    "西安": (34.30, 108.93),
    "西宁": (36.62, 101.77),
}

START = "2025-01-01"
END = "2025-12-31"

for city, (lat, lon) in CITIES.items():
    print(f"\n{'='*50}")
    print(f"[{city}] lat={lat}, lon={lon}")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={START}&end_date={END}"
        f"&daily=temperature_2m_mean"
        f"&timezone=Asia/Shanghai"
    )

    resp = requests.get(url, timeout=30)
    data = resp.json()

    # 解析每日数据
    dates = data["daily"]["time"]
    temps = data["daily"]["temperature_2m_mean"]

    # 转为 DataFrame 按月聚合
    df_daily = pd.DataFrame({"date": pd.to_datetime(dates), "temp": temps})
    df_daily["month"] = df_daily["date"].dt.month
    monthly = df_daily.groupby("month")["temp"].mean().round(2)

    print(f"  2025年月均温 (Open-Meteo):")
    for m in range(1, 13):
        if m in monthly.index:
            print(f"    {m}月: {monthly[m]:.2f}°C")
        else:
            print(f"    {m}月: N/A")

    print(f"  年均温: {monthly.mean():.2f}°C")

    # ───── 对比：现有数据 vs Open-Meteo ─────
    existing_file = f"data/{city}_月均温.csv"
    df_existing = pd.read_csv(existing_file, encoding="utf-8-sig")
    row_2025 = df_existing[df_existing["年"] == 2025]

    if len(row_2025) > 0:
        print(f"\n  对比（现有 vs Open-Meteo）:")
        for m in range(1, 13):
            existing_val = row_2025.iloc[0, m]  # column index m
            om_val = monthly.get(m, np.nan)
            if pd.notna(existing_val) and not pd.isna(om_val):
                diff = om_val - existing_val
                flag = "⚠️" if abs(diff) > 2 else "✅"
                print(f"    {m}月: 现有={existing_val:.2f}  OM={om_val:.2f}  Δ={diff:+.2f} {flag}")
            elif pd.isna(existing_val) and not pd.isna(om_val):
                print(f"    {m}月: 现有=缺失  OM={om_val:.2f}  ← 补全")
            elif pd.notna(existing_val) and pd.isna(om_val):
                print(f"    {m}月: 现有={existing_val:.2f}  OM=缺失")

    time.sleep(1)  # 礼貌等待

print("\n✅ Open-Meteo 数据获取完成")
