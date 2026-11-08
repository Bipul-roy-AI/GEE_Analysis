# Bangladesh adaptation: 0178_xee_img_clip
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0178_xee_img_clip'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0101_xarray_clip.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-183: Image Clipping

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
point = BD_ROI
point
border = BD_COUNTRY
map.addLayer(border)
vec = geemap.ee_to_gdf(border)
vec
era = ee.ImageCollection('ECMWF/ERA5/DAILY').filterDate('2020', '2021').select('mean_2m_air_temperature')
era
import xarray as xr
ds = xr.open_dataset(era, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.3)
ds = ds.sortby('time') * 1
ds.isel(time=10).mean_2m_air_temperature.plot(x='lon', y='lat', robust=True)
import geopandas as pgd
vec.plot()
import rioxarray
vec.crs
vec.geometry
ds_rename = ds.rename({'lon': 'x', 'lat': 'y'})
ds_clip = ds_rename.rio.clip(vec.geometry, vec.crs)
ds_clip.isel(time=10).mean_2m_air_temperature.plot(x='x', y='y', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0178_xee_img_clip', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
