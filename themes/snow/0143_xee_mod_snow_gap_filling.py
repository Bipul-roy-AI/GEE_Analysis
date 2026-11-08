# Bangladesh adaptation: 0143_xee_mod_snow_gap_filling
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'snow' / '0143_xee_mod_snow_gap_filling'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0060_snow_gapfilling.ipynb


utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-148: MODIS Snow Cover Product Gap-Filling, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap
import xee
import xarray as xr
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
mod = ee.ImageCollection('MODIS/061/MOD10A1').filterDate('2020', '2021').select('NDSI_Snow_Cover')
mod
ds = xr.open_dataset(mod, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.01)
ds
ds.sel(time=ds.time.dt.month == 1).NDSI_Snow_Cover.plot(x='lon', y='lat', col='time', col_wrap=7, robust=True)
ds_rolling = ds.rolling(time=10, center=True, min_periods=1).median('time')
ds_fill = ds.fillna(ds_rolling)
ds_fill.sel(time=ds_rolling.time.dt.month == 1).NDSI_Snow_Cover.plot(x='lon', y='lat', col='time', col_wrap=7, robust=True)
import netCDF4
ds_fill.to_netcdf('snow_cover.nc')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'snow', '0143_xee_mod_snow_gap_filling', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'snow')  # explicit upload; requires Drive OAuth scope
