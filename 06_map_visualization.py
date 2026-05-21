#!/usr/bin/env python3
"""
三城地理标注地图: 兰州/西安/西宁 + ERA5 数据覆盖示意
优先使用 cartopy，不可用时降级为 folium 或纯 matplotlib
"""

import warnings
warnings.filterwarnings("ignore")

CITIES = {
    "兰州": {"lat": 36.06, "lon": 103.83, "alt": 1520},
    "西安": {"lat": 34.27, "lon": 108.93, "alt": 400},
    "西宁": {"lat": 36.62, "lon": 101.78, "alt": 2261},
}

COLORS = {"兰州": "#e74c3c", "西安": "#3498db", "西宁": "#2ecc71"}

# ───── 方法1: cartopy ─────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    fig, ax = plt.subplots(figsize=(10, 8),
                           subplot_kw={"projection": ccrs.PlateCarree()})

    # 设置地图范围 (三城周边)
    ax.set_extent([99, 112, 32, 39], crs=ccrs.PlateCarree())

    # 添加地图要素
    ax.add_feature(cfeature.LAND, facecolor="#f5f5dc", alpha=0.8)
    ax.add_feature(cfeature.OCEAN, facecolor="#c6e2ff", alpha=0.3)
    ax.add_feature(cfeature.LAKES, facecolor="#c6e2ff", alpha=0.6)
    ax.add_feature(cfeature.RIVERS, edgecolor="#87ceeb", linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, edgecolor="gray", linewidth=0.5, linestyle="--")
    ax.add_feature(cfeature.COASTLINE, edgecolor="gray", linewidth=0.5)

    # 添加省份边界
    try:
        provinces = cfeature.NaturalEarthFeature(
            "cultural", "admin_1_states_provinces_lines",
            "10m", edgecolor="gray", facecolor="none", linewidth=0.3)
        ax.add_feature(provinces)
    except Exception:
        pass

    # 标注城市
    for name, info in CITIES.items():
        ax.plot(info["lon"], info["lat"], "o", color=COLORS[name],
                markersize=12, markeredgecolor="white", markeredgewidth=1.5,
                transform=ccrs.PlateCarree(), zorder=5)
        ax.annotate(f"{name}\n{info['alt']}m",
                    (info["lon"], info["lat"]),
                    xytext=(8, 8), textcoords="offset points",
                    fontsize=10, fontweight="bold", color=COLORS[name],
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor=COLORS[name], alpha=0.85),
                    transform=ccrs.PlateCarree())

    # 网格线
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="gray",
                      alpha=0.5, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 8}
    gl.ylabel_style = {"size": 8}

    ax.set_title("图7: 兰州-西安-西宁 地理位置 (ERA5 数据覆盖区域)",
                 fontweight="bold", fontsize=13, pad=15)

    fig.tight_layout()
    fig.savefig("fig7_三城地图.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("✅ fig7_三城地图.png (cartopy) 已保存")

except ImportError:
    # ───── 方法2: folium (交互式 HTML) ─────
    try:
        import folium

        # 计算中心点
        center_lat = sum(c["lat"] for c in CITIES.values()) / 3
        center_lon = sum(c["lon"] for c in CITIES.values()) / 3

        m = folium.Map(location=[center_lat, center_lon],
                       zoom_start=6,
                       tiles="CartoDB positron")

        for name, info in CITIES.items():
            folium.CircleMarker(
                location=[info["lat"], info["lon"]],
                radius=10,
                popup=folium.Popup(
                    f"<b>{name}</b><br>海拔: {info['alt']}m",
                    max_width=200),
                color=COLORS[name],
                fill=True,
                fill_color=COLORS[name],
                fill_opacity=0.8,
                weight=2,
                tooltip=name,
            ).add_to(m)

            # 标注文字
            folium.map.Marker(
                [info["lat"] + 0.15, info["lon"]],
                icon=folium.DivIcon(
                    html=f'<div style="font-size:11pt;font-weight:bold;'
                         f'color:{COLORS[name]};text-shadow:1px 1px 2px white;'
                         f'white-space:nowrap">{name}<br>'
                         f'<span style="font-size:8pt">{info["alt"]}m</span></div>'
                ),
            ).add_to(m)

        m.save("fig7_三城地图.html")
        print("✅ fig7_三城地图.html (folium 交互地图) 已保存")

    except ImportError:
        # ───── 方法3: 纯 matplotlib scatter ─────
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=(8, 8))

        # 简化的经纬度散点图
        for name, info in CITIES.items():
            ax.scatter(info["lon"], info["lat"], s=200, c=COLORS[name],
                       edgecolors="white", linewidth=1.5, zorder=5)
            ax.annotate(f"{name}\n{info['alt']}m",
                        (info["lon"], info["lat"]),
                        xytext=(10, 10), textcoords="offset points",
                        fontsize=11, fontweight="bold", color=COLORS[name],
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                  edgecolor=COLORS[name], alpha=0.85))

        # 连接线表示城市间关系
        city_list = list(CITIES.keys())
        for i in range(len(city_list)):
            for j in range(i + 1, len(city_list)):
                c1, c2 = city_list[i], city_list[j]
                ax.plot([CITIES[c1]["lon"], CITIES[c2]["lon"]],
                        [CITIES[c1]["lat"], CITIES[c2]["lat"]],
                        "gray", lw=0.5, ls="--", alpha=0.4, zorder=1)

        ax.set_xlabel("经度 (°E)", fontsize=11)
        ax.set_ylabel("纬度 (°N)", fontsize=11)
        ax.set_title("图7: 兰州-西安-西宁 地理位置", fontweight="bold", fontsize=13)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig("fig7_三城地图.png", dpi=200)
        plt.close(fig)
        print("✅ fig7_三城地图.png (matplotlib 简化版) 已保存")
        print("   💡 安装 cartopy 可获得精美地图: pip install cartopy")
        print("   💡 安装 folium 可获得交互地图: pip install folium")
