# geo-figure-studio

[English](README.en.md) · [简体中文](README.md)

一个面向**遥感 / 地学 / 空间制图**的可复现作图工作台，兼作 [Claude Code](https://claude.com/claude-code) 的专用技能（Skill）。

它把「逐项问清作图细节 → 借鉴地学顶刊制图规范 → 出草图 → 分批精修 → 自动质检 → git 逐版归档」
串成一条**强制工作流**。交付的是**可复现、可回退、可二次调整**的 `脚本 + params.yaml + 成品图`，
而不是一张一次性固化的效果图。

> 本项目由武汉大学遥感科研工作者发起，初衷是解决"图出完了就改不动、配色全靠感觉、每张图都从零开始"的痛点。

## 特性

- **8 项硬门禁**：研究区 / 数据源 / 预处理口径 / 图型 / 去向 / 尺寸 / 投影 / 叙事，缺一不出图
- **先草图后精修**：配色分级 / 地图要素 / 文字字体 / 版式排版 / 输出投稿 / 质检冻结，6 区块逐块追问
- **顶刊制图规范**：尺寸字号 DPI 去向矩阵、色带分级与色盲校验、chartjunk 红线、期刊投稿规范索引
- **自动质检**：栅格与 PDF 检查、色盲模拟（Machado 2009）、文本溢出、地图元素完整性
- **git 逐版归档**：每版图 = 一个 commit + 一个版本目录；成品图走 Git LFS，原始数据只记 SHA256 指纹
- **字重感知字体降级**：中文正文自动挑常规字重（400），缺字逐字回退，不出现豆腐块

## 目录结构

```
geo-figure-studio/
├── SKILL.md                 # Claude Code 技能入口（8 项门禁 + 主循环）
├── references/              # 制图参考库（用到哪类读哪份，不一次全读）
│   ├── destinations.md      # 去向矩阵：期刊/学位/PPT 的尺寸·字号·DPI
│   ├── palettes.md          # 色带选型、四种分级法、色盲校验实测
│   ├── chartjunk.md         # 顶刊红线：3D 饼图/渐变/阴影/双 Y 轴滥用
│   ├── journal-specs.md     # 期刊投稿规范索引（含作者指南 URL）
│   ├── git-workflow.md      # 分支/归档/Git LFS/常见故障
│   └── figure-types/        # 各图型规范（12 类全文档化，01–12）
├── scripts/                 # 三个命令行脚本
│   ├── init_figure.py       # 开新图：生成目录骨架 + params.yaml
│   ├── archive_version.py   # 归档新版本：CHANGELOG + commit + tag
│   └── check_figure.py      # 质检：栅格/PDF/色盲/溢出/元素
├── _style/geo_style.py      # 样式内核：色带/分级/字体/保存
├── _templates/              # 每张图的模板
│   ├── make_fig.py          # 出图脚本（只读 params.yaml）
│   ├── params.yaml          # 唯一真相源（8 项门禁 + 数据指纹）
│   └── figure_README.md     # 图说明模板
└── tests/                   # pytest 测试
```

## 安装

**依赖**：Python ≥ 3.10（开发时实测 Python 3.13.14）。核心库见 [requirements.txt](requirements.txt)。

```bash
git clone https://github.com/<your-name>/geo-figure-studio.git
cd geo-figure-studio
pip install -r requirements.txt
git lfs install        # 成品图走 Git LFS，克隆后拉取二进制需 git lfs pull
```

### 安装为 Claude Code 技能（可选）

把本仓库放到技能目录，`SKILL.md` 即被自动识别：

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
git clone https://github.com/<your-name>/geo-figure-studio.git ~/.claude/skills/geo-figure-studio

# Windows
git clone https://github.com/<your-name>/geo-figure-studio.git %USERPROFILE%\.claude\skills\geo-figure-studio
```

## 快速开始

### 作为独立工具

```bash
# 1. 开新图（生成 figures/<日期>_<图名>/ 骨架 + params.yaml）
python scripts/init_figure.py --name 河北NDVI年际趋势 --type 01-raster-index --dest journal

# 2. 填 params.yaml 的 gate 区块（8 项）与 data_fingerprint（数据只记路径+SHA256）

# 3. 出图（在图的目录下）
cd figures/2026-10-15_河北NDVI年际趋势
python make_fig.py

# 4. 质检
python scripts/check_figure.py --figure figures/2026-10-15_河北NDVI年际趋势

# 5. 归档新版本（先归档，再重跑写入新版本目录）
python scripts/archive_version.py --figure figures/2026-10-15_河北NDVI年际趋势 --note "配色改 RdYlGn"
```

### 作为 Claude Code 技能

直接对 Claude 说：**「帮我画一张河北 2015–2024 年 NDVI 年际趋势图」**。
技能会先逐项问清 8 项硬门禁，再出草图、分批精修、质检、归档。

## 工作流

### 8 项硬门禁（缺一不出图）

| # | 项目 | 追问要点 |
|---|------|----------|
| 1 | 研究区与四至 | 区域名？边界文件路径？经纬度范围？ |
| 2 | 数据源 | 文件绝对路径、传感器、分辨率、时间范围 |
| 3 | 数据预处理口径 | 合成方式与周期、云掩膜、大气校正、指数公式 |
| 4 | 图型 | 见 `references/figure-types/` |
| 5 | 去向 | 期刊论文 / 学位论文 / 汇报 PPT |
| 6 | 尺寸 | 单栏 90mm / 双栏 190mm / 整页 / PPT 16:9 半幅 |
| 7 | 投影与坐标系 | 地理还是投影坐标？具体 EPSG？ |
| 8 | 叙事 | 这张图要证明什么结论？答不出 → 这张图可能不该画 |

### 精修 6 区块

**A 配色与分级** → **B 地图要素** → **C 文字与字体** → **D 版式与排版** → **E 输出与投稿** → **F 质检与冻结**

出草图后逐块追问，答一块改一块，每块一次 `archive_version.py` 归档。

## 图型支持

12 类图型**全部文档化**，每类一份规范（适用数据 / 必须要素 / 常见坑 / 顶刊默认 / 叙事检验），
见 `references/figure-types/NN-*.md`：

| 编号 | 图型 | 说明 |
|------|------|------|
| 01 | 栅格指数专题图 | NDVI / EVI / NDWI / LST 等连续栅格 |
| 02 | 分类与变化检测 | 土地利用分类、两时相变化检测 |
| 03 | 矢量分级设色 | 行政单元 / 流域的比率与密度分级 |
| 04 | 研究区位图 | 定位图 + 研究区放大图（多层次递进） |
| 05 | 地形晕渲图 | DEM 分层设色 + 山体阴影（**已内置渲染**） |
| 06 | 局部放大图 | 主图 + 关键局部高分辨率放大 |
| 07 | 样线剖面图 | 沿样线的 DEM / 指数 / 温度剖面 |
| 08 | 采样验证图 | 采样点分布 + 实测 vs 估算散点 |
| 09 | 混淆矩阵图 | 分类精度与混淆来源 |
| 10 | 多面板统计图 | 散点回归 / 箱线 / 误差棒等拼图 |
| 11 | 技术路线图 | 研究流程纯示意（不依赖地理数据） |
| 12 | 光谱曲线与三维地形 | 光谱可分性 + DEM 三维可视化 |

## 色盲校验

`check_figure.py` 用 **Machado 2009** 模型对相邻色级做红绿色盲（deuteranopia/protanopia）模拟，
报最小 ΔE。阈值 10：<5 判「不合规」，5–10 判「疑似」。实测结论——定性色带用 `tol_muted` 级数再高也安全；
连续色带 `YlGn`/`terrain` 别超过 6 级。详见 [references/palettes.md](references/palettes.md)。

## 贡献

欢迎提 issue 与 PR，见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

[MIT](LICENSE) © 2026 苏坤羽 (Kunyu Su)
