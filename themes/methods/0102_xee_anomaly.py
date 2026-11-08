# Bangladesh adaptation: 0102_xee_anomaly
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0102_xee_anomaly'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0010_anomaly_mapping.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-107: Anomaly Mapping, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!

"""
import ee
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import xee
None
None
sm = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select('soil').filterDate('2000', '2024')
sm_ds = xr.open_dataset(sm, engine='ee', geometry=BD_ROI)
sm_ds
sm_annual = sm_ds.resample(time='YE').mean('time') * 0.1
sm_annual
sm_mean = sm_annual.mean('time')
sm_mean
sm_mean['soil'].plot(x='lon', y='lat', cmap='jet', figsize=(7, 4), vmin=10, vmax=100)
plt.savefig('sm_mean.png', dpi=360)
anomaly = sm_annual - sm_mean
anomaly
shp = __import__('geemap').ee_to_gdf(BD_COUNTRY)
shp
shp.crs
countries = shp.to_crs('EPSG:4326')
countries.crs
sub = anomaly.sel(lon=slice(0, 180), lat=slice(0, 90), time='2020-12-31')
fig, ax = plt.subplots(figsize=(9, 4))
sub['soil'].plot(x='lon', y='lat', cmap='coolwarm_r', vmin=-10, vmax=10, ax=ax)
countries.boundary.plot(ax=ax, lw=1, color='black')
plt.savefig('sm_anomaly.png', dpi=360)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0102_xee_anomaly', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
