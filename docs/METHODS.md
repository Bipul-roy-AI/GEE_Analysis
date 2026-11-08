# Methods, scope and validation

## What was changed

All 245 supplied files are accounted for in `catalog.json`, including source hashes, datasets found in the code, theme and validation notes. Adaptations replace drawn or literal foreign study geometries with Bangladesh, remove interactive notebook installers, remove embedded notebook outputs, use the requested cloud project through shared initialization and add themed export helpers. They preserve tutorial dates and algorithms so the source method remains inspectable. These adaptations are distinct from the QA improvements in the national toolkit; they have not all been upgraded into validated national models.

The national toolkit adds the following more reproducible approaches:

| Theme | Products and safeguards |
|---|---|
| Climate | CHIRPS daily totals, >=1 mm wet-day counts, >=50 mm heavy-rain-day counts; ERA5-Land Celsius and vector-magnitude wind speed. Do not sum monthly mean precipitation rates as totals. |
| Vegetation | MODIS Collection 6.1 scaled NDVI with SummaryQA, valid composite counts and annual-mean Sen slope for 2001–2024. Offset and slope bands have different units. |
| Drought | VCI against the **same calendar month** in 2001–2020; zero/near-zero denominator mask. VCI is not SPI, SPEI or a calibrated yield-loss model. |
| Water | Sentinel-2 harmonized reflectance, SCL cloud/shadow/no-data filtering, MNDWI and a spectral water screen; JRC historical occurrence as separate context. Threshold water is not a validated lake inventory. |
| Flood | August 2024 candidate inundation from Sentinel-1 VH change with a July baseline; matched pass and common relative-orbit IDs, speckle reduction, permanent-water/slope masks and small-component filtering. Common-orbit mosaics still need footprint/acquisition review and per-orbit evaluation. |
| Terrain | SRTM elevation, slope and aspect. A radar surface elevation is not a bare-earth flood-depth model. |
| Land cover | Dynamic World modal class and temporal mean probabilities; area by each class, not mean class ID. Modal label and mean-probability argmax are different products. |
| Forest | Pinned Hansen 2024 v1.12 tree cover 2000 and annual loss-year areas; loss is not necessarily deforestation or its cause. Deliberately pinned, not labelled the latest release. |
| Agriculture | MODIS IGBP cropland and cropland/natural-vegetation mosaic classes, masked NDVI. This does not identify Bangladesh crop species or validate irrigation. |
| Urban | QA-filtered MODIS daytime LST and valid-coverage VIIRS night radiance; no unsupported attribution of heat to urbanization. |
| Population | Fixed GHSL 2020 population counts summed on their native grid, not averaged or relabelled as current population. |
| Air quality | Sentinel-5P OFFL tropospheric NO2, CO and CH4 columns with product-specific units. Catalog-ingestion masks are retained; additional application-specific QA and coverage checks are required. Columns are not surface concentrations or PM2.5. |
| Soil | ERA5-Land top-layer volumetric soil water and scaled OpenLandMap topsoil pH. This does not measure field-scale irrigation or groundwater. |
| Water quality | Water-masked NDTI and green/blue ratios; explicitly dimensionless uncalibrated proxies. No local chlorophyll, TSS or turbidity concentration is invented. |
| Snow | Valid-observation mask for MODIS snow codes and separate observed-snow/valid-day counts. Missing days do not become zero snow. Bangladesh is not a seasonal snowpack study site. |
| Ocean | HYCOM surface temperature/salinity with scale/offset. Strict Bangladesh land clipping may contain few or no valid ocean pixels. No offshore or EEZ boundary is invented. |

`bdgee.series` adds same-month standardized anomalies, robust Theil–Sen trends with intervals and consecutive-spell counting that breaks on missing values. The anomaly is explicitly **not** gamma-fitted SPI. Kendall p-values are uncorrected for serial dependence; inferential climate studies require autocorrelation/seasonality checks, suitable multiple-testing controls and independent validation.

## Geographic contract

Default national mask: `FAO/GAUL/2015/level0`, `ADM0_NAME = Bangladesh`. Division/district units use levels 1/2, also filtered to Bangladesh. This is a dated land boundary, not a current survey or a maritime delimitation. Disputed/coastal representations and administrative changes should be reviewed against an authoritative source before publication. STAC bounding boxes are only search bounds; analysis pixels must be masked by the exact national polygon.

To use an official supplied national asset, change the `boundaries()` selection in `bdgee/core.py` to the verified asset and its actual property schema, and replace the matching declaration in `tools/js_header.txt` before rebuilding adaptations. Administrative features must share the chosen boundary vintage or be intersected and reviewed. No private asset path is guessed.

## Export semantics

- Each national product exports a numeric, cloud-optimized GeoTIFF plus CSV administrative statistics. Continuous products have mean, standard deviation, min/max and valid sample count; categorical products have class km²; counts are summed.
- `EPSG:4326` is the default geographic export/statistics grid following the reported projection-parsing failure with the previous `EPSG:6933` configuration. It is not an equal-area grid; class areas still use `ee.Image.pixelArea()` evaluated on the reduction grid. Population retains its native projection to avoid regridding counts. Scale matches a practical native/product resolution; it does not improve underlying information.
- Pixel area is applied **before** class-area aggregation. Masked areas remain missing. Continuous statistics are pixel/sample weighted on the selected grid, not automatically area-weighted or population-weighted estimates. Aspect needs circular statistics for directional interpretation; its generic arithmetic mean is not a preferred national direction.
- No categorical interpolation or fine-pixel output is presented as new measured information. Exporting a coarse climate field at 10 m would only resample it.
- The generic tutorial exporters cannot infer arbitrary algorithm semantics. Review labels and scales; use the typed national exporter for count and class products. UI styling is not scientific data. Local PNG plots, CSV values and NetCDF arrays can be uploaded with the explicit Drive helper.
- Independent task execution can fail because of data gaps, quotas, private assets, time limits or Drive permissions. A plan/submitted ID is not a completed result.

## Experimental methods that still need study-specific work

Downscaling, empirical water-quality concentrations, biomass/carbon models, crop-type classifiers, flood depth, inferred soil moisture, flood-risk prediction and forecasts need local calibration, physically justified assumptions and spatial/time holdout evaluation. Imported training features and assets must be supplied or replaced with verified Bangladesh samples. Replacing training geometries with a country polygon does not create labelled samples. Do not run or interpret such examples until their training schema and sample locations have been reviewed.

Snow/ice/volcano examples remain educational mechanisms; no Bangladesh snowpack, frozen lake or eruption event is asserted. A Bangladesh SO2 anomaly is not evidence of volcanic activity. Open-water indices cannot alone separate all turbid water, built surfaces, shadows and vegetation. SAR low backscatter is not uniquely floodwater or oil. Flood-depth and groundwater changes cannot be established from a DEM/GRACE proxy alone.

The source catalogue's `adapted_unverified` status is intentionally conservative: syntax conversion succeeded, but live datasets, imported features, library compatibility and scientific results were not verified for that source. Optional tutorial dependencies are not all installed or tested in the preparation machine. No published figure or numeric result is fabricated to fill this gap.

## Live validation once authenticated

1. Confirm the national selection returns one feature and inspect division/district counts and codes.
2. For each dataset/window, check collection counts, first-image bands, scale/offset, native projection, valid coverage and acquisition dates; report zero observations explicitly.
3. Inspect distributions and independent reference points before accepting thresholds or empirical models. Check seasonal comparability and event timing.
4. Export a representative product and administrative CSV; confirm task completion and Drive delivery. Check class totals against mapped valid area and population totals against the native source reduction.
5. For every scientific tutorial used, run it to completion with its exact optional dependencies, review export_errors.json, verify every intended output and document local validation. Offline API graph tests do not replace this step.
