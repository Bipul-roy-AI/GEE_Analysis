# Bangladesh adaptation: 0192_bootcamp2026_7
# Original author: Amirhossein Ahrari; see original attribution below and originals/.
from bdgee.core import initialize, boundaries
from bdgee.notebook import export_outputs, upload_local
initialize()  # Run `earthengine authenticate` first; project is configured in bdgee.
BD_COUNTRY, BD_DISTRICTS = boundaries()
BD_ROI = BD_COUNTRY.geometry()
BD_BBOX = [88.0, 20.5, 92.7, 26.7]  # search only, not analysis boundary
roi = geometry = border = iran = tehran = province = loc = point = BD_ROI
# Run from the repository root; all local outputs are isolated by source.
from pathlib import Path
import os
_REPO_ROOT = Path.cwd()
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0192_bootcamp2026_7'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""07_session7_time_series_gap_filling.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session7: Time Series Gap Filling

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi

def cloud_mask(img):
    qa_band = img.select('QA_PIXEL')
    bit1 = qa_band.bitwiseAnd(1 << 1).neq(0)
    bit2 = qa_band.bitwiseAnd(1 << 2).neq(0)
    bit3 = qa_band.bitwiseAnd(1 << 3).neq(0)
    bit4 = qa_band.bitwiseAnd(1 << 4).neq(0)
    mask = bit1.Or(bit2).Or(bit3).Or(bit4)
    sr = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    ndvi = sr.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
    return ndvi.updateMask(mask.Not()).copyProperties(img, ['system:time_start'])
frame_filter = ee.Filter.And(ee.Filter.eq('WRS_PATH', 168), ee.Filter.eq('WRS_ROW', 34))
landsat9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate('2025', '2026').filterBounds(roi).filter(frame_filter).map(cloud_mask)
landsat9
import xarray as xr
landsat_ds = xr.open_dataset(landsat9, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=50)
landsat_ds = landsat_ds.sortby('time') * 1
landsat_ds.ndvi.plot(x='X', y='Y', col='time', col_wrap=7, robust=True, vmin=0)
landsat_ds
land_roll = landsat_ds.rolling(time=15, min_periods=1, center=True).mean('time')
land_fill = land_roll.fillna(0)
land_fill.ndvi.plot(x='X', y='Y', col='time', col_wrap=7, robust=True, vmin=0)

def sen2_mask(img):
    prob_band = img.select('probability')
    cloud_free = prob_band.lt(20)
    sr = img.select('B.*').multiply(0.0001)
    ndvi = sr.normalizedDifference(['B8', 'B4']).rename('ndvi')
    return ndvi.updateMask(cloud_free).copyProperties(img, ['system:time_start'])
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2025', '2026').filterBounds(roi).select('B.*').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 45)).linkCollection(ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY'), 'probability').map(sen2_mask)
sen2.limit(10)
sen2_ds = xr.open_dataset(sen2, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=100)
sen2_ds = sen2_ds.sortby('time') * 1
sen2_10days = sen2_ds.resample(time='10D').max('time')
sen2_roll = sen2_10days.rolling(time=10, min_periods=1, center=True).mean('time')
import netCDF4
sen2_roll.to_netcdf('sen2.nc')
sen2_roll.ndvi.plot(x='X', y='Y', col='time', col_wrap=6, robust=True, vmin=0)
sen2_10days.ndvi.plot(x='X', y='Y', col='time', col_wrap=6, robust=True, vmin=0)
sen2_ds.sel(time=sen2_ds.time.dt.month == 5).ndvi.plot(x='X', y='Y', col='time', col_wrap=7, robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0192_bootcamp2026_7', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
