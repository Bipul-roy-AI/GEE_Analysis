# Bangladesh adaptation: 107_xee_water_consumption
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'soil_drought' / '107_xee_water_consumption'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0015_water_consumption.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-112: Vegetation Water Consumption, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap as gee
import xarray as xr
import xee
None
None
ndvi = ee.ImageCollection('MODIS/061/MOD13A2').select('NDVI').filterDate('2019', '2020')
ndvi_max = ndvi.max().multiply(0.0001)
ndvi_thr = ndvi_max.gt(0.5).selfMask()
ndvi_pix_area = ndvi_thr.multiply(ee.Image.pixelArea())
veg_area = ndvi_pix_area.reduceRegion(reducer=ee.Reducer.sum(), geometry=geometry, scale=1000).values().get(0)
veg_area.getInfo()
map = gee.Map(basemap='HYBRID')
map
geometry = BD_ROI
ds_ndvi = xr.open_dataset(ndvi, engine='ee', crs='EPSG:4326', scale=0.01, geometry=BD_ROI)
ds_ndvi
ds_ndvi_max = ds_ndvi.max(dim='time') * 0.0001
ds_ndvi_max.NDVI.plot(x='lon', y='lat', cmap='Greens', robust=True)
ds_ndvi_thr = ds_ndvi_max.NDVI > 0.5
ds_ndvi_thr.plot(x='lon', y='lat')
'https://gee-community-catalog.org/projects/usgs_modis_et/'
et = ee.ImageCollection('projects/earthengine-legacy/assets/projects/usgs-ssebop/modis_et_v5_monthly').filterDate('2019', '2020')
ds_et = xr.open_dataset(et, engine='ee', scale=0.01, crs='EPSG:4326', geometry=BD_ROI)
ds_et
ds_et.et.plot(x='lon', y='lat', cmap='gist_earth_r', col='time', col_wrap=4, robust=True)
et_mask = ds_et * ds_ndvi_thr
et_mask.et.plot(x='lon', y='lat', cmap='gist_earth_r', col='time', col_wrap=4, robust=True)
et_mean = et_mask.mean(dim=['lon', 'lat'])
et_mean
et_mean_val = et_mean.et.values
et_mean_val
wat_cons = 7834196440.9002495 * et_mean_val
wat_cons

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '107_xee_water_consumption', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
