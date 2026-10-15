# geo-figure-studio

[简体中文](README.md) · [English](README.en.md)

A reproducible figure-making workbench for **remote sensing / geoscience / spatial mapping**,
doubling as a [Claude Code](https://claude.com/claude-code) skill.

It enforces a workflow of *"ask every plotting detail up front → borrow top-journal geoscience
figure conventions → draft → refine in six passes → auto QC → version every revision in git"*.
What you ship is a **reproducible, revertible, re-tunable** `script + params.yaml + rendered figure`,
never a one-off flattened image.

## Highlights

- **8 hard gates** before any figure: study area, data source, preprocessing recipe, figure type,
  destination, size, projection, narrative — missing one means ask, don't draw.
- **Draft first, refine in 6 blocks**: color & classification / map elements / text & fonts /
  layout / export / QC & freeze.
- **Top-journal conventions**: destination→size/font/DPI matrix, colormap + classification guide,
  colorblind simulation, chartjunk red lines, journal author-guide index.
- **Auto QC**: raster & PDF checks, colorblind simulation (Machado 2009), text overflow, map completeness.
- **git-per-revision**: one commit + one version directory per revision; rendered figures go to Git LFS,
  raw data is tracked only by SHA256 fingerprint.
- **Weight-aware CJK font fallback**: picks a regular-weight (400) CJK face for body text and falls back
  per-glyph, so no tofu boxes.

## Install

Python ≥ 3.10 (tested on 3.13.14). See [requirements.txt](requirements.txt).

```bash
git clone https://github.com/<your-name>/geo-figure-studio.git
cd geo-figure-studio
pip install -r requirements.txt
git lfs install        # figures are stored via Git LFS; run `git lfs pull` after clone
```

### Install as a Claude Code skill (optional)

```bash
git clone https://github.com/<your-name>/geo-figure-studio.git ~/.claude/skills/geo-figure-studio
```

Then just tell Claude: *"Plot the 2015–2024 NDVI annual trend for Hebei."*

## Quick start (standalone)

```bash
python scripts/init_figure.py --name hebei_ndvi_trend --type 01-raster-index --dest journal
# edit params.yaml (gate block + data_fingerprint)
cd figures/<date>_hebei_ndvi_trend && python make_fig.py
python scripts/check_figure.py --figure figures/<date>_hebei_ndvi_trend
python scripts/archive_version.py --figure figures/<date>_hebei_ndvi_trend --note "switch to RdYlGn"
```

## Figure types

All **12 types documented**, one spec per type (data / required elements / common pitfalls /
journal defaults / narrative check) under `references/figure-types/NN-*.md`:

| # | Type | Notes |
|---|------|-------|
| 01 | raster-index | NDVI / EVI / NDWI / LST continuous rasters |
| 02 | classification & change | LULC classification, bi-temporal change |
| 03 | vector choropleth | ratio/density grading of admin units / basins |
| 04 | study-area location | overview + zoomed study area (multi-level) |
| 05 | terrain / hillshade | DEM hypsometric tint + hillshade (**built-in renderer**) |
| 06 | inset / zoom | main map + high-resolution detail |
| 07 | transect profile | DEM/index/temperature along a line |
| 08 | sampling & validation | sample distribution + observed-vs-predicted |
| 09 | confusion matrix | classification accuracy & confusion |
| 10 | multipanel stats | regression / box / errorbar panels |
| 11 | technical roadmap | research flow schematic (no data) |
| 12 | spectral curves & 3D terrain | spectral separability + DEM 3D view |

## License

[MIT](LICENSE) © 2026 Kunyu Su
