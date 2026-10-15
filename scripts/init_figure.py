#!/usr/bin/env python
"""geo-figure-studio · 一键开新图。

用法：
    python scripts/init_figure.py --name 河北NDVI年际趋势 --type 01-raster-index --dest journal
"""
from __future__ import annotations

import argparse
import datetime as _dt
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_DEFAULT = Path(__file__).resolve().parents[1]

# 去向 → 尺寸预设（mm）。期刊单栏 90 / 双栏 190；学位论文 A4 版心；PPT 16:9 半幅
SIZE_PRESETS = {
    "journal": {"width_mm": 90, "height_mm": 60, "exact": True},
    "journal-wide": {"width_mm": 190, "height_mm": 110, "exact": True},
    "thesis": {"width_mm": 150, "height_mm": 100, "exact": True},
    "ppt": {"width_mm": 160, "height_mm": 90, "exact": False},
}
DEST_ALIASES = {"journal": "journal", "期刊": "journal", "thesis": "thesis",
                "学位论文": "thesis", "ppt": "ppt", "PPT": "ppt"}


def create(name, figure_type, destination, repo=None, today=None):
    """建立一张新图的目录骨架并返回其路径。已存在则抛 FileExistsError。"""
    repo = Path(repo) if repo else REPO_DEFAULT
    dest = DEST_ALIASES.get(destination, destination)
    if dest not in SIZE_PRESETS:
        raise ValueError(f"未知去向 {destination!r}，可选 {sorted(SIZE_PRESETS)}")
    today = today or _dt.date.today().isoformat()

    fig_id = f"{today}_{name}"
    target = repo / "figures" / fig_id
    if target.exists():
        raise FileExistsError(f"图目录已存在：{target}")

    (target / "output").mkdir(parents=True)
    (target / "data").mkdir(parents=True)

    tpl = repo / "_templates"
    params = yaml.safe_load((tpl / "params.yaml").read_text(encoding="utf-8"))
    params["meta"]["figure_id"] = fig_id
    params["meta"]["title"] = name
    params["meta"]["created"] = today
    params["gate"]["figure_type"] = figure_type
    params["gate"]["destination"] = dest
    params["gate"]["size"].update(SIZE_PRESETS[dest])
    (target / "params.yaml").write_text(
        yaml.safe_dump(params, allow_unicode=True, sort_keys=False), encoding="utf-8")

    shutil.copy(tpl / "make_fig.py", target / "make_fig.py")

    readme = (tpl / "figure_README.md").read_text(encoding="utf-8")
    readme = (readme.replace("{{figure_id}}", fig_id)
                    .replace("{{narrative}}", "（待填：这张图要证明什么）"))
    for k in ("sensor", "resolution_m", "time_range", "composite",
              "composite_period", "cloud_mask", "atmospheric_correction",
              "index_formula", "version"):
        readme = readme.replace("{{" + k + "}}", "—")
    (target / "README.md").write_text(readme, encoding="utf-8")

    (target / "CHANGELOG.md").write_text(
        f"# 改动日志 · {fig_id}\n\n"
        f"| 版本 | 日期 | 改动 | 要求人 |\n|------|------|------|--------|\n"
        f"| v1 | {today} | 初版骨架 | 用户 |\n", encoding="utf-8")

    (target / "data" / ".gitkeep").touch()
    (target / "output" / ".gitkeep").touch()

    subprocess.run(["git", "add", "-A"], cwd=repo, check=False, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"feat: 新建图 {fig_id}（{figure_type}）"],
                   cwd=repo, check=False, capture_output=True)
    return target


def main(argv=None):
    ap = argparse.ArgumentParser(description="geo-figure-studio 开新图")
    ap.add_argument("--name", required=True, help="图名，如 河北NDVI年际趋势")
    ap.add_argument("--type", required=True, dest="figure_type",
                    help="图型编号，如 01-raster-index")
    ap.add_argument("--dest", required=True, help="journal / thesis / ppt")
    ap.add_argument("--repo", default=None, help="仓库根，默认脚本上两级")
    a = ap.parse_args(argv)
    d = create(a.name, a.figure_type, a.dest, repo=a.repo)
    print("已建立:", d)
    print("下一步：填 params.yaml 的 gate 区块（8 项），再跑 python make_fig.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
