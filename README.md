# Bangladesh GEE Analysis

Bangladesh adaptations of **all 245 supplied tutorial files**, organized into 15 theme folders, plus a shared Python toolkit with 16 national workflows. Google Cloud project: **`axial-paratext-491911-b6`**.

**Validation status:** source conversion and offline API-graph tests are available. Earth Engine computations, dataset availability, numerical outputs and Drive delivery have **not** been verified: this machine has no authorized Earth Engine session. No export tasks have been submitted. The project ID is a billing/quota project identifier, not authentication.

## Choose a workflow

- **National analysis:** use `python -m bdgee ...` below. These workflows add QA masks, units, class-area/count-aware statistics and reproducible exports.
- **Individual tutorial methods:** browse [the full catalogue](docs/CATALOG.md), then `themes/<theme>/`. Every JavaScript file has a Bangladesh/export header; every Python example has both `.py` and output-free `.ipynb` forms. These retain their original algorithms and dates and are **experimental adaptations**, not scientifically validated national products. Run them one at a time after reviewing inputs, dates, scale, training data and memory needs.
- **Provenance:** `originals/` preserves all supplied bytes, including the file named `.py` that actually contains notebook JSON. These are reference material, not Bangladesh-ready entry points. [Attribution](ATTRIBUTION.md).

## Install and authenticate

```bash
cd /path/to/GEE_Analysis
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
# Optional: notebooks, geemap, STAC, xarray and plotting libraries
pip install -e '.[notebooks]'
earthengine authenticate
```

Register your Google account for Earth Engine and enable the Earth Engine API on `axial-paratext-491911-b6`. Your account needs permission to use that project. Authentication is interactive and credentials must stay outside Git. For uploading locally generated PNG/NetCDF/CSV files, use the Drive-scope authentication described in [RUNNING.md](docs/RUNNING.md).

## National products and Drive exports

```bash
# Build a plan; does not submit tasks (requires authenticated EE access).
python -m bdgee climate --start 2024-01-01 --end 2025-01-01
# Explicitly submit the raster and administrative-statistics exports.
python -m bdgee climate --start 2024-01-01 --end 2025-01-01 --submit
python -m bdgee water --start 2024-11-01 --end 2025-03-01 --submit
python -m bdgee flood --submit
```

Theme choices: `climate`, `vegetation`, `drought`, `water`, `flood`, `terrain`, `landcover`, `forest`, `agriculture`, `urban`, `population`, `air_quality`, `soil`, `water_quality`, `snow`, `ocean`.

Each named product exports a GeoTIFF map and a CSV combining district and country statistics to **`BD_GEE_<theme>`** in Google Drive. Categorical maps export class area in km²; population is summed on its native projection; continuous products export descriptive statistics and valid sample counts. These continuous means are sample means, not automatically area-weighted national estimates. No-data remains missing. Plans and task IDs are saved under ignored `outputs/<theme>/`. Raw GeoTIFF maps retain values; local figures can be uploaded separately. No nested path is passed as a Drive folder name.

**Date exceptions:** terrain/soil pH are static; Hansen uses 2000–2024; population uses the 2020 GHSL epoch; historical water uses 1984–2021; vegetation trend uses 2001–2024; flood uses the July baseline and August 20–31, 2024 event windows. Those product names identify their dates. Other products use `--start/--end` (end exclusive). Drought compares the calendar month of `--start` against the same month in 2001–2020, and includes that month across the selected window. Use a one-month window for a single-month result.

## Boundary and interpretation

The analysis mask is the **Bangladesh national land boundary from FAO GAUL 2015 level 0**, selected by `ADM0_NAME='Bangladesh'`; district summaries use GAUL 2015 level 2. It is a dated international public dataset, **not a claim of the latest official administrative or maritime boundary**. [Boundary details and replacement guidance](docs/METHODS.md). Offshore ocean products can legitimately be empty under a strict land mask. No boundary is inferred from a map click or foreign coordinates.

## Checks

```bash
python -m pytest -q
python tools/validate_sources.py
```

Offline tests check all national computation/export graphs against the EE SDK's bundled API signatures, raster/CSV export routing, categorical/population aggregation, local statistical methods, source hashes and complete conversion coverage. They do not access imagery or verify remote results. [Methods, limitations and validation steps](docs/METHODS.md).
