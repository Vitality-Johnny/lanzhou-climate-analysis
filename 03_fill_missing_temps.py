#!/usr/bin/env python3
"""
用 Open-Meteo 补全 2025 年缺失月均温
兰州: 补 9-12月 | 西安/西宁: 补 8-12月
"""

import requests
import pandas as pd
import numpy as np
import time
import os

CITIES = {
    "兰州": (36.05, 103.88),
    "西安": (34.30, 108.93),
    "西宁": (36.62, 101.77),
}

START = "2025-01-01"
END = "2025-12-31"

for city, (lat, lon) in CITIES.items():
    print(f"\n{'='*50}")
    print(f"[{city}] 获取 Open-Meteo 2025 年月均温")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={START}&end_date={END}"
        f"&daily=temperature_2m_mean"
        f"&timezone=Asia/Shanghai"
    )

    resp = requests.get(url, timeout=30)
    data = resp.json()
    dates = pd.to_datetime(data["daily"]["time"])
    temps = data["daily"]["temperature_2m_mean"]

    df_daily = pd.DataFrame({"date": dates, "temp": temps})
    df_daily["month"] = df_daily["date"].dt.month
    monthly = df_daily.groupby("month")["temp"].mean().round(2)

    # ───── 读取现有文件 ─────
    csv_path = f"data/{city}_月均温.csv"
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.rstrip(",") for l in content.strip().split("\n")]

    header = lines[0]
    data_lines = lines[1:]

    # 解析表头
    cols = header.split(",")

    # 找 2025 行
    for i, line in enumerate(data_lines):
        vals = line.split(",")
        year = int(vals[0].strip())
        if year == 2025:
            # 确保有 13 列（年 + 12 个月）
            while len(vals) < 13:
                vals.append("")

            filled = []
            for m in range(1, 13):
                existing = vals[m].strip() if m < len(vals) else ""
                if existing == "" or existing.lower() == "nan":
                    om_val = monthly.get(m, np.nan)
                    if not np.isnan(om_val):
                        filled.append(f"{m}月: 空→{om_val}°C")
                        vals[m] = f"{om_val:.2f}"
                    else:
                        vals[m] = ""
                else:
                    vals[m] = vals[m].strip()

            # 重建行
            data_lines[i] = ",".join(vals[:13])

            print(f"  {', '.join(filled) if filled else '无需补全'}")
            break

    # ───── 写回文件（UTF-8 BOM） ─────
    new_content = "\n".join([header] + data_lines)
    with open(csv_path, "w", encoding="utf-8-sig") as f:
        f.write(new_content)
    print(f"  已保存: {csv_path}")

    time.sleep(1)

print("\n✅ 全部补全完成！")
