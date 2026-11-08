# Running the analyses

## Before a national export

1. Activate the virtual environment and authenticate to Earth Engine using your own account. The account must have EE access and permission to use `axial-paratext-491911-b6`.
2. Choose a theme and explicit half-open dates. Start with a small seasonal window. Use `--admin-level 0` for country only, `1` for divisions or `2` for districts.
3. Run without `--submit` to build and inspect `outputs/<theme>/task_plan.json`. The CLI checks nonempty boundaries and image bands; this is not a data-coverage or scientific-validity guarantee.
4. Run with `--submit` only after reviewing scale, time window and method. A returned task ID means submitted, not completed. Check completion in Earth Engine's Tasks interface or `earthengine task list`; inspect errors before relying on exports.
5. Confirm all GeoTIFF/CSV files arrived in `BD_GEE_<theme>`. Check no-data pixels, units, plausible ranges, administrative codes and timestamps. No export was executed during preparation of this repository.

Earth Engine Drive exports create separate flat folders by theme. Create/keep just one folder of each name: duplicate folder names can lead to unexpected destinations. Reruns can create duplicate files. GeoTIFFs may be tiled into multiple files for large outputs. Do not put a slash-delimited pseudo-path in `folder`.

## Code Editor JavaScript examples

Open one `.js` file from `themes/` in https://code.earthengine.google.com/ . Select project `axial-paratext-491911-b6` in the Code Editor settings. This selection cannot be imposed by JavaScript.

Review the original analysis window and `BD_SCALE`; the default 1000 m is a conservative export review default, **not a statement about native data resolution**. `BD_CREATE_EXPORTS` defaults to false. Set it true to create export tasks for displayed raster maps, their district/country descriptive CSVs, existing exports, image-series chart values, and printed EE scalar/dictionary values. Start the required tasks in the Tasks tab. Generic descriptive tables are not substitutes for class-area or population-count statistics: use the national workflows for those.

The hooks cover standard positional image-series, seriesByRegion and histogram calls. Histogram CSV cells contain bucket/value-count arrays; seriesByRegion exports district rows. The standard object-style configurations of these three chart types are also handled. Custom array charts need an explicit export of their underlying table/array. Do not assume a UI chart image is a numeric export. The source-specific catalogue is the starting point for reviewing these tutorial methods, not a guarantee that imported training assets are public or complete.

## Python tutorial adaptations

Start Jupyter from the **repository root**, and set the notebook's working directory to that root before the first cell. The first cell sets the national boundary and a source-specific local output directory; interactive notebook package installers have been removed. Install the notebook extra and any additional algorithm-specific libraries first. The original tutorial algorithm is in the next cell. Original dates are retained intentionally, including old-sensor coverage periods.

The final cell plans EE raster/table/time-series exports and writes local arrays, scalar values and plotted figures. It returns `bd_tasks` without starting them. Inspect `export_errors.json`; a failed output is explicitly reported, not silently marked successful. Change the export scale from its 1000 m review default to the appropriate analysis scale. This generic exporter includes intermediate global results, so review the plan for redundant exports. Image-collection maps are temporal means; their full national per-date values export as CSV. For categorical/count collections, replace generic means with method-specific class areas or sums.

To upload local figures, NetCDF and CSV files to the same thematic folder:

```python
from bdgee.core import initialize
initialize(authenticate=True)  # requests Earth Engine + Drive scopes
# Re-run the analysis; then, after reviewing outputs:
from bdgee.notebook import upload_local
upload_local('outputs/vegetation/YOUR_SOURCE_NAME', 'vegetation')
```

Enable Drive API on the OAuth/quota project if required. Credentials must include Drive scope; an EE-only token cannot upload local files. Uploads are explicit and can create duplicates. Review the local folder first. No Drive credentials are stored in this repository.

## National-scale resource management

A Bangladesh-wide 10 m grid contains roughly 1.5 billion land pixels; multi-date xarray, STAC and deep-learning examples can exceed workstation memory. A changed polygon does not solve that. Use server-side national workflows for exports; for experimental local-array methods, process spatial tiles/time chunks and merge results with the exact national mask. STAC examples search a Bangladesh bounding box and then clip the analysis dataset to GAUL, not to the box. Include border-intersecting tiles and preserve valid-data masks.

Imported training samples and empirical coefficients from other countries are not Bangladesh ground truth. RF/XGBoost/deep-learning/downscaling examples require local labels and spatial/temporal holdout evaluation before use. Install TensorFlow only for the relevant deep-learning example and compatible Python/hardware; it is intentionally not required for the national workflows.

## Rebuilding the source adaptations

```bash
python tools/adapt_archive.py /path/to/GoogleEarthEngine-main.zip
python tools/validate_sources.py
python -m pytest -q
```

The importer treats uploaded code as data. It preserves originals, removes notebook shell installers, sets explicit boundary aliases, adapts literal study geometries and emits an auditable catalogue. It does not execute tutorials or certify their models. Manual scientific improvements belong in `bdgee/`; rebuilding tutorial adaptations replaces their generated contents.

To check saved task IDs and retain their actual status:

```bash
python tools/task_status.py outputs/climate/task_plan.json
```

`READY`/`RUNNING` are pending, `COMPLETED` is completed, and `FAILED`/`CANCELLED` are unsuccessful. Confirm Drive files even after task completion. The helper exits nonzero on failed/cancelled tasks.

Additional experimental dependencies found in specific sources: `standard-precip`, `xclim`, `xeofs`, `xrscipy`, `xarray-spatial`, `dea-tools`, and `tensorflow`. These are not prerequisites for the national toolkit; review each package's supported Python/NumPy versions and install it only for the relevant tutorial. The optional notebook extra covers common tools but is not a tested all-tutorial environment.
