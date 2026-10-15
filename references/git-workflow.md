# git 工作流 · geo-figure-studio

## 仓库路径

- 仓库根：本仓库克隆目录（`geo-figure-studio/`），代码与图都放这里。
- 备份远程：自选（U 盘 / 内网裸仓库），remote 名约定为 `usb`；创建方式见 README。

## 分支规则

- **永远不在 `main`/`master` 直接改代码**。改图前先建分支：`git checkout -b feat/xxx`。
- 一版图 = 一次 commit + 一个 `output/vN/` 目录。
- 冻结（投稿/送审/归档）时打 tag：`git tag v1.0`。

## 禁止操作

- 不执行网络 `git push`（唯一例外：推送到本机 U 盘 remote `usb`）。
- 不执行 `git reset --hard` / `force push`（这些须用户手动确认）。

## `.gitattributes` 的 LFS 规则（全文）

```
*.png  filter=lfs diff=lfs merge=lfs -text
*.tif  filter=lfs diff=lfs merge=lfs -text
*.tiff filter=lfs diff=lfs merge=lfs -text
*.pdf  filter=lfs diff=lfs merge=lfs -text
*.svg  filter=lfs diff=lfs merge=lfs -text
*.jpg  filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text

# 参数与代码必须是纯文本，永不进 LFS
*.py   -text
*.yaml text eol=lf
*.md   text eol=lf

# 大栅格不入库（数据策略见 spec §9.3）
*.tif.aux.xml -filter -diff -merge
```

要点：成品图（png/tif/pdf/svg/jpg）走 LFS；`params.yaml`/`make_fig.py`/README 走纯文本，
保证 `git diff` 对参数改动可读。

## 数据不入库

原始数据（SRTM DEM、Landsat 影像、shapefile）**不进 git**。`params.yaml` 的
`data_fingerprint` 只记录：绝对路径、文件大小、SHA256 校验和。复现时靠指纹核验数据是否被换。

## 提交信息格式

- 图新建：`feat: 新建图 <figure_id>（<type>）`
- 图版本：`fig(<figure_id>): v<N> — <改了什么>`
- 技能改动：`feat:/fix:/docs: <说明>（geo-figure-studio）`

## U 盘同步

```bash
git push usb main && git lfs push usb --all
```

**为什么必须 `git lfs push usb --all`**：普通 `git push` 只传指针文件（约 130 字节的
`oid sha256:...`），不传真正的二进制对象。漏掉 `git lfs push` 的话，U 盘上的备份就是
一堆"无内容的指针"，图全部丢失。每次提交成品图后都要补这一句。

> 进度条显示 "0 B" 是 git-lfs 的显示假象，实际对象已上传。验证：`git lfs ls-files`。

## 常见故障

1. **LFS 对象没传过去** —— 症状：U 盘克隆后 `git lfs ls-files` 为空，图打不开。
   修：`git lfs push usb --all`；确认真实原因（是否只跑了 `git push`）。
2. **仓库体积失控** —— 症状：`git count-objects -vH` 持续膨胀。修：检查是否误把大栅格
   （`.tif` 数据文件）当图提交了；数据文件应只记指纹，`.gitignore` 已忽略 `data/`、`*.nc`、`*.hdf`。
3. **数据文件被移动导致复现失败** —— 症状：`check_figure.py` 报"数据文件不存在/校验和不匹配"。
   修：`params.yaml` 里 `data_fingerprint` 的路径是绝对路径；移动数据后须同步更新路径+sha256。

## 环境参考（开发机实测示例，2026-10，非通用要求）

- **Python**：3.13.14（Windows 10 Pro）
- **依赖**：cartopy 0.26.0、mapclassify 2.10.0、matplotlib 3.10.9、numpy 2.4.6、
  pandas 3.0.3、geopandas 1.1.3、rasterio 1.5.0、pypdf 6.20.1、Pillow 12.2.0
- **字体实测**：
  - `Source Han Serif SC` **仅一个条目、weight=900（Heavy）**——只有展示字重，无法作正文。
  - `Noto Serif SC` **未安装**。
  - 故字体降级链实际命中 **`SimSun`（宋体，weight=400）**，中文核心期刊正文标准。
  - 拉丁命中 **`Arial`**。
  - 结论：本机中文默认用宋体，是**正确机制**（字重感知降级）而非巧合。若日后装了
    思源宋体常规字重（400），首选会自动切回思源宋体。
- **GBK 控制台注意**：本机默认控制台是 GBK，跑含中文输出的命令时若出现乱码，
  加两个环境变量：`PYTHONUTF8=1` 与 `PYTHONIOENCODING=utf-8`。
- **`safe.directory`**：把备份远程放在 U 盘/外置盘这类"不记录属主"的盘时，git 会以
  "dubious ownership" 拦 `git push usb`。用
  `git config --global --add safe.directory <裸仓库路径>` 放行；撤除用
  `git config --global --unset safe.directory <裸仓库路径>`。
