# Bangladesh adaptation: 0202_flood_intelligence1
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'flood' / '0202_flood_intelligence1'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""01_session1.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Flood Intelligence Workshop - Session1: Flood Detection and Mapping using SAR
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
'# **Study Area**'
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
'# **Sentinel-1 Image Collection (GEE)**'
sen1 = ee.ImageCollection('COPERNICUS/S1_GRD').filterDate('2018', '2020').filterBounds(roi).filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')).filter(ee.Filter.eq('instrumentMode', 'IW')).filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
sen1
'# **GEE Image Collection to Xarray**'
from shapely.geometry import shape
vec = shape(roi.getInfo())
vec
from xee import helpers
grid_params = helpers.fit_geometry(geometry=vec, grid_crs='EPSG:3857', grid_scale=(100, -100))
import xarray as xr
ds = xr.open_dataset(sen1, engine='ee', **grid_params)
ds = ds['VV'].sortby('time') * 1
'# **Flood Detection**'
baseline = ds.median(dim='time')
import hvplot.xarray
baseline.hvplot(x='x', y='y', robust=True, cmap='RdBu_r', height=500)
ds_monthly = ds.resample(time='M').min('time')
ds_anomaly = ds_monthly - baseline
ds_anomaly.mean(dim=['y', 'x']).to_dataframe().plot(marker='o')
flood = ds_anomaly.sel(time='2019-04').squeeze('time').drop_vars('time')
flood.hvplot(x='x', y='y', robust=True, cmap='RdBu_r', height=600)
'# **Visualization**'
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 6))
baseline.plot(ax=ax[0], x='x', y='y', robust=True, cmap='RdBu_r', cbar_kwargs={'orientation': 'horizontal', 'pad': 0.02, 'label': 'Baseline'})
ax[0].tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
ax[0].set_ylabel('')
ax[0].set_xlabel('')
flood.plot(ax=ax[1], x='x', y='y', robust=True, cmap='RdBu_r', cbar_kwargs={'orientation': 'horizontal', 'pad': 0.02, 'label': 'Flood Event'})
ax[1].tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
ax[1].set_ylabel('')
ax[1].set_xlabel('')
plt.tight_layout()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'flood', '0202_flood_intelligence1', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'flood')  # explicit upload; requires Drive OAuth scope
