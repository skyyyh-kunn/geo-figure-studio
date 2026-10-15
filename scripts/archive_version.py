#!/usr/bin/env python
"""geo-figure-studio · 版本归档。

把 params.yaml 的版本号 +1、建好新 output/vN 目录、追加 CHANGELOG、提交。
之后再跑 make_fig.py 就会写进新版本目录。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

import yaml


def _run(cmd, cwd):
    # 强制 UTF-8：本机默认控制台为 GBK，git 的提交/日志输出是 UTF-8，
    # text=True 用系统 locale 解码会崩（UnicodeDecodeError）。errors="replace" 兜底。
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def bump(figure_dir, note, requester="用户", repo=None, today=None):
    """版本号 +1 并归档。返回新版本号。"""
    d = Path(figure_dir).resolve()
    repo = Path(repo) if repo else d.parents[1]
    today = today or _dt.date.today().isoformat()
    if not note or not note.strip():
        raise ValueError("bump: note 不能为空 —— 每版必须写清改了什么")

    pp = d / "params.yaml"
    params = yaml.safe_load(pp.read_text(encoding="utf-8"))
    old = int(params["refine"]["output"]["version"])
    new = old + 1
    params["refine"]["output"]["version"] = new
    pp.write_text(yaml.safe_dump(params, allow_unicode=True, sort_keys=False),
                  encoding="utf-8")

    (d / "output" / f"v{new}").mkdir(parents=True, exist_ok=True)

    cl = d / "CHANGELOG.md"
    text = cl.read_text(encoding="utf-8") if cl.exists() else "# 改动日志\n\n"
    text += (f"\n## v{new} · {today}\n\n"
             f"- 改动：{note.strip()}\n"
             f"- 要求人：{requester}\n"
             f"- 说明：本版内容由 `output/v{new}/` 承载，重跑 `python make_fig.py` 生成\n")
    cl.write_text(text, encoding="utf-8")

    _run(["git", "add", "-A"], repo)
    _run(["git", "commit", "-m",
          f"fig({params['meta']['figure_id']}): v{new} — {note.strip()}"], repo)
    return new


def main(argv=None):
    ap = argparse.ArgumentParser(description="geo-figure-studio 版本归档")
    ap.add_argument("--figure", required=True, help="图目录，如 figures/2026-10-13_x")
    ap.add_argument("--note", required=True, help="本版改了什么")
    ap.add_argument("--requester", default="用户", help="谁要求改的")
    ap.add_argument("--repo", default=None)
    a = ap.parse_args(argv)
    v = bump(a.figure, a.note, a.requester, a.repo)
    print(f"已归档为 v{v}。下一步：python {Path(a.figure) / 'make_fig.py'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
