# tests/test_templates.py
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]

# 模板在 _templates/（深度 1）位置时，其自带的 parents[2] 路径指向仓库外，
# 故测试在此注入 _style，与 test_init_figure.py 注入 scripts 同一模式（见 R18）。
sys.path.insert(0, str(REPO / "_style"))


def _load_make_fig():
    spec = importlib.util.spec_from_file_location(
        "tpl_make_fig", REPO / "_templates" / "make_fig.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tpl_make_fig"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_masked_turns_nodata_into_nan():
    mf = _load_make_fig()
    arr = np.array([[1.0, 2.0, -9999.0], [4.0, -9999.0, 6.0]])
    out = mf.masked(arr, nodata=-9999.0)
    assert np.ma.isMaskedArray(out)
    assert out.mask[0, 2] and out.mask[1, 1]
    assert not out.mask[0, 0]


def test_masked_mean_excludes_nodata():
    """关键：镜像上 nodata 若被当成 0，均值会被拉低，图上出现假低值区。"""
    mf = _load_make_fig()
    arr = np.array([[0.8, 0.8, -9999.0], [0.8, 0.8, 0.8]])
    naive = float(np.mean(np.where(arr == -9999.0, 0.0, arr)))
    correct = float(mf.masked(arr, nodata=-9999.0).mean())
    assert abs(correct - 0.8) < 1e-9
    assert naive < correct          # 证明不处理 nodata 确实会出错


def test_masked_treats_nonfinite_as_nan():
    mf = _load_make_fig()
    arr = np.array([1.0, np.nan, np.inf, 4.0])
    out = mf.masked(arr)
    assert out.mask[1] and out.mask[2]
    assert abs(float(out.mean()) - 2.5) < 1e-9


def test_params_template_parses_and_has_contract_keys():
    p = yaml.safe_load((REPO / "_templates" / "params.yaml").read_text(encoding="utf-8"))
    assert set(p) >= {"meta", "gate", "refine", "data_fingerprint", "qa"}
    assert p["gate"]["size"]["width_mm"] == 90
    assert p["refine"]["output"]["version"] == 1
    assert p["refine"]["output"]["formats"] == ["pdf", "tif", "png"]
