# {{figure_id}}

## 这张图要证明什么

{{narrative}}

## 数据来源

| 项 | 值 |
|----|-----|
| 传感器 | {{sensor}} |
| 分辨率 | {{resolution_m}} m |
| 时间范围 | {{time_range}} |
| 预处理口径 | 合成={{composite}} / 周期={{composite_period}} / 云掩膜={{cloud_mask}} / 大气校正={{atmospheric_correction}} |
| 指数公式 | {{index_formula}} |

## 复现

```bash
python make_fig.py
```

产出写入 `output/v{{version}}/`。数据文件路径与校验和见 `params.yaml` 的 `data_fingerprint`。

## 版本

| 版本 | 日期 | 改动 |
|------|------|------|
| v1 | | 初版 |
