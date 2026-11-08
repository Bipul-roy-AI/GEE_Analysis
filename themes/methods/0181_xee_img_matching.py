# Bangladesh adaptation: 0181_xee_img_matching
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0181_xee_img_matching'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0105_img_matching.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-186: Image Matching Techniques Spatially and Temporally

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
temp = ee.ImageCollection('NASA/VIIRS/002/VNP21A1D').filterDate('2020', '2021').select('LST_1KM')
temp
ndvi = ee.ImageCollection('NASA/VIIRS/002/VNP13A1').filterDate('2020', '2021').select('NDVI')
ndvi
import xarray as xr
ds_temp = xr.open_dataset(temp, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.01)
ds_temp
ds_ndvi = xr.open_dataset(ndvi, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.005)
ds_ndvi
ds_temp = ds_temp.sortby('time') * 1
ds_ndvi = ds_ndvi.sortby('time') * 1
ds_temp_monthly = ds_temp.resample(time='M').mean('time')
ds_ndvi_monthly = ds_ndvi.resample(time='M').median('time')
ds_temp_monthly
ds_ndvi_monthly
ds_ndvi_like_temp = ds_ndvi_monthly.interp_like(ds_temp_monthly)
ds_temp_monthly
ds_ndvi_like_temp
merge = xr.merge([ds_temp_monthly, ds_ndvi_like_temp])
merge
import netCDF4
merge.to_netcdf('merged_ds.nc')
merge.LST_1KM.plot(x='lon', y='lat', col='time', col_wrap=6, cmap='RdBu_r', robust=True)
merge.NDVI.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True, cmap='RdYlGn')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0181_xee_img_matching', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
