import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "_style"))
import check_figure as C  # noqa: E402
import geo_style as g  # noqa: E402


def _make_png(path, width_mm, height_mm, dpi):
    import matplotlib.pyplot as plt
    g.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=g.mm_to_inch(width_mm, height_mm))
    fig.add_subplot(111).plot([1, 2], [1, 2])
    fig.savefig(path, dpi=dpi, bbox_inches=None)
    plt.close(fig)


def test_check_raster_passes_on_correct_size(tmp_path):
    p = tmp_path / "ok.png"
    _make_png(p, 90, 60, 300)
    issues = C.check_raster(p, width_mm=90, dpi=300)
    assert [i for i in issues if i.level == "不合规"] == []


def test_check_raster_flags_wrong_dpi(tmp_path):
    p = tmp_path / "bad.png"
    _make_png(p, 90, 60, 72)
    issues = C.check_raster(p, width_mm=90, dpi=300)
    assert any(i.level == "不合规" and "DPI" in i.message for i in issues)


def test_check_raster_flags_wrong_width(tmp_path):
    p = tmp_path / "narrow.png"
    _make_png(p, 60, 60, 300)
    issues = C.check_raster(p, width_mm=90, dpi=300)
    assert any(i.level == "不合规" and "宽度" in i.message for i in issues)


def test_check_pdf_flags_fonttype3(tmp_path):
    import matplotlib.pyplot as plt
    g.apply_style(cjk="SimSun", latin="Arial")
    from matplotlib import rcParams
    rcParams["pdf.fonttype"] = 3          # 故意做错
    fig = plt.figure(figsize=g.mm_to_inch(90, 60))
    fig.add_subplot(111).plot([1, 2], [1, 2])
    p = tmp_path / "type3.pdf"
    fig.savefig(p, bbox_inches=None)
    plt.close(fig)
    rcParams["pdf.fonttype"] = 42
    issues = C.check_pdf(p, width_mm=90)
    assert any(i.level == "不合规" and "Type 3" in i.message for i in issues)


def test_check_pdf_passes_on_good_file(tmp_path):
    import matplotlib.pyplot as plt
    g.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=g.mm_to_inch(90, 60))
    fig.add_subplot(111).plot([1, 2], [1, 2])
    p = tmp_path / "good.pdf"
    fig.savefig(p, bbox_inches=None, metadata={"Creator": "x"})
    plt.close(fig)
    issues = C.check_pdf(p, width_mm=90)
    assert [i for i in issues if i.level == "不合规"] == []


def test_check_colorblind_flags_low_distinguishability():
    issues = C.check_colorblind("Blues", k=20)
    assert issues
    assert all(isinstance(i, C.Issue) for i in issues)
    assert all(i.level in (C.BAD, C.WARN) for i in issues)


def test_simulate_colorblind_preserves_shape_and_range():
    rgb = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    sim = C.simulate_colorblind(rgb, "deuteranopia")
    assert sim.shape == rgb.shape
    assert np.all(sim >= 0) and np.all(sim <= 1)


def test_simulate_colorblind_makes_red_and_green_converge():
    """模拟器正确性的判据：红绿色盲下，纯红与纯绿必须显著靠近。"""
    rgb = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    normal = np.linalg.norm(np.diff(C._linear_to_lab(C._srgb_to_linear(rgb)), axis=0))
    sim = C.simulate_colorblind(rgb, "deuteranopia")
    blind = np.linalg.norm(np.diff(C._linear_to_lab(C._srgb_to_linear(sim)), axis=0))
    assert blind < normal * 0.6


def test_tol_muted_beats_single_hue_ramp_for_colorblind_safety():
    """定性色带应比单色渐变更能扛住色盲——这是阈值设定合理性的判据。"""
    def worst_delta_e(cmap, k):
        vals = []
        for i in C.check_colorblind(cmap, k):
            if "ΔE=" in i.message:
                vals.append(float(i.message.split("ΔE=")[1].split("（")[0]))
        return min(vals) if vals else 99.0

    assert worst_delta_e("tol_muted", 5) > worst_delta_e("Blues", 20)


def test_check_fingerprint_flags_missing_file(tmp_path):
    params = {"data_fingerprint": [
        {"path": str(tmp_path / "nope.tif"), "bytes": 1, "sha256": "x"}]}
    issues = C.check_fingerprint(params)
    assert any(i.level == "不合规" and "不存在" in i.message for i in issues)


def test_check_fingerprint_flags_changed_file(tmp_path):
    f = tmp_path / "d.bin"
    f.write_bytes(b"hello")
    params = {"data_fingerprint": [
        {"path": str(f), "bytes": 5,
         "sha256": "0" * 64}]}
    issues = C.check_fingerprint(params)
    assert any(i.level == "不合规" and "校验和" in i.message for i in issues)


def test_check_elements_flags_declared_but_uncalled(tmp_path):
    s = tmp_path / "make_fig.py"
    s.write_text("print('no components here')\n", encoding="utf-8")
    params = {"refine": {"map_elements": {"scalebar": True, "north_arrow": True}}}
    issues = C.check_elements(params, s)
    assert any(i.level == "不合规" and "比例尺" in i.message for i in issues)


def test_run_reports_overall_level(tmp_path):
    fig = tmp_path / "figures" / "2026-10-13_x"
    (fig / "output" / "v1").mkdir(parents=True)
    _make_png(fig / "output" / "v1" / "fig.png", 90, 60, 300)
    (fig / "params.yaml").write_text(
        "meta: {figure_id: x}\n"
        "gate: {size: {width_mm: 90, height_mm: 60, exact: true}}\n"
        "refine:\n  output: {version: 1, dpi: 300, formats: [png]}\n"
        "  palette: {cmap: tol_muted, k: 6}\n"
        "  map_elements: {}\n"
        "data_fingerprint: []\n", encoding="utf-8")
    (fig / "make_fig.py").write_text("pass\n", encoding="utf-8")
    level, issues = C.run(fig)
    assert level in ("不合规", "疑似", "通过")
