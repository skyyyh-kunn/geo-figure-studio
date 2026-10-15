# tests/test_geo_style.py
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_style"))
import geo_style


def test_pick_font_returns_first_available():
    installed = {"SimSun", "SimHei"}
    assert geo_style.pick_font(["Source Han Serif SC", "SimSun", "SimHei"], installed) == "SimSun"


def test_pick_font_returns_none_when_none_available():
    assert geo_style.pick_font(["Nope AA", "Also Nope"], {"SimSun"}) is None


def test_available_fonts_returns_nonempty_set():
    fonts = geo_style.available_fonts()
    assert isinstance(fonts, set)
    assert len(fonts) > 0


def test_apply_style_sets_fonts_and_fonttype():
    from matplotlib import rcParams
    info = geo_style.apply_style(cjk="SimSun", latin="Arial")
    assert rcParams["pdf.fonttype"] == 42
    assert rcParams["ps.fonttype"] == 42
    assert rcParams["axes.unicode_minus"] is False
    assert info["cjk"] == "SimSun"
    assert info["latin"] == "Arial"


def test_apply_style_warns_when_preferred_cjk_missing():
    """思源宋体不可用时必须降级并告警，绝不静默出方框图。"""
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        info = geo_style.apply_style()
    assert info["cjk"] != "Source Han Serif SC" or "Source Han Serif SC" in info["installed"]
    msgs = " ".join(str(x.message) for x in w)
    if "Source Han Serif SC" not in info["installed"]:
        assert "降级" in msgs, "字体降级时没有告警"
        assert info["cjk"] in geo_style.CJK_CANDIDATES


def test_apply_style_uses_dejavu_and_warns_when_no_cjk_at_all(monkeypatch):
    monkeypatch.setattr(geo_style, "available_fonts", lambda: {"Arial"})
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        info = geo_style.apply_style()
    assert info["cjk"] == "DejaVu Sans"
    assert any("方框" in str(x.message) for x in w)


def test_save_figure_exact_size_produces_target_mm(tmp_path):
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(90, 60))
    ax = fig.add_subplot(111)
    ax.plot([1, 2], [1, 2])
    paths = geo_style.save_figure(fig, tmp_path, stem="t", formats=("png",),
                                  dpi=300, exact=True)
    plt.close(fig)
    from PIL import Image
    im = Image.open(paths[0])
    assert abs(im.width / im.info["dpi"][0] * 25.4 - 90) < 0.6


def test_save_figure_returns_one_path_per_format(tmp_path):
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(90, 60))
    fig.add_subplot(111).plot([1, 2], [1, 2])
    paths = geo_style.save_figure(fig, tmp_path, stem="t",
                                  formats=("pdf", "png"), dpi=300)
    plt.close(fig)
    assert [p.suffix for p in paths] == [".pdf", ".png"]
    assert all(p.exists() for p in paths)


def test_save_figure_default_formats_does_not_crash(tmp_path):
    """F1 回归：默认三种格式（含 tif）都须成功写出，metadata 不得对 tif 崩溃。"""
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(90, 60))
    fig.add_subplot(111).plot([1, 2], [1, 2])
    paths = geo_style.save_figure(fig, tmp_path, stem="t")  # 默认 pdf/tif/png
    plt.close(fig)
    assert [p.suffix for p in paths] == [".pdf", ".tif", ".png"]
    assert all(p.exists() and p.stat().st_size > 0 for p in paths)


def test_classify_make_cmap_norm_yields_k_distinct_colors():
    """F2 回归：classify(k) + make_cmap(k) + norm 必须产生 k 个互异色级，
    不得因断点少一条边而静默丢掉一级颜色。"""
    import numpy as np
    v = np.random.default_rng(0).normal(0.5, 0.15, 400)
    for method in ("jenks", "quantile", "equal"):
        bins = geo_style.classify(v, method, k=5)
        cmap = geo_style.make_cmap("YlGn", k=5)
        norm = geo_style.norm_from_bins(bins, cmap)
        idx = np.clip(np.asarray(norm(v), dtype=int), 0, cmap.N - 1)
        assert len(np.unique(idx)) == 5, f"{method} 只渲染出 {len(np.unique(idx))} 级"


def test_classify_std_ignores_k():
    """F4：std 分级返回数据自定的边，不理会 k。"""
    import numpy as np
    v = np.random.default_rng(1).normal(0.5, 0.15, 300)
    a = geo_style.classify(v, method="std", k=2)
    b = geo_style.classify(v, method="std", k=8)
    assert np.array_equal(a, b)
    assert np.all(np.diff(a) > 0)


def test_apply_style_renders_cjk_without_missing_glyphs():
    """R10/R15 回归：中文必须真正可渲染，不得因字体族被泛型别名吞掉而全部出方框。

    以 matplotlib 的缺字告警作为方框的机器可检替代——无需人眼确认。
    """
    import warnings
    import matplotlib.pyplot as plt
    info = geo_style.apply_style()
    if info["cjk"] == "DejaVu Sans":
        pytest.skip("本机无中文字体；该情形已由 test_apply_style_uses_dejavu_... 覆盖")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fig = plt.figure(figsize=geo_style.mm_to_inch(60, 20))
        fig.text(0.1, 0.5, "中文标题样式")
        fig.canvas.draw()
        plt.close(fig)
    missing = [str(x.message) for x in w if "missing from font" in str(x.message)]
    assert not missing, f"中文缺字（将渲染为方框）: {missing[:3]}"


def test_classify_returns_k_plus_one_edges():
    """k 类方法返回 k+1 条边（数据最小值 + k 个上界），供 BoundaryNorm 直接使用。"""
    import numpy as np
    bins = geo_style.classify(np.arange(100, dtype=float), method="quantile", k=5)
    assert len(bins) == 6
    assert bins[0] == 0.0          # 首边 == 数据最小值
    assert np.all(np.diff(bins) > 0)


def test_classify_ignores_nan_and_inf():
    import numpy as np
    v = np.array([1.0, 2.0, np.nan, 3.0, np.inf, 4.0, 5.0, -np.inf, np.nan, 6.0])
    bins = geo_style.classify(v, method="quantile", k=4)
    assert len(bins) == 5
    assert np.all(np.isfinite(bins))


def test_make_cmap_returns_discrete_colormap():
    cmap = geo_style.make_cmap("YlGn", k=5)
    assert cmap.N == 5


def test_norm_from_bins_maps_into_range():
    import numpy as np
    from matplotlib.colors import Normalize
    bins = np.array([0.0, 1.0, 2.0, 3.0])
    cmap = geo_style.make_cmap("YlGn", k=3)
    norm = geo_style.norm_from_bins(bins, cmap)
    assert isinstance(norm, Normalize)
    assert norm(bins[2]) == 2


def test_add_north_arrow_creates_annotation():
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(90, 90))
    ax = fig.add_subplot(111)
    before = len(ax.texts)
    geo_style.add_north_arrow(ax)
    # 箭头由 annotate 绘制、箭头下方的 "N" 由 ax.text 绘制，故新增两个 Text 艺术家
    assert len(ax.texts) == before + 2
    assert any(getattr(t, "arrow_patch", None) is not None for t in ax.texts)
    assert any(t.get_text() == "N" for t in ax.texts)
    plt.close(fig)


def test_add_legend_default_call_collects_handles_from_axes():
    """默认参数调用不得崩：句柄由 matplotlib 从 axes 自动收集。"""
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(90, 60))
    ax = fig.add_subplot(111)
    ax.plot([1, 2], [1, 2], label="样线")
    leg = geo_style.add_legend(ax)
    assert [t.get_text() for t in leg.get_texts()] == ["样线"]
    plt.close(fig)


def test_add_legend_handles_only_uses_auto_labels():
    """F3 回归：只给 handles 时，标签须由句柄自带的 label 自动填充。"""
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(90, 60))
    ax = fig.add_subplot(111)
    line, = ax.plot([1, 2], [1, 2], label="样线")
    leg = geo_style.add_legend(ax, handles=[line])
    assert [t.get_text() for t in leg.get_texts()] == ["样线"]
    plt.close(fig)


def test_add_inset_returns_axes_inside_parent():
    import matplotlib.pyplot as plt
    geo_style.apply_style(cjk="SimSun", latin="Arial")
    fig = plt.figure(figsize=geo_style.mm_to_inch(180, 120))
    ax = fig.add_subplot(111)
    ins = geo_style.add_inset(ax, bounds=(0.6, 0.6, 0.35, 0.35))
    assert ins is not ax
    assert ins.get_position().x0 > ax.get_position().x0
    plt.close(fig)


# --- R9：字体降级链必须字重感知（只有展示字重的族不得充当正文） ---

class _FakeFace:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


def test_body_weight_families_excludes_heavy_only_family():
    entries = [_FakeFace("Heavy Only", 900), _FakeFace("Normal Face", 400),
               _FakeFace("Bold Face", 700)]
    fams = geo_style.body_weight_families(entries)
    assert "Normal Face" in fams
    assert "Heavy Only" not in fams
    assert "Bold Face" not in fams


def test_body_weight_families_default_reads_real_font_table():
    fams = geo_style.body_weight_families()
    assert isinstance(fams, set)
    assert len(fams) > 0


def test_pick_body_font_skips_display_weight_only_candidate():
    got, rejected = geo_style.pick_body_font(
        ("Heavy Only", "SimSun"), installed={"Heavy Only", "SimSun"},
        body={"SimSun"})
    assert got == "SimSun"
    assert rejected == "Heavy Only"


def test_pick_body_font_reports_rejected_when_all_are_display_weight():
    got, rejected = geo_style.pick_body_font(
        ("Heavy Only",), installed={"Heavy Only"}, body=set())
    assert got is None
    assert rejected == "Heavy Only"


def test_apply_style_warns_when_preferred_is_display_weight_only(monkeypatch):
    """F5/R9：首选族只有展示字重时，降级告警须点明「展示字重」这一原因。"""
    import warnings
    monkeypatch.setattr(geo_style, "available_fonts",
                        lambda: {"Source Han Serif SC", "SimSun", "Arial"})
    # 本机真实情况：思源宋体只有 900 字重，不在正文字重集里
    monkeypatch.setattr(geo_style, "body_weight_families",
                        lambda entries=None, body=geo_style.BODY_WEIGHT_RANGE: {"SimSun"})
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        info = geo_style.apply_style()
    assert info["cjk"] == "SimSun"
    assert any("展示字重" in str(x.message) for x in w)


# --- R13：默认分支回退到真实字体表（installed=None / body=None） ---

def test_pick_font_falls_back_to_real_font_table_when_installed_is_none():
    got = geo_style.pick_font(geo_style.CJK_CANDIDATES)
    assert got in geo_style.CJK_CANDIDATES


def test_pick_body_font_falls_back_to_real_font_table_by_default():
    got, _rejected = geo_style.pick_body_font(geo_style.CJK_CANDIDATES)
    assert got in geo_style.CJK_CANDIDATES
