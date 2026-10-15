---
name: geo-figure-studio
description: 地学/遥感/空间制图工作台。触发词：画图、作图、出图、NDVI图、专题图、地形晕渲、剖面图、混淆矩阵、技术路线图、研究区位图、帮我画一张、改这张图、这张图再调一下。按「8项硬门禁 → 草图 → 6区块分批追问 → 质检 → git逐版归档」流程产出可复现、可回退、符合地学顶刊规范的图。产出脚本+params.yaml+成品图，而非一次性固化效果图。
---

# geo-figure-studio · 地学作图工作台

## 定位

地学/遥感/空间制图任务的主入口。不接管光电/非空间通用科研绘图（→ `scientific-toolkit-skill`），
不接管学术 Word/PPT 排版（→ `office-academic-skill`）。

**仓库根**：本仓库克隆目录（代码与图都放这里，`scripts/` 相对仓库根定位）
**参考库**：本技能 `references/` 目录，用到哪类图才读哪份，不要一次全读。

## 铁律

1. **硬门禁 8 项缺一不出图** —— 只提问，不动手
2. **先出草图再追问细节** —— 配色/断点/留白看着图判断比空想准
3. **`params.yaml` 是唯一真相源** —— 禁止在 `make_fig.py` 里硬编码可调参数
4. **交付前必跑质检** —— 结果如实报告，不隐瞒「疑似」项
5. **不生成不可二次调整的固化效果图** —— 代码必须留存
6. **不编造数据支撑图表**
7. 改代码前建 `feat/xxx` 分支；不执行网络 `git push` / `reset --hard` / `force push`
   （唯一例外：推送到 U 盘 remote `usb`）

## 主循环

```
用户要图
  ↓
【硬门禁 8 项】不齐 → 只提问
  ↓  齐了
【初始化】python scripts/init_figure.py --name X --type NN --dest journal
  ↓
【填 params.yaml】把 8 项答案写进 gate 区块；数据写 data_fingerprint
  ↓
【第一版草图】按顶刊默认参数出图：python make_fig.py
  ↓
【分批精修】A 配色分级 → B 地图要素 → C 文字字体 → D 版式排版 → E 输出投稿
     每块：问 → 改 params.yaml → 重跑 → 用户确认 → archive_version.py
  ↓
【质检】python scripts/check_figure.py --figure figures/xxx
     不合规必改；疑似项交用户人眼确认
  ↓
【冻结】archive_version.py 记录终版 → 更新 README.md 索引 → git push usb main && git lfs push usb --all
```

## 硬门禁 8 项

问法：一次问齐，让用户能一次答完；答不出的项明确标记为待定，**不得默认填充**。

| # | 项目 | 追问要点 |
|---|------|----------|
| 1 | 研究区与四至 | 区域名？边界文件路径？经纬度范围？ |
| 2 | 数据源 | 文件绝对路径、传感器、分辨率、时间范围 |
| 3 | **数据预处理口径** | 合成方式与周期、云掩膜方法、是否大气校正、指数公式 |
| 4 | 图型 | 见 `references/figure-types/`（12 类全文档化：01–12） |
| 5 | 去向 | 期刊论文 / 学位论文 / 汇报 PPT |
| 6 | 尺寸 | 单栏 90mm / 双栏 190mm / 整页 / PPT 16:9 半幅 |
| 7 | 投影与坐标系 | 地理还是投影坐标？具体 EPSG？ |
| 8 | **叙事** | 这张图要证明什么结论？答不出 → 提示这张图可能不该画 |

## 精修 6 区块

出草图后逐块追问，答一块改一块，每块一次 `archive_version.py`。

- **A 配色与分级** —— 色带选型、分级方法（Jenks/分位数/等间隔/标准差）、断点值、色盲校验、跨图统一性
- **B 地图要素** —— 比例尺、指北针、经纬网、行政边界与注记、地名、图例、放大框与连线
- **C 文字与字体** —— 中英文字体、各级字号、子图编号、单位量纲、有效数字
- **D 版式与排版** —— 画布尺寸、子图间距与对齐、留白裁切、面板比例、共用图例
- **E 输出与投稿** —— 格式、DPI、字体嵌入、RGB/CMYK、灰度可读性
- **F 质检与冻结** —— 跑质检、修不合规、打 tag、更新索引

## 常用命令

```bash
# 开新图
python scripts/init_figure.py --name 河北NDVI年际趋势 --type 01-raster-index --dest journal

# 出图（在图的目录下）
python make_fig.py

# 归档为新版本（先跑这个，再跑 make_fig.py 写入新版本目录）
python scripts/archive_version.py --figure figures/2026-10-13_河北NDVI年际趋势 --note "配色改 RdYlGn"

# 质检
python scripts/check_figure.py --figure figures/2026-10-13_河北NDVI年际趋势

# 备份到 U 盘
git push usb main && git lfs push usb --all
```

## 参考库索引

| 文件 | 何时读 |
|------|--------|
| `references/journal-specs.md` | 确定去向为期刊时，查目标刊的尺寸/字号/DPI |
| `references/destinations.md` | 每次作图确定尺寸字号时 |
| `references/figure-types/NN-*.md` | 确定图型后，读对应那一份 |
| `_templates/make_fig.py` | 已内置 05-terrain 渲染；其余图型按对应 figure-types 文档实现后固化回此模板 |
| `references/palettes.md` | 进入精修区块 A 时 |
| `references/chartjunk.md` | 出草图前自检，以及用户说"感觉不好看"时 |
| `references/git-workflow.md` | 涉及分支、归档、U 盘同步、冲突处理时 |

## 红线

- 不编造数据支撑图表
- 不生成不可二次调整的固化效果图 —— 代码必须留存
- 地图类不得缺比例尺、指北针、图例（用户明确示意的原理示意图除外，且须标注"示意图"）
- 禁用 3D 饼图、渐变背景、阴影、高饱和荧光色
- 不在 `main` 分支直接改动
- 交付前必跑质检，如实报告「疑似」项

## 首次使用提示

本技能首次在本机运行时，先读 `references/git-workflow.md` 的「环境参考」小节，
确认字体降级链实际命中哪个字体、依赖是否齐全。
