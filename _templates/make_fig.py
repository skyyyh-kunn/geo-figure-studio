"""由 geo-figure-studio 生成的出图脚本。

规则：本文件只负责「读 params.yaml → 计算 → 画 → 存」，不硬编码任何
可调参数。要改图请改 params.yaml。

图型分发：build_figure 按 gate.figure_type 调用对应实现。
已固化图型：05-terrain。其余图型在首次真实作图时按
references/figure-types/NN-*.md 实现，并固化回 _templates/make_fig.py。
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_style"))
import geo_style as g   # noqa: E402

HERE = Path(__file__).resolve().parent


def load_params(path=HERE / "params.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def masked(arr, nodata=None):
    """统一 nodata 处理：把 nodata 置为 NaN，避免被当成 0 参与均值/趋势。"""
    import numpy as np

    a = np.asarray(arr, dtype=float)
    if nodata is not None:
        a = np.where(a == nodata, np.nan, a)
    a = np.where(np.isfinite(a), a, np.nan)
    return np.ma.masked_invalid(a)


def build_figure(p, **data):
    """按 params 出图。按图型分发到对应实现，参数一律从 p 读取。"""
    ft = p["gate"]["figure_type"]
    if ft == "05-terrain":
        return build_terrain(p)
    return build_placeholder(p, ft)


def build_terrain(p):
    """05-terrain：DEM 分层设色 + 山体阴影。"""
    import matplotlib.pyplot as plt
    import numpy as np
    import rasterio

    g.apply_style()
    w = p["gate"]["size"]["width_mm"]
    h = p["gate"]["size"]["height_mm"]
    fig = plt.figure(figsize=g.mm_to_inch(w, h))
    ax = fig.add_subplot(111)

    # 1) 读 DEM：路径与 nodata 来自 params，不在代码里写死
    dem_path = p["gate"]["data_source"]["paths"][0]
    with rasterio.open(dem_path) as ds:
        dem = ds.read(1).astype("float64")
        nodata = ds.nodata
        transform = ds.transform
    dem = masked(dem, nodata)

    # 2) 山体阴影（梯度法；方位角/高度角取顶刊常用 315°/45°）
    dy, dx = np.gradient(np.ma.filled(dem, np.nan))
    az, alt = np.deg2rad(315.0), np.deg2rad(45.0)
    slope = np.pi / 2 - np.arctan(np.hypot(dx, dy))
    aspect = np.arctan2(-dx, dy)
    hill = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
    hill = (hill - np.nanmin(hill)) / (np.nanmax(hill) - np.nanmin(hill) + 1e-12)

    # 3) 分层设色：分级方法、级数、色带来自 params
    rp = p["refine"]["palette"]
    bins = list(rp["bins"]) or g.classify(dem, rp["classify_method"], rp["k"])
    cmap = g.make_cmap(rp["cmap"], len(bins) - 1)
    norm = g.norm_from_bins(bins, cmap)

    # 4) 画图：extent 由栅格仿射变换算，单位 = CRS 单位（米）
    ny, nx = dem.shape
    extent = (transform.c, transform.c + nx * transform.a,
              transform.f + ny * transform.e, transform.f)
    ax.imshow(dem, cmap=cmap, norm=norm, extent=extent,
              aspect="equal", interpolation="nearest")
    ax.imshow(hill, cmap="gray", extent=extent, aspect="equal",
              alpha=0.4, interpolation="nearest", vmin=0, vmax=1)
    cb = fig.colorbar(ax.images[0], ax=ax, fraction=0.04, pad=0.02)
    cb.ax.tick_params(labelsize=6)
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")

    _add_map_elements(ax, p)
    return fig


def build_placeholder(p, ft):
    """未固化图型：画出占位提示，指引实现路径，而非假装成功。"""
    import matplotlib.pyplot as plt

    g.apply_style()
    w = p["gate"]["size"]["width_mm"]
    h = p["gate"]["size"]["height_mm"]
    fig = plt.figure(figsize=g.mm_to_inch(w, h))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    ax.text(
        0.5, 0.5,
        f"图型 {ft} 尚未固化渲染代码\n"
        f"请按 references/figure-types/{ft}.md 实现后固化回 _templates/make_fig.py",
        ha="center", va="center", fontsize=8, wrap=True,
    )
    return fig


def _add_map_elements(ax, p):
    """按 params 追加比例尺 / 指北针 / 标题。"""
    me = p["refine"]["map_elements"]
    if me.get("north_arrow"):
        g.add_north_arrow(ax)
    if me.get("scalebar"):
        g.add_scalebar(ax, dx=1.0, units=me.get("scalebar_units", "m"))
    if p["gate"]["narrative"]:
        ax.set_title(p["gate"]["narrative"], fontsize=8)


def main():
    p = load_params()
    out = HERE / "output" / f"v{p['refine']['output']['version']}"
    fig = build_figure(p)
    paths = g.save_figure(
        fig, out, stem=p["meta"]["figure_id"] or "fig",
        formats=tuple(p["refine"]["output"]["formats"]),
        dpi=p["refine"]["output"]["dpi"],
        exact=p["gate"]["size"].get("exact", True),
    )
    for x in paths:
        print("写出:", x)


if __name__ == "__main__":
    main()
