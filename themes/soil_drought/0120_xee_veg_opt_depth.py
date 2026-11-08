# Bangladesh adaptation: 0120_xee_veg_opt_depth
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0120_xee_veg_opt_depth'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-125: Vegetation Optical Depth Product, in Python API (Xee)

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
map = geemap.Map()
map
point = BD_ROI
point
feature = BD_COUNTRY
map2 = geemap.Map()
map2.centerObject(feature, 5)
map2.addLayer(feature, {}, 'basin')
map2
collection = ee.ImageCollection('projects/sat-io/open-datasets/VODCA/L_BAND_V2').filterDate('2015', '2020')
collection
ds = xr.open_dataset(collection, engine='ee', scale=0.25, crs='EPSG:4326', geometry=BD_ROI)
ds
annual = ds.resample(time='YE').mean('time')
annual.VOD.plot(x='lon', y='lat', col='time', robust=True, col_wrap=3)
month = ds.groupby('time.month').mean('time')
import matplotlib.pyplot as plt
month.VOD.plot(x='lon', y='lat', col='month', col_wrap=4, robust=True)
plt.savefig('VOD.png', dpi=360, bbox_inches='tight')
ds_sub = ds.sel(lat=59.530075111125456, lon=31.23284642583383, method='nearest')
ds_sub
ds_sub.VOD.plot()
import netCDF4
annual.to_netcdf('annual.nc')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0120_xee_veg_opt_depth', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
