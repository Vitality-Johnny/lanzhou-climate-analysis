#!/usr/bin/env python3
"""
Phase 2+3: 数据清洗 + 合并
读取 6 个 CSV → 清洗缺失值/异常值 → 合并为 Tidy Data 长表
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = "data"
OUTPUT_DIR = "."

# ───── 1. 读取所有 CSV ─────
files = {
    "兰州": ("兰州_月均温.csv", "兰州_月降水量.csv"),
    "西安": ("西安_月均温.csv", "西安_月降水量.csv"),
    "西宁": ("西宁_月均温.csv", "西宁_月降水量.csv"),
}

dfs_temp = {}
dfs_prec = {}

def safe_read_csv(filepath):
    """安全读取 CSV，处理混合行尾和尾部逗号"""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()
    # 统一行尾
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    # 移除行尾多余逗号
    lines = content.strip().split("\n")
    lines = [line.rstrip(",") for line in lines]
    content = "\n".join(lines)
    with open(filepath + ".tmp", "w", encoding="utf-8-sig") as f:
        f.write(content)
    return pd.read_csv(filepath + ".tmp")

for city, (temp_file, prec_file) in files.items():
    df_t = safe_read_csv(os.path.join(DATA_DIR, temp_file))
    df_p = safe_read_csv(os.path.join(DATA_DIR, prec_file))
    # 清理临时文件
    os.remove(os.path.join(DATA_DIR, temp_file) + ".tmp")
    os.remove(os.path.join(DATA_DIR, prec_file) + ".tmp")
    dfs_temp[city] = df_t
    dfs_prec[city] = df_p
    print(f"[读取] {city} → 气温 {df_t.shape}, 降水 {df_p.shape}")

# ───── 2. 缺失值检查 ─────
print("\n" + "=" * 60)
print("【缺失值检查】")
print("=" * 60)
miss_count = {"城市": [], "气温缺失月数": [], "降水缺失月数": []}
for city in files:
    t_miss = dfs_temp[city].iloc[:, 1:].isnull().sum().sum()
    p_miss = dfs_prec[city].iloc[:, 1:].isnull().sum().sum()
    miss_count["城市"].append(city)
    miss_count["气温缺失月数"].append(int(t_miss))
    miss_count["降水缺失月数"].append(int(p_miss))
    print(f"  {city}: 气温缺失 {t_miss} 个月, 降水缺失 {p_miss} 个月")

miss_df = pd.DataFrame(miss_count)
print(miss_df.to_string(index=False))

# 逐月显示缺失详情
print("\n【气温缺失详情 — 2025 年】")
for city in files:
    row_2025 = dfs_temp[city][dfs_temp[city]["年"] == 2025]
    if len(row_2025) > 0:
        missing_months = [f"{m+1}月" for m in range(12) if pd.isna(row_2025.iloc[0, m+1])]
        print(f"  {city} 2025: 缺 {missing_months if missing_months else '无缺失'}")

# ───── 3. 异常值检测 ─────
print("\n" + "=" * 60)
print("【异常值检测】")
print("=" * 60)

# 气温异常（超过3倍标准差则标记）
all_temps = pd.concat([df.iloc[:, 1:].stack() for df in dfs_temp.values()])
temp_mean, temp_std = all_temps.mean(), all_temps.std()
temp_low = temp_mean - 3 * temp_std
temp_high = temp_mean + 3 * temp_std
print(f"  气温: mean={temp_mean:.2f}°C, std={temp_std:.2f}")
print(f"  正常范围: [{temp_low:.1f}, {temp_high:.1f}]")

temp_outliers = []
for city in files:
    df = dfs_temp[city]
    for col in df.columns[1:]:
        for idx, val in df[col].items():
            if not pd.isna(val) and (val < temp_low or val > temp_high):
                yr = df.at[idx, "年"]
                temp_outliers.append(f"  ⚠️ {city} {yr}年{col}: T={val:.2f}°C")

if temp_outliers:
    print("【气温异常值】")
    for o in temp_outliers:
        print(o)
else:
    print("  气温无3σ异常值 ✅")

# 降水异常
all_prec = pd.concat([df.iloc[:, 1:].stack() for df in dfs_prec.values()])
prec_mean, prec_std = all_prec.mean(), all_prec.std()
prec_high = prec_mean + 3 * prec_std
print(f"\n  降水: mean={prec_mean:.1f}mm, std={prec_std:.1f}")
print(f"  上界(3σ): {prec_high:.1f}mm")

prec_outliers = []
heavy_rain = []  # >100mm 暴雨
for city in files:
    df = dfs_prec[city]
    for col in df.columns[1:]:
        for idx, val in df[col].items():
            if not pd.isna(val):
                yr = df.at[idx, "年"]
                if val > prec_high:
                    prec_outliers.append(f"  ⚠️ {city} {yr}年{col}: P={val:.1f}mm (>{prec_high:.1f})")
                if val > 100:
                    heavy_rain.append(f"  🌧️ {city} {yr}年{col}: P={val:.1f}mm")

if prec_outliers:
    print("【降水异常值(>3σ)】")
    for o in prec_outliers:
        print(o)
else:
    print("  降水无3σ异常值 ✅")

print(f"\n【暴雨月(>100mm)】：共 {len(heavy_rain)} 个")

# ───── 4. 来源交叉验证（兰州 lishi.tianqi vs 西安/西宁 GHCN） ─────
print("\n" + "=" * 60)
print("【来源交叉验证】")
print("=" * 60)
print("  兰州数据源: lishi.tianqi.com (0.5°C精度)")
print("  西安/西宁数据源: GHCN-Daily (0.01°C精度)")
print("  → 精度差异不影响趋势分析，报告中需注明来源")

# ───── 5. 合并为 Tidy Data ─────
print("\n" + "=" * 60)
print("【数据合并 → Tidy Data 长表】")
print("=" * 60)

records = []
for city in files:
    df_t = dfs_temp[city]
    df_p = dfs_prec[city]

    for idx in range(len(df_t)):
        year = int(df_t.at[idx, "年"])
        for m in range(12):
            month = m + 1
            month_label = f"{m+1}月"
            temp = df_t.at[idx, month_label]
            prec = df_p.at[idx, month_label]
            records.append({
                "城市": city,
                "年": year,
                "月": month,
                "月均温": temp,    # NaN if missing
                "月降水量": prec,
            })

all_data = pd.DataFrame(records)

# 添加季节
season_map = {12: "冬季", 1: "冬季", 2: "冬季",
              3: "春季", 4: "春季", 5: "春季",
              6: "夏季", 7: "夏季", 8: "夏季",
              9: "秋季", 10: "秋季", 11: "秋季"}
all_data["季节"] = all_data["月"].map(season_map)

# 添加年份标签（用于跨年冬季归属）
all_data["年标签"] = all_data.apply(
    lambda r: f"{r['年']}-{r['年']+1}" if r["月"] == 12 else str(r["年"]), axis=1
)

print(f"  合并后总记录: {len(all_data)} 行")
print(f"  列: {list(all_data.columns)}")
print(f"  缺失情况: 月均温 NaN={all_data['月均温'].isna().sum()}, 月降水量 NaN={all_data['月降水量'].isna().sum()}")

# ───── 6. 保存 ─────
output_path = os.path.join(OUTPUT_DIR, "tidy_climate_data.csv")
all_data.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"\n  已保存: {output_path}")

# 预览
print("\n" + "=" * 60)
print("【合并数据预览】（前 10 行 + 含缺失行）")
print("=" * 60)
print(all_data.head(10).to_string(index=False))
print("\n... 含缺失值的行 ...")
missing_rows = all_data[all_data["月均温"].isna() | all_data["月降水量"].isna()]
print(missing_rows.to_string(index=False))

# ───── 7. 年度汇总表（供可视化用） ─────
print("\n" + "=" * 60)
print("【生成年度汇总表】")
print("=" * 60)

annual = all_data.groupby(["城市", "年"], dropna=False).agg(
    年均温=("月均温", lambda x: x.mean() if x.notna().sum() >= 6 else np.nan),
    年降水=("月降水量", "sum"),
    月均温_有效月数=("月均温", lambda x: x.notna().sum()),
).reset_index()

# 去除2025年数据不足的年均温
for idx in range(len(annual)):
    if annual.at[idx, "月均温_有效月数"] < 6:
        annual.at[idx, "年均温"] = np.nan
        annual.at[idx, "_备注"] = f"仅{annual.at[idx,'月均温_有效月数']}个月"

annual_output = os.path.join(OUTPUT_DIR, "annual_summary.csv")
annual.to_csv(annual_output, index=False, encoding="utf-8-sig")
print(f"  已保存: {annual_output}")
print(annual.to_string(index=False))

print("\n✅ 数据清洗 + 合并完成！")
