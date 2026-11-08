# Bangladesh adaptation: 0101_xee_intro
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0101_xee_intro'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0009_xee_intro3.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-106: Introduction to Xee, for GEE Python API

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!


"""
import ee
import xarray as xr
import xee
None
None
temp = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').select('temperature_2m').filterDate('2010', '2011')
ds = xr.open_dataset(temp, engine='ee', geometry=BD_ROI)
ds
jan = ds.sel(time='2010-01-01')
jan
jan['temperature_2m'].plot(x='lon', y='lat', cmap='jet')
temp_cel = ds - 273.15
temp_cel
jan_cel = temp_cel.sel(time='2010-01-01')
import matplotlib.pyplot as plt
jan_cel['temperature_2m'].plot(x='lon', y='lat', cmap='jet')
plt.savefig('jan012010.png', dpi=360)
weekly = ds.resample(time='W').mean()
weekly
monthly = ds.resample(time='M').max()
monthly
sub = monthly.sel(lon=slice(0, 150), lat=slice(0, 90), time='2010-03-31')
sub
sub['temperature_2m'].plot(x='lon', y='lat', cmap='jet')
sub.to_netcdf('monthly_max.nc')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0101_xee_intro', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
