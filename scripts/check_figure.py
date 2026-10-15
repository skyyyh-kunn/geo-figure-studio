#!/usr/bin/env python
"""geo-figure-studio · 成图质检。

三级结论：不合规（必须修）/ 疑似（需人眼确认）/ 通过。
如实声明能力边界：文本溢出只能启发式估算，配色美观度无法自动判断。
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_style"))
import geo_style as g  # noqa: E402

BAD, WARN, OK = "不合规", "疑似", "通过"
TOL_MM = 0.6


@dataclass
class Issue:
    level: str
    message: str

    def __str__(self):
        return f"[{self.level}] {self.message}"


# ────────────────────────────── 位图与 PDF

def check_raster(path, width_mm, dpi, height_mm=None, tol_mm=TOL_MM):
    """校验位图的 DPI 与物理尺寸。"""
    from PIL import Image

    path = Path(path)
    issues = []
    with Image.open(path) as im:
        got_dpi = im.info.get("dpi")
        w_px, h_px = im.size
        mode = im.mode

    if not got_dpi or not got_dpi[0]:
        issues.append(Issue(BAD, f"{path.name}: 未写入 DPI 元数据，出版社无法判断尺寸"))
        return issues

    got = float(got_dpi[0])
    if abs(got - dpi) > 1:
        issues.append(Issue(BAD, f"{path.name}: DPI={got:.0f}，应为 {dpi}"))

    real_w = w_px / got * 25.4
    if abs(real_w - width_mm) > tol_mm:
        issues.append(Issue(BAD, f"{path.name}: 宽度 {real_w:.2f}mm，应为 {width_mm}mm "
                                 f"（偏差 {real_w - width_mm:+.2f}mm）"))
    if height_mm is not None:
        real_h = h_px / got * 25.4
        if abs(real_h - height_mm) > tol_mm:
            issues.append(Issue(BAD, f"{path.name}: 高度 {real_h:.2f}mm，应为 {height_mm}mm"))

    if mode not in ("RGB", "RGBA", "L", "1", "P"):
        issues.append(Issue(WARN, f"{path.name}: 色彩模式 {mode}，投稿前确认是否需 RGB/CMYK"))
    return issues


def check_pdf(path, width_mm, height_mm=None, tol_mm=TOL_MM):
    """校验 PDF 的页面尺寸与字体嵌入（Type 3 会被部分出版社拒收）。"""
    from pypdf import PdfReader

    path = Path(path)
    issues = []
    reader = PdfReader(str(path))
    page = reader.pages[0]
    w_pt = float(page.mediabox.width)
    h_pt = float(page.mediabox.height)
    real_w = w_pt / 72 * 25.4
    if abs(real_w - width_mm) > tol_mm:
        issues.append(Issue(BAD, f"{path.name}: 页面宽度 {real_w:.2f}mm，应为 {width_mm}mm"))
    if height_mm is not None:
        real_h = h_pt / 72 * 25.4
        if abs(real_h - height_mm) > tol_mm:
            issues.append(Issue(BAD, f"{path.name}: 页面高度 {real_h:.2f}mm，应为 {height_mm}mm"))

    type3, not_embedded = set(), set()
    for pg in reader.pages:
        res = pg.get("/Resources")
        if res is None:
            continue
        fonts = res.get("/Font")
        if fonts is None:
            continue
        for key in fonts:
            fo = fonts[key].get_object()
            base = str(fo.get("/BaseFont", key))
            st = fo.get("/Subtype")
            if str(st) == "/Type3":
                type3.add(base)
                continue
            desc = fo.get("/FontDescriptor")
            if desc is None and "/DescendantFonts" in fo:
                df = fo["/DescendantFonts"][0].get_object()
                desc = df.get("/FontDescriptor")
            if desc is None:
                continue
            d = desc.get_object()
            if not any(k in d for k in ("/FontFile", "/FontFile2", "/FontFile3")):
                not_embedded.add(base)

    if type3:
        issues.append(Issue(BAD, f"{path.name}: 含 Type 3 字体 {sorted(type3)}；"
                                 f"出版社常拒收，请设 rcParams['pdf.fonttype']=42 后重出"))
    if not_embedded:
        issues.append(Issue(BAD, f"{path.name}: 字体未嵌入 {sorted(not_embedded)}"))
    return issues


# ────────────────────────────── 色盲可区分性

# Machado et al. 2009 生理模型，severity=1.0，作用在**线性 sRGB** 上。
# （brief 原给的 Viénot/Brettel 矩阵是 LMS 空间投影矩阵，直接作用在线性 RGB
# 会把纯绿映成黑色——纯红/纯绿在色盲下未显著收敛，见 test_simulate_colorblind_...。）
_CB_MATRICES = {
    "protanopia": np.array([[0.152286, 1.052583, -0.204868],
                            [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968],
                              [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
}


def _srgb_to_linear(rgb):
    rgb = np.asarray(rgb, dtype=float)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(rgb):
    rgb = np.clip(np.asarray(rgb, dtype=float), 0.0, 1.0)
    return np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - 0.055)


def _linear_to_lab(rgb_lin):
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = rgb_lin @ m.T
    white = np.array([0.95047, 1.0, 1.08883])
    t = xyz / white
    eps, kappa = 216 / 24389, 24389 / 27
    f = np.where(t > eps, np.cbrt(t), (kappa * t + 16) / 116)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


def simulate_colorblind(rgb, kind="deuteranopia"):
    """把 sRGB 颜色（0-1）模拟为指定色盲视觉。"""
    return _linear_to_srgb(_srgb_to_linear(rgb) @ _CB_MATRICES[kind].T)


def _level_colors(cmap_name, k):
    if cmap_name == "tol_muted":
        base = g.TOL_MUTED
        idx = np.linspace(0, len(base) - 1, k).round().astype(int)
        return np.array([[int(base[i][1:3], 16), int(base[i][3:5], 16),
                          int(base[i][5:7], 16)] for i in idx]) / 255.0
    cmap = g.make_cmap(cmap_name, k)
    return np.array([cmap(i)[:3] for i in range(k)])


def check_colorblind(cmap_name, k, min_delta_e=10.0):
    """对相邻色级做红绿色盲模拟，报出最小 ΔE。"""
    colors = _level_colors(cmap_name, k)
    issues = []
    for kind in ("deuteranopia", "protanopia"):
        sim = simulate_colorblind(colors, kind)
        lab = _linear_to_lab(_srgb_to_linear(sim))
        d = np.linalg.norm(np.diff(lab, axis=0), axis=1)
        worst = float(d.min())
        if worst < min_delta_e:
            level = BAD if worst < min_delta_e / 2 else WARN
            issues.append(Issue(
                level,
                f"色带 {cmap_name} 在{k} 级下，{kind} 视觉中相邻级最小 ΔE={worst:.1f}"
                f"（阈值 {min_delta_e}），分级可能不可区分"))
    return issues


# ────────────────────────────── 数据指纹与要素齐全性

def _sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def check_fingerprint(params):
    """核验 params.yaml 记录的数据文件是否仍与建档时一致。"""
    issues = []
    for rec in params.get("data_fingerprint") or []:
        p = Path(rec.get("path", ""))
        if not p.is_file():
            issues.append(Issue(BAD, f"数据文件不存在：{p} —— 复现会失败"))
            continue
        size = p.stat().st_size
        if rec.get("bytes") and size != rec["bytes"]:
            issues.append(Issue(BAD, f"数据文件大小变了：{p.name} "
                                     f"{size}≠{rec['bytes']} —— 可能被替换或损坏"))
        if rec.get("sha256") and len(str(rec["sha256"])) == 64:
            got = _sha256(p)
            if got != rec["sha256"]:
                issues.append(Issue(BAD, f"数据文件校验和不匹配：{p.name} —— "
                                         f"内容已变，历史版本无法复现"))
    return issues


_ELEMENT_CALLS = {
    "scalebar": (g.add_scalebar.__name__, "比例尺"),
    "north_arrow": (g.add_north_arrow.__name__, "指北针"),
    "gridlines": (g.add_gridlines.__name__, "经纬网"),
    "legend": (g.add_legend.__name__, "图例"),
    "inset": (g.add_inset.__name__, "放大框"),
}


def check_elements(params, script_path):
    """检查 params 声明的地图要素在出图脚本里是否真的被调用。"""
    issues = []
    src = Path(script_path).read_text(encoding="utf-8", errors="replace")
    me = (params.get("refine") or {}).get("map_elements") or {}
    for key, flag in me.items():
        if not flag or key not in _ELEMENT_CALLS:
            continue
        fname, cn = _ELEMENT_CALLS[key]
        if fname not in src:
            issues.append(Issue(BAD, f"params 声明了{cn}（{key}=true），"
                                     f"但 make_fig.py 中未见 {fname}() 调用"))
    if (params.get("refine") or {}).get("palette", {}).get("colorblind_checked") is False:
        issues.append(Issue(WARN, "色带尚未人工确认色盲友好（palette.colorblind_checked=false）"))
    return issues


def check_text_overflow(path):
    """启发式：仅报疑似，绝不判定为错误。"""
    return [Issue(WARN, f"{Path(path).name}: 文本是否溢出/重叠无法自动判定，请人眼确认")]


# ────────────────────────────── 主流程

def run(figure_dir, verbose=True):
    """跑完整质检，返回 (总体结论, 问题列表)。"""
    d = Path(figure_dir).resolve()
    params = yaml.safe_load((d / "params.yaml").read_text(encoding="utf-8"))
    ver = params["refine"]["output"]["version"]
    outdir = d / "output" / f"v{ver}"
    width_mm = params["gate"]["size"]["width_mm"]
    height_mm = params["gate"]["size"].get("height_mm")
    dpi = params["refine"]["output"].get("dpi", 600)

    issues = []
    if not outdir.is_dir():
        issues.append(Issue(BAD, f"版本目录不存在：{outdir} —— 请先跑 make_fig.py"))
    else:
        for f in sorted(outdir.iterdir()):
            if f.suffix.lower() in (".png", ".tif", ".tiff"):
                issues += check_raster(f, width_mm, dpi, height_mm)
                issues += check_text_overflow(f)
            elif f.suffix.lower() == ".pdf":
                issues += check_pdf(f, width_mm, height_mm)

    pal = params["refine"].get("palette") or {}
    if pal.get("cmap"):
        k = pal.get("k") or len(pal.get("bins") or []) or 5
        issues += check_colorblind(pal["cmap"], int(k))

    issues += check_fingerprint(params)
    issues += check_elements(params, d / "make_fig.py")

    level = BAD if any(i.level == BAD for i in issues) else (
        WARN if any(i.level == WARN for i in issues) else OK)

    if verbose:
        print(f"== 质检 {d.name} · v{ver} ==")
        if not issues:
            print("  无问题")
        for i in issues:
            print("  " + str(i))
        print(f"== 结论：{level} ==")
    return level, issues


def main(argv=None):
    ap = argparse.ArgumentParser(description="geo-figure-studio 成图质检")
    ap.add_argument("--figure", required=True)
    a = ap.parse_args(argv)
    level, _ = run(a.figure)
    return 0 if level == OK else 1


if __name__ == "__main__":
    sys.exit(main())
