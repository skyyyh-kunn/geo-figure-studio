# 期刊制图规范 · geo-figure-studio

> **诚实原则**：地学各刊的**具体**图宽/字号/DPI 数值每年可能更新，且同一出版社不同刊
> 口径不一。本文件只给**通用基线**（跨刊稳定、不会错的部分）与**权威投稿页 URL**；
> 凡标「需查证」的具体数值，作图前**必须现查该刊最新作者指南**，不得凭印象填、不得编造。

## 通用基线（跨地学刊稳定）

| 项 | 通用值 | 说明 |
|----|--------|------|
| 单栏图宽 | 8–9 cm（约 3.2 英寸） | 对应双栏排版的一栏 |
| 双栏图宽 | 17–18 cm（约 7 英寸） | 跨整页 |
| 字号 | 6–8 pt（成品印刷后） | 图缩印后仍须可读 |
| 最小线宽 | 0.5 pt（约 0.18 mm） | 更细的线印刷易断 |
| 提交分辨率 | ≥300 DPI（位图）；矢量优先 | 出版要求常 600–1200 DPI |
| 提交格式 | PDF / EPS / SVG（矢量）；TIFF / PNG（位图） | 以刊要求为准 |
| 颜色模式 | 在线 RGB；需印刷复核时 CMYK | 灰度可读性常被单列要求 |
| 字体嵌入 | 必须嵌入 | 否则审稿系统替换字体毁版式 |

**这些是共识基线，不是某刊的承诺值**——具体到某刊，仍按下面 URL 现查。

## 国际期刊（投稿指南 URL）

| 期刊 | 作者指南 URL | 需查证项 |
|------|-------------|----------|
| Remote Sensing of Environment | https://www.elsevier.com/journals/remote-sensing-of-environment/0034-4257/guide-for-authors | 图宽/DPI/格式 |
| ISPRS J. Photogramm. Remote Sens. | https://www.elsevier.com/journals/isprs-journal-of-photogrammetry-and-remote-sensing/0924-2716/guide-for-authors | 图宽/DPI/格式 |
| Int. J. Applied Earth Obs. Geoinf. | https://www.elsevier.com/journals/international-journal-of-applied-earth-observation-and-geoinformation/0303-2434/guide-for-authors | 图宽/DPI/格式 |
| Remote Sensing (MDPI) | https://www.mdpi.com/journal/remotesensing/instructions | 图宽/DPI/格式 |
| IEEE TGRS | https://www.grss-ieee.org/publications/transactions-on-geoscience-and-remote-sensing/author-resources/ | 图宽/字号/格式 |
| Nature Geoscience | https://www.nature.com/ngeo/submission-guidelines | 图宽/字号/颜色 |
| Science | https://www.science.org/content/page/science-information-authors | 图宽/字号/格式 |
| AGU 系（JGR、Earth's Future、GRL） | https://www.agu.org/publish-with-agu/publish | 图宽/字号/格式 |
| Global Change Biology | https://onlinelibrary.wiley.com/page/journal/13652486/homepage/forauthors | 图宽/DPI/格式 |
| Journal of Hydrology | https://www.elsevier.com/journals/journal-of-hydrology/0022-1694/guide-for-authors | 图宽/DPI/格式 |
| CATENA | https://www.elsevier.com/journals/catena/0341-8162/guide-for-authors | 图宽/DPI/格式 |

## 中文核心期刊（投稿指南 URL）

| 期刊 | 投稿指南 URL | 需查证项 |
|------|-------------|----------|
| 遥感学报 | http://www.jors.cn/ | 图宽/字号/DPI |
| 地理学报 | 见期刊官网「投稿指南」（需查证当前域名） | 图宽/字号/DPI |
| 地理研究 | http://www.dlyj.ac.cn/ | 图宽/字号/DPI |
| 生态学报 | http://www.ecologica.cn/ | 图宽/字号/DPI |

> 中文刊的图要求差异更大（部分仍要纸质图、黑白图），且官网域名偶有调整，
> 以上 URL 也可能变动——**一律以现查为准**，本表只给起点，不背书具体数值。

## 使用流程

1. 硬门禁第 5 项确定去向期刊后，**现查**该刊作者指南的图相关章节。
2. 把查到的 `图宽 / 字号 / DPI / 格式 / 颜色模式` 填进 `params.yaml` 的 `output` 区块。
3. 若查不到（付费墙、外网不通），明确标记为「需查证」，**用通用基线兜底**并告知用户
   此项未核实，绝不编造一个"看起来像"的数值写死。
