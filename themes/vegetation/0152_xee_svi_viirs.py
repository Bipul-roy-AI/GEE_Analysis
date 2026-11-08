# Bangladesh adaptation: 0152_xee_svi_viirs
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'vegetation' / '0152_xee_svi_viirs'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0072_svi.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-157: Standardized Vegetation Index (SVI) using Python API (Xee)

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
point = BD_ROI
point
roi = BD_ROI
map.addLayer(roi, {}, 'roi')
evi = ee.ImageCollection('NASA/VIIRS/002/VNP13A1').filterDate('2015', '2025').select('EVI').map(lambda x: x.clip(roi).copyProperties(x, ['system:time_start']))
evi
ds = xr.open_dataset(evi, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.01)
ds = ds.sortby('time') * 1
ds_mean = ds.mean(dim='time')
ds_std = ds.std(dim='time')
svi = (ds - ds_mean) / ds_std
svi_annual = svi.resample(time='Y').mean('time')
import matplotlib.pyplot as plt
svi_annual.EVI.plot(x='lon', y='lat', col='time', col_wrap=5, cmap='turbo_r', robust=True)
plt.savefig('svi_annual.png', dpi=360, bbox_inches='tight')
import netCDF4
svi_annual.to_netcdf('svi_annual_array.nc')
svi_annual_mean = svi_annual.mean(dim=['lon', 'lat'])
svi_annual_df = svi_annual_mean.to_dataframe().dropna()
svi_annual_df.to_csv('svi_annual.csv')
svi_annual_df.plot()
svi_mean = svi.mean(dim=['lon', 'lat'])
svi_mean_df = svi_mean.to_dataframe().dropna()
svi_mean_df.to_csv('svi_16days.csv')
svi_mean_df.plot()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0152_xee_svi_viirs', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
