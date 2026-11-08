# Bangladesh adaptation: 0179_xee_img_stat
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0179_xee_img_stat'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0102_array_stat.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-184: Image Statistics

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
smap = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/005').filterDate('2020', '2021').select('soil_moisture_am')
smap
import xarray as xr
ds = xr.open_dataset(smap, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds
ds = ds.sortby('time') * 1
ds_mean = ds.mean(dim='time')
ds_mean.soil_moisture_am.plot(x='lon', y='lat', robust=True)
mean_val = ds_mean.median(dim=['lon', 'lat']).soil_moisture_am.values
mean_val
mean_ser = ds.mean(dim=['lon', 'lat']).to_dataframe()
mean_ser
mean_ser.describe()
mean_ser.plot()
ds_sub = ds.sel(lon=52.72936677576619, lat=36.56616811342166, method='nearest')
ds_sub.to_dataframe().soil_moisture_am.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0179_xee_img_stat', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
