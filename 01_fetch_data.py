#!/usr/bin/env python3
"""
统一数据下载：Open-Meteo ERA5 → 月均温 + 月降水量
城市：兰州 西安 西宁 | 时段：1960-2025
"""

import requests
import pandas as pd
import numpy as np
import os
import time

CITIES = {
    "兰州": (36.05, 103.88),
    "西安": (34.30, 108.93),
    "西宁": (36.62, 101.77),
}

START = "1960-01-01"
END = "2025-12-31"
OUT_DIR = "data"

os.makedirs(OUT_DIR, exist_ok=True)

for city, (lat, lon) in CITIES.items():
    print(f"\n{'='*50}")
    print(f"[{city}] lat={lat}, lon={lon} | {START} → {END}")

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={START}&end_date={END}"
        "&daily=temperature_2m_mean,precipitation_sum"
        "&timezone=Asia/Shanghai"
    )

    resp = requests.get(url, timeout=60)
    data = resp.json()

    daily = data["daily"]
    dates = pd.to_datetime(daily["time"])
    temps = daily["temperature_2m_mean"]
    precips = daily["precipitation_sum"]

    df = pd.DataFrame({
        "date": dates,
        "temp": temps,
        "precip": precips,
    })
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # 月均温
    monthly_temp = df.groupby(["year", "month"])["temp"].mean().round(2)
    temp_wide = monthly_temp.unstack(level="month")
    temp_wide.columns = [f"{m}月" for m in range(1, 13)]
    temp_wide.index.name = "年"
    temp_wide = temp_wide.reset_index()

    # 月降水
    monthly_prec = df.groupby(["year", "month"])["precip"].sum().round(1)
    prec_wide = monthly_prec.unstack(level="month")
    prec_wide.columns = [f"{m}月" for m in range(1, 13)]
    prec_wide.index.name = "年"
    prec_wide = prec_wide.reset_index()

    # 保存
    temp_path = os.path.join(OUT_DIR, f"{city}_月均温.csv")
    prec_path = os.path.join(OUT_DIR, f"{city}_月降水量.csv")

    temp_wide.to_csv(temp_path, index=False, encoding="utf-8-sig")
    prec_wide.to_csv(prec_path, index=False, encoding="utf-8-sig")

    # 统计摘要
    annual_t = temp_wide.set_index("年").mean(axis=1)
    annual_p = prec_wide.set_index("年").sum(axis=1)

    print(f"  气温: {temp_wide.shape[0]}年, 均值 {annual_t.mean():.1f}°C, 范围 [{annual_t.min():.1f}, {annual_t.max():.1f}]")
    print(f"  降水: {prec_wide.shape[0]}年, 均值 {annual_p.mean():.0f}mm, 范围 [{annual_p.min():.0f}, {annual_p.max():.0f}]")
    print(f"  已保存: {temp_path}, {prec_path}")

    time.sleep(1)

# 汇总
print("\n" + "=" * 50)
print("✅ 数据下载完成！统一源 = Open-Meteo ERA5")
print(f"   时间范围: {START} → {END} (共 {2025-1960+1} 年)")
for city in CITIES:
    t = pd.read_csv(os.path.join(OUT_DIR, f"{city}_月均温.csv"))
    p = pd.read_csv(os.path.join(OUT_DIR, f"{city}_月降水量.csv"))
    print(f"   {city}: {t.shape[0]}年气温 + {p.shape[0]}年降水")
