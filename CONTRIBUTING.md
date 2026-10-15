# 贡献指南

欢迎提 issue 与 PR。本项目是「遥感 / 地学 / 空间制图」的工具箱 + Claude Code 技能。

## 添加新图型

1. 在 `references/figure-types/` 下新建 `NN-<name>.md`（编号沿用现有 01/05/10 的空位）。
2. 按现有模板写五段：**适用数据 / 必须要素 / 常见坑 / 顶刊默认 / 叙事检验**。
3. 若需要新色带或新分级方法：先改 `_style/geo_style.py`，再在 `tests/test_geo_style.py` 补回归测试。
4. `python -m pytest tests/ -q` 全绿后再提 PR。

## 提交规范

- `feat: <说明>（geo-figure-studio）`
- `fix: <说明>（geo-figure-studio）`
- `docs: <说明>（geo-figure-studio）`

## 数据隐私

**不要提交任何原始数据**（栅格 / 矢量 / 大文件）。本项目只接受数据指纹
（绝对路径 + 文件大小 + SHA256）。`.gitignore` 已忽略 `data/`、`*.nc`、`*.hdf`、`*.img` 等。

## 质检红线

- 地图类必须含比例尺、指北针、图例（原理示意图除外，且须标「示意图」）。
- 禁用 3D 饼图、渐变背景、阴影、高饱和荧光色。
- 交付前必跑 `scripts/check_figure.py`，如实报告「疑似」项。
