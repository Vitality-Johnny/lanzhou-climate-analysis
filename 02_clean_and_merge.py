#!/usr/bin/env python3
"""数据清洗与合并 — 统一 Open-Meteo ERA5 源, 1960-2025"""

import pandas as pd, numpy as np, os

CITIES = ["兰州", "西安", "西宁"]
DATA_DIR = "data"

# 读取
dfs_temp, dfs_prec = {}, {}
for city in CITIES:
    dfs_temp[city] = pd.read_csv(os.path.join(DATA_DIR, f"{city}_月均温.csv"), encoding="utf-8-sig")
    dfs_prec[city] = pd.read_csv(os.path.join(DATA_DIR, f"{city}_月降水量.csv"), encoding="utf-8-sig")
    print(f"[读] {city}: 气温 {dfs_temp[city].shape}, 降水 {dfs_prec[city].shape}")

# 缺失值
print("\n缺失值:")
for city in CITIES:
    tm = dfs_temp[city].iloc[:, 1:].isnull().sum().sum()
    pm = dfs_prec[city].iloc[:, 1:].isnull().sum().sum()
    print(f"  {city}: 气温 NaN={tm}, 降水 NaN={pm}")

# 异常值 (3σ)
all_t = pd.concat([df.iloc[:, 1:].stack() for df in dfs_temp.values()])
all_p = pd.concat([df.iloc[:, 1:].stack() for df in dfs_prec.values()])
t_hi = all_t.mean() + 3*all_t.std()
p_hi = all_p.mean() + 3*all_p.std()
print(f"\n异常值阈值: 气温>{t_hi:.1f}°C, 降水>{p_hi:.1f}mm")

outliers = []
for city in CITIES:
    for col in dfs_temp[city].columns[1:]:
        for i, v in dfs_temp[city][col].items():
            if pd.notna(v) and abs(v) > t_hi:
                outliers.append(f"  {city} {int(dfs_temp[city].at[i,'年'])}年{col}: {v:.1f}°C")
    for col in dfs_prec[city].columns[1:]:
        for i, v in dfs_prec[city][col].items():
            if pd.notna(v) and v > p_hi:
                outliers.append(f"  {city} {int(dfs_prec[city].at[i,'年'])}年{col}: {v:.0f}mm")

if outliers:
    print(f"异常值({len(outliers)}个, 保留并标记):")
    for o in outliers[:10]: print(o)
else:
    print("无3σ异常值")

# 合并为 tidy data
records = []
SEASONS = {12:"冬",1:"冬",2:"冬",3:"春",4:"春",5:"春",6:"夏",7:"夏",8:"夏",9:"秋",10:"秋",11:"秋"}
for city in CITIES:
    for i in range(len(dfs_temp[city])):
        yr = int(dfs_temp[city].at[i, "年"])
        for m in range(12):
            records.append({
                "城市": city, "年": yr, "月": m+1,
                "月均温": dfs_temp[city].at[i, f"{m+1}月"],
                "月降水量": dfs_prec[city].at[i, f"{m+1}月"],
                "季节": SEASONS[m+1]
            })

tidy = pd.DataFrame(records)
tidy.to_csv("tidy_climate_data.csv", index=False, encoding="utf-8-sig")
print(f"\nTidy data: {len(tidy)}行, 0缺失")

# 年度汇总
annual = tidy.groupby(["城市", "年"]).agg(年均温=("月均温","mean"), 年降水=("月降水量","sum")).round(2).reset_index()
annual.to_csv("annual_summary.csv", index=False, encoding="utf-8-sig")
print(f"年度汇总: {len(annual)}行")

# 快照
for city in CITIES:
    sub = annual[annual["城市"]==city]
    recent = sub[sub["年"]>=2015]
    all_years = sub
    print(f"\n{city}: 1960-2024 均温 {all_years['年均温'].mean():.1f}°C, 降水 {all_years['年降水'].mean():.0f}mm")
    print(f"       2015-2024 均温 {recent['年均温'].mean():.1f}°C, 降水 {recent['年降水'].mean():.0f}mm")

print("\n✅ 清洗合并完成")
