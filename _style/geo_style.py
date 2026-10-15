# _style/geo_style.py
"""geo-figure-studio 统一样式与制图组件库。

所有出图脚本必须 import 本模块，不得自行硬编码字体、字号、DPI、色带。
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.colors import BoundaryNorm, ListedColormap

CJK_CANDIDATES = (
    "Source Han Serif SC",   # 思源宋体（首选，需自行安装）
    "Noto Serif SC",
    "SimSun",                # 宋体（Windows 自带，中文核心期刊正文标准）
    "Microsoft YaHei",
    "SimHei",
)
LATIN_CANDIDATES = ("Arial", "Helvetica", "DejaVu Sans")

# 正文字重区间。只有展示字重（Heavy/Black 等 900）的字体族不得充当正文：
# 它会让通篇中文呈现为粗体，且 400 与 700 的请求解析到同一字面，粗体与正文不可区分。
BODY_WEIGHT_RANGE = (300, 500)


def available_fonts() -> set:
    """返回系统已安装字体名集合。"""
    return {f.name for f in font_manager.fontManager.ttflist}


def pick_font(candidates, installed=None):
    """按优先级返回第一个已安装字体名；全缺返回 None。"""
    installed = available_fonts() if installed is None else installed
    for name in candidates:
        if name in installed:
            return name
    return None


def body_weight_families(entries=None, body=BODY_WEIGHT_RANGE):
    """返回拥有正文字重（body 区间内）可用条目的字体族名集合。"""
    lo, hi = body
    if entries is None:
        entries = font_manager.fontManager.ttflist
    return {e.name for e in entries if lo <= getattr(e, "weight", 400) <= hi}


def pick_body_font(candidates, installed=None, body=None):
    """按优先级返回第一个既可安装、又有正文字重的候选族。

    返回 (选中族名 | None, 因只有展示字重而被跳过的首个族名 | None)。
    跳过是有意为之，调用方须据此告警，不得静默。
    """
    installed = available_fonts() if installed is None else installed
    body = body_weight_families() if body is None else body
    rejected = None
    for name in candidates:
        if name not in installed:
            continue
        if name in body:
            return name, rejected
        if rejected is None:
            rejected = name
    return None, rejected


BASE = {
    "font.size": 7,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "legend.fontsize": 7,
    "legend.frameon": False,
    "lines.linewidth": 0.9,
    "grid.linewidth": 0.4,
    "grid.alpha": 0.5,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": None,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.unicode_minus": False,
    "figure.dpi": 150,
}


def mm_to_inch(*mms):
    """毫米转英寸。单参数返回标量，多参数返回元组。"""
    vals = tuple(m / 25.4 for m in mms)
    return vals[0] if len(vals) == 1 else vals


def apply_style(cjk=None, latin=None, **overrides):
    """注入 Geo-Figures 统一样式。返回实际生效的字体与解析结果。

    字体缺失时自动沿候选链降级并告警，绝不静默失败。
    """
    installed = available_fonts()
    requested = cjk
    skipped = None
    if cjk is None:
        cjk, skipped = pick_body_font(CJK_CANDIDATES, installed)
    elif cjk not in installed:
        warnings.warn(f"指定的中文字体 {cjk} 未安装，中文可能渲染为方框",
                      RuntimeWarning, stacklevel=2)
    latin = latin or pick_font(LATIN_CANDIDATES, installed)
    if cjk is None:
        warnings.warn("未找到任何中文字体，中文将渲染为方框；请安装思源宋体或确认 SimSun 可用",
                      RuntimeWarning, stacklevel=2)
        cjk = "DejaVu Sans"
    elif requested is None and cjk != CJK_CANDIDATES[0]:
        why = (f"{skipped} 只有展示字重，正文会通篇加粗且粗体与正文不可区分"
               if skipped else f"{CJK_CANDIDATES[0]} 未安装")
        warnings.warn(f"中文降级为 {cjk}：{why}", RuntimeWarning, stacklevel=2)
    if latin is None:
        latin = "DejaVu Sans"

    rcParams.update(BASE)
    # font.family 必须是显式族列表：matplotlib 的逐字形回退只沿该列表走。
    # 若留成 "sans-serif" 这类泛型别名，它只解析到 font.sans-serif 中第一个命中的字体，
    # 于是拉丁字体排首位时，全部中文静默渲染为方框。
    rcParams["font.family"] = [latin, cjk, "DejaVu Sans"]
    rcParams["font.sans-serif"] = [latin, cjk, "DejaVu Sans"]
    rcParams["font.serif"] = [cjk, latin, "DejaVu Sans"]
    rcParams.update(overrides)
    return {"cjk": cjk, "latin": latin, "installed": installed}


def save_figure(fig, outdir, stem="fig", formats=("pdf", "tif", "png"),
                dpi=600, exact=True):
    """保存成图，返回产物路径列表。

    exact=True 时不做 bbox 裁切，保证输出物理尺寸 == figsize，满足期刊精确尺寸要求。
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fmt in formats:
        p = outdir / f"{stem}.{fmt}"
        kw = {}
        if fmt in ("png", "tif", "tiff", "jpg", "jpeg"):
            kw["dpi"] = dpi
        if fmt in ("tif", "tiff"):
            kw["pil_kwargs"] = {"compression": "tiff_lzw"}
        # metadata 仅 pdf/png/ps/eps 支持；svg 拒 Producer 键，tif/jpg 直接 not supported。
        if fmt in ("pdf", "png", "ps", "eps"):
            kw["metadata"] = {"Creator": "geo-figure-studio", "Producer": "geo-figure-studio"}
        fig.savefig(
            p,
            bbox_inches=None if exact else "tight",
            pad_inches=0 if exact else 0.02,
            transparent=False,
            **kw,
        )
        paths.append(p)
    return paths


# 顺序色带（单变量、由低到高）
PALETTES = {
    "sequential": {
        "绿-植被": "YlGn",
        "蓝-水体": "Blues",
        "棕-高程": "terrain",
        "橙-温度": "YlOrRd",
        "紫-通用": "viridis",
        "灰-通用": "Greys",
        "绿-通用": "BuGn",
    },
    "diverging": {
        "红蓝-距平": "RdYlBu_r",
        "棕绿-干湿": "BrBG",
        "红蓝-通用": "RdBu_r",
        "紫橙-通用": "PuOr",
    },
}

# Paul Tol muted — 10 色，色盲友好定性色带
TOL_MUTED = ["#332288", "#88CCEE", "#44AA99", "#117733", "#999933",
             "#DDCC77", "#CC6677", "#882255", "#AA4499", "#DDDDDD"]

_METHODS = ("jenks", "quantile", "equal", "std", "fisher")


def classify(values, method="jenks", k=5, max_sample=20000, seed=0):
    """对一维数据做分级，返回断点（bin edges）数组。

    k 类方法（jenks/quantile/equal/fisher）返回 k+1 条边（数据最小值 + k 个上界），
    供 norm_from_bins 直接构造 BoundaryNorm；std 忽略 k，返回数据自定的边。

    NaN 与 inf 被剔除；样本量超过 max_sample 时随机抽样后再分级。
    """
    import mapclassify

    v = np.asarray(values, dtype=float).ravel()
    v = v[np.isfinite(v)]
    if v.size == 0:
        raise ValueError("classify: 输入不含任何有效值")
    if v.size > max_sample:
        v = np.random.default_rng(seed).choice(v, max_sample, replace=False)

    if method == "std":
        # StdMean 的 bins 本就是数据自定的边（均值为中心 ± n·σ），不理会 k。
        return np.asarray(mapclassify.StdMean(v).bins, dtype=float)
    elif method in ("jenks", "fisher"):
        cls = mapclassify.FisherJenks(v, k=k)
    elif method == "quantile":
        cls = mapclassify.Quantiles(v, k=k)
    elif method == "equal":
        cls = mapclassify.EqualInterval(v, k=k)
    else:
        raise ValueError(f"classify: 未知分级方法 {method!r}，可选 {_METHODS}")
    # mapclassify 的 .bins 是 k 个上界、缺下界；补上数据最小值得到 k+1 条边，
    # 与 norm_from_bins 的 BoundaryNorm「边比色多 1」约定一致。
    return np.concatenate([[v.min()], np.asarray(cls.bins, dtype=float)])


def make_cmap(name, k=None):
    """取色带；给 k 时返回 k 级离散色带，否则返回连续色带。"""
    if k is None:
        return plt.get_cmap(name)
    base = plt.get_cmap(name)
    colors = base(np.linspace(0.05, 0.95, k))
    return ListedColormap(colors, name=f"{name}_{k}")


def norm_from_bins(bins, cmap):
    """由断点与离散色带构造 BoundaryNorm。断点数应比色级数多 1。"""
    bins = np.asarray(bins, dtype=float)
    return BoundaryNorm(bins, ncolors=cmap.N, clip=True)


ARROW_COLOR = "#222222"


def add_scalebar(ax, dx=1.0, units="m", length=0.25, location="lower right",
                 label=None, fontsize=7):
    """加比例尺。dx 为数据坐标中 1 单位对应的实际长度（投影坐标系取 1.0）。"""
    from matplotlib_scalebar.scalebar import ScaleBar

    sb = ScaleBar(
        dx, units=units, dimension="si-length",
        length_fraction=length, location=location,
        frameon=False, color=ARROW_COLOR, box_alpha=0.0,
        label=label, font_properties={"size": fontsize},
        sep=3, pad=0.4,
    )
    ax.add_artist(sb)
    return sb


def add_north_arrow(ax, x=0.94, y=0.86, size=0.08, label="N", fontsize=8):
    """加指北针（纯 matplotlib，不依赖 cartopy）。"""
    ax.annotate(
        "", xy=(x, y + size), xytext=(x, y),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(facecolor=ARROW_COLOR, edgecolor=ARROW_COLOR,
                        width=1.2, headwidth=5.0, headlength=6.0),
        annotation_clip=False, zorder=20,
    )
    ax.text(x, y + size + 0.015, label, transform=ax.transAxes,
            ha="center", va="bottom", fontsize=fontsize, zorder=20)


def add_legend(ax, handles=None, labels=None, loc="lower left", ncol=1,
               fontsize=7, title=None, outside=False, **kw):
    """统一图例：无边框、小字号、紧凑间距。

    handles/labels 一律以关键字传入：matplotlib 的 legend() 把单个位置参数
    硬当标签列表，遇到 Artist 就抛 TypeError；关键字形式才走其
    「handles 给则补标签 / labels 给则补句柄 / 全 None 则自动收集」分支。
    """
    if outside:
        anchor = (1.02, 1.0) if loc == "upper left" else (1.02, 0.0)
        leg = ax.legend(handles=handles, labels=labels, loc="upper left",
                        bbox_to_anchor=anchor, ncol=ncol, fontsize=fontsize,
                        title=title, frameon=False, borderaxespad=0.2, **kw)
    else:
        leg = ax.legend(handles=handles, labels=labels, loc=loc, ncol=ncol,
                        fontsize=fontsize, title=title, frameon=False,
                        borderaxespad=0.3, **kw)
    if leg.get_title() is not None:
        leg.get_title().set_fontsize(fontsize)
    return leg


def add_gridlines(ax, xs=None, ys=None, fontsize=6, **kw):
    """加经纬网。仅对 cartopy GeoAxes 生效。"""
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="#999999",
                      alpha=0.6, linestyle="--", **kw)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": fontsize}
    gl.ylabel_style = {"size": fontsize}
    return gl


def add_inset(ax, bounds=(0.62, 0.62, 0.34, 0.34), **kw):
    """在父图内嵌放大框。bounds=(x0, y0, w, h)，axes fraction 坐标。"""
    ins = ax.inset_axes(list(bounds), **kw)
    return ins


def connect_inset(ax, inset, xy_from, xy_to, color=ARROW_COLOR, lw=0.5,
                  coords="axes fraction"):
    """画放大框与源区的连线。"""
    from matplotlib.patches import ConnectionPatch

    con = ConnectionPatch(
        xyA=xy_from, coordsA=coords, axesA=ax,
        xyB=xy_to, coordsB=coords, axesB=inset,
        color=color, linewidth=lw, zorder=19,
    )
    inset.add_artist(con)
    return con
