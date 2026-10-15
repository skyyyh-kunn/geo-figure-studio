# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 约定。

## [1.0.0] - 2026-10-15

### 新增
- 图型规范补全至 12 类：新增 02 分类与变化检测 / 03 矢量分级设色 / 04 研究区位图 /
  06 局部放大图 / 07 样线剖面 / 08 采样验证 / 09 混淆矩阵 / 11 技术路线图 / 12 光谱曲线与三维地形。
- `_templates/make_fig.py` 内置 05-terrain 渲染（DEM 读取 + 分层设色 + 山体阴影），
  其余图型给出明确的固化占位提示。
- 端到端验收：真实 SRTM DEM 跑通 init → make → check → archive 全链路（0 不合规）。

### 变更
- 项目名简化为 `geo-figure-studio`。

## [0.1.0] - 2026-10-15

### 新增
- `SKILL.md`：Claude Code 技能入口（8 项硬门禁 + 主循环 + 精修 6 区块）。
- `references/` 8 份参考文档：去向矩阵、色带分级、chartjunk 红线、期刊投稿规范、git 工作流、3 类图型（01 栅格指数 / 05 地形 / 10 多面板统计）。
- `scripts/init_figure.py`：一键开新图（目录骨架 + params.yaml + 初始 commit）。
- `scripts/archive_version.py`：归档新版本（CHANGELOG + commit + tag）。
- `scripts/check_figure.py`：质检（栅格/PDF/色盲模拟/文本溢出/地图元素）。
- `_style/geo_style.py`：样式内核（色带、四种分级法、字重感知字体降级、尺寸保存）。
- `_templates/`：make_fig.py + params.yaml + figure_README.md 模板。
- `tests/`：pytest 测试套件。
- `.gitattributes`：成品图走 Git LFS，代码/参数走纯文本。
