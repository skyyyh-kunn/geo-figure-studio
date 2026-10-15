import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import init_figure  # noqa: E402


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True,
                   capture_output=True)
    # F3：Windows 非特权会话下 symlink 需开发者模式，改用 copytree（见账本裁定 F3）
    shutil.copytree(REPO / "_templates", tmp_path / "_templates")
    shutil.copytree(REPO / "_style", tmp_path / "_style")
    return tmp_path


def test_create_makes_expected_tree(repo):
    d = init_figure.create("河北NDVI年际趋势", "01-raster-index", "journal",
                           repo=repo, today="2026-10-13")
    assert d.name == "2026-10-13_河北NDVI年际趋势"
    for rel in ("params.yaml", "make_fig.py", "README.md", "CHANGELOG.md"):
        assert (d / rel).exists(), rel
    assert (d / "output").is_dir()
    assert (d / "data").is_dir()


def test_create_fills_params_from_cli(repo):
    d = init_figure.create("测试图", "05-terrain", "thesis",
                           repo=repo, today="2026-10-13")
    p = yaml.safe_load((d / "params.yaml").read_text(encoding="utf-8"))
    assert p["gate"]["figure_type"] == "05-terrain"
    assert p["gate"]["destination"] == "thesis"
    assert p["meta"]["figure_id"] == "2026-10-13_测试图"
    assert p["refine"]["output"]["version"] == 1


def test_create_applies_destination_size_preset(repo):
    d = init_figure.create("双栏图", "01-raster-index", "journal",
                           repo=repo, today="2026-10-13")
    p = yaml.safe_load((d / "params.yaml").read_text(encoding="utf-8"))
    assert p["gate"]["size"]["width_mm"] == 90
    assert p["gate"]["size"]["exact"] is True

    d2 = init_figure.create("PPT图", "01-raster-index", "ppt",
                            repo=repo, today="2026-10-13")
    p2 = yaml.safe_load((d2 / "params.yaml").read_text(encoding="utf-8"))
    assert p2["gate"]["size"]["width_mm"] == 160
    assert p2["gate"]["size"]["exact"] is False


def test_create_is_idempotent_guarded(repo):
    init_figure.create("重复图", "01-raster-index", "journal",
                       repo=repo, today="2026-10-13")
    with pytest.raises(FileExistsError):
        init_figure.create("重复图", "01-raster-index", "journal",
                           repo=repo, today="2026-10-13")


def test_create_leaves_gate_todos_for_unknown(repo):
    d = init_figure.create("待填图", "07-profile", "journal",
                           repo=repo, today="2026-10-13")
    p = yaml.safe_load((d / "params.yaml").read_text(encoding="utf-8"))
    assert p["gate"]["study_area"]["name"] == ""
    assert p["gate"]["data_source"]["paths"] == []
    assert p["gate"]["narrative"] == ""
