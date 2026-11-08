# Bangladesh adaptation: 0177_xee_xarray_collection
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0177_xee_xarray_collection'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0100_xarray.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-182: Image Collection vs. Xarray

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
era = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate('2019', '2020')
era
import xarray as xr
ds = xr.open_dataset(era, engine='ee', crs='EPSG:4326', scale=1, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds
ds.mean_2m_air_temperature
temp = ds.mean_2m_air_temperature
temp.coords
temp.dims
temp.values
temp.time.values
temp.lon.values
temp.lat.values
temp.isel(time=20)
temp.sel(time='2019-07-10')
temp.sel(time=slice('2019-07-01', '2019-09-01'))
temp.sel(time=temp.time.dt.month == 8)
temp_cel = temp - 273.15
temp_cel
july = temp_cel.sel(time=temp_cel.time.dt.month == 7)
july.plot(x='lon', y='lat', col='time', robust=True, col_wrap=7)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0177_xee_xarray_collection', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
