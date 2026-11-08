# Bangladesh adaptation: 0129_export_ee
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0129_export_ee'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0043_export_xarray.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-134: Export from Xee Files, in Python API

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap
import xarray as xr
import xee
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
pr = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate('2015', '2016')
pr
ds = xr.open_dataset(pr, engine='ee', crs='EPSG:4326', scale=0.3, geometry=BD_ROI)
ds
monthly = ds.resample(time='M').sum('time')
import rioxarray
monthly = monthly.rio.write_crs('EPSG:4326', inplace=True)
monthly = monthly.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
monthly.rio.write_coordinate_system(inplace=True)
import netCDF4
monthly.to_netcdf('monthly_pr.nc')
import matplotlib.pyplot as plt
monthly.precipitation.plot(x='lon', y='lat', col='time', col_wrap=4, robust=True)
plt.savefig('monthly_pr.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0129_export_ee', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
