# 去向矩阵 · 尺寸字号 DPI

数值必须与 `scripts/init_figure.py` 的 `SIZE_PRESETS` 完全一致（下表由 Step 10 自动校验）。

| 去向 | 宽×高 (mm) | exact | DPI | 字体 | 备注 |
|------|-----------|-------|-----|------|------|
| journal（单栏） | 90 × 60 | true | 600 | Arial + 宋体 | 线条 ≥0.5pt，字号 6-8pt |
| journal-wide（双栏） | 190 × 110 | true | 600 | 同上 | 跨栏图 |
| thesis | 150 × 100 | true | 300 | 宋体 + Times New Roman | A4 版心内 |
| ppt | 160 × 90 | false | 150 | 微软雅黑/黑体 | 16:9 半幅，字号 ≥14pt |

## 尺寸规则

- **期刊**：单栏 90mm、双栏 190mm 是绝大多数地学刊的版心宽；高度自定但保持 3:2 左右。
- **exact=true**：`save_figure(exact=True)` 不做 bbox 裁切，输出物理尺寸 == 设定尺寸（期刊硬要求）。
- **exact=false**（PPT）：允许 tight 裁切，内容撑满画布即可，不要求像素级精确。

## 字号与线宽（顶刊通用）

| 元素 | 期刊（90mm） | PPT |
|------|-------------|-----|
| 轴标签 | 8pt | ≥14pt |
| 刻度 | 7pt | ≥12pt |
| 图例 | 7pt | ≥12pt |
| 标题 | 8pt | ≥18pt |
| 轴/边框线宽 | 0.6pt | ≥1.5pt |
| 数据线宽 | 0.9pt | ≥2pt |

原则：**图按最终印刷尺寸画**（figsize 就是 mm 转 inch），不要在 PowerPoint 里拉伸缩放——那会
毁掉字号与线宽的一致性。
