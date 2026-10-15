import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import archive_version  # noqa: E402


@pytest.fixture
def fig(tmp_path):
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path,
                   check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path,
                   check=True, capture_output=True)
    d = tmp_path / "figures" / "2026-10-13_x"
    (d / "output" / "v1").mkdir(parents=True)
    (d / "output" / "v1" / "fig.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (d / "params.yaml").write_text(
        yaml.safe_dump({"meta": {"figure_id": "2026-10-13_x"},
                        "refine": {"output": {"version": 1}}},
                       allow_unicode=True), encoding="utf-8")
    (d / "CHANGELOG.md").write_text(
        "# 改动日志 · 2026-10-13_x\n\n| 版本 | 日期 | 改动 | 要求人 |\n"
        "|------|------|------|--------|\n| v1 | 2026-10-13 | 初版 | 用户 |\n",
        encoding="utf-8")
    return d, tmp_path


def test_bump_increments_version(fig):
    d, repo = fig
    new = archive_version.bump(d, "配色改为 RdYlGn", repo=repo)
    assert new == 2
    p = yaml.safe_load((d / "params.yaml").read_text(encoding="utf-8"))
    assert p["refine"]["output"]["version"] == 2


def test_bump_appends_changelog_entry(fig):
    d, repo = fig
    archive_version.bump(d, "配色改为 RdYlGn", requester="导师", repo=repo)
    txt = (d / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "配色改为 RdYlGn" in txt
    assert "导师" in txt
    assert "## v2" in txt          # 版本归档以「## vN · 日期」标题追加，非表格行


def test_bump_puts_changelog_under_version_heading(fig):
    d, repo = fig
    archive_version.bump(d, "加显著性打点", repo=repo)
    lines = (d / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    assert any(l.startswith("## v2") for l in lines)


def test_bump_commits_with_note(fig):
    d, repo = fig
    archive_version.bump(d, "改断点为 Jenks 6 级", repo=repo)
    log = subprocess.run(["git", "log", "--oneline"], cwd=repo,
                         capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    assert "改断点为 Jenks 6 级" in log


def test_bump_writes_new_output_dir(fig):
    d, repo = fig
    archive_version.bump(d, "第二版", repo=repo)
    assert (d / "output" / "v2").is_dir()
