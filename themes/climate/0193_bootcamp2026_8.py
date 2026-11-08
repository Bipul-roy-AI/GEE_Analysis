# Bangladesh adaptation: 0193_bootcamp2026_8
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0193_bootcamp2026_8'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""08_session8_temporal_aggregation.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Landsat - Sentinel Data Analysis in GEE using Python API Session8: Temporal Aggregation

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

def ndvi_cal(img):
    qa_band = img.select('QA_PIXEL')
    bit1 = qa_band.bitwiseAnd(1 << 1).neq(0)
    bit2 = qa_band.bitwiseAnd(1 << 2).neq(0)
    bit3 = qa_band.bitwiseAnd(1 << 3).neq(0)
    bit4 = qa_band.bitwiseAnd(1 << 4).neq(0)
    cloud_mask = bit1.Or(bit2).Or(bit3).Or(bit4)
    sr = img.select('SR_B.*').multiply(2.75e-05).add(-0.2)
    ndvi = sr.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
    return ndvi.updateMask(cloud_mask.Not()).copyProperties(img, ['system:time_start'])
landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate('2020', '2026').filterBounds(roi).map(ndvi_cal)
landsat8
import xarray as xr
ds = xr.open_dataset(landsat8, engine='ee', crs='EPSG:3857', geometry=BD_ROI, scale=100)
ds = ds.sortby('time') * 1
ds.sel(time='2022-05').ndvi.plot(x='X', y='Y', col='time', robust=True)
ndvi_month = ds.groupby('time.month').median('time')
ndvi_month.ndvi.plot(x='X', y='Y', col='month', robust=True, col_wrap=6)
ndvi_season = ds.groupby('time.season').median('time')
ndvi_season.ndvi.plot(x='X', y='Y', col='season', robust=True)
ndvi_monthly = ds.resample(time='M').median('time')
ndvi_monthly.sel(time='2024').ndvi.plot(x='X', y='Y', robust=True, col='time', col_wrap=6, vmin=0)
df = ndvi_monthly.median(dim=['X', 'Y']).to_dataframe()
df.to_csv('ndvi_monthly_2020_2025.csv')
ndvi_3months = ds.resample(time='3M').median('time')
ndvi_3months.sel(time='2023').ndvi.plot(x='X', y='Y', robust=True, col='time')
ndvi_3month_mean = ndvi_3months.median(dim=['X', 'Y'])
ndvi_3month_mean.ndvi.plot()
ndvi_annual = ds.resample(time='A').median('time')
ndvi_annual.ndvi.plot(x='X', y='Y', robust=True, col='time')
ndvi_annual.median(dim=['X', 'Y']).ndvi.plot()
ndvi_out = ndvi_annual.copy()
import netCDF4
ndvi_out.to_netcdf('ndvi_annual.nc')
ndvi_open = xr.open_dataset('ndvi_annual.nc')
ndvi_open
import rioxarray
ndvi_out = ndvi_out['ndvi']
ndvi_out = ndvi_out.rio.write_crs('EPSG:3857')
ndvi_out = ndvi_out.rio.set_spatial_dims(x_dim='X', y_dim='Y')
ndvi_out = ndvi_out.rio.write_coordinate_system(inplace=True)
ndvi_out = ndvi_out.transpose('time', 'Y', 'X')
ndvi_out.rio.to_raster('ndvi_annual.tiff')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0193_bootcamp2026_8', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
