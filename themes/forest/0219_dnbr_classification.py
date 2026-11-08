# Bangladesh adaptation: 0219_dnbr_classification
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'forest' / '0219_dnbr_classification'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00015_dnbr_classification.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-203: Wildfire Burn Severity Classification using dNBR Index
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
hansen = ee.Image('UMD/hansen/global_forest_change_2025_v1_13').select('loss', 'lossyear')
target = hansen.select('loss').eq(1).And(hansen.select('lossyear').eq(23))
map = geemap.Map(basemap='SATELLITE')
map.addLayer(target, {}, 'target')
map
roi = BD_ROI
roi
'# **MODIS Image Collection**'
modis = ee.ImageCollection('MODIS/061/MOD09A1').filterDate('2022', '2024').select(['sur_refl_b02', 'sur_refl_b07'], ['nir', 'swir'])
modis
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:3857', grid_scale=(500, -500))
ds = xr.open_dataset(modis, engine='ee', **grid_params)
ds = ds.sortby('time') * 0.0001
'# **NBR**'
nbr = (ds.nir - ds.swir) / (ds.nir + ds.swir)
nbr = xr.Dataset({'index': nbr})
import numpy as np
pre_fire = nbr.sel(time='2022').mean('time')
post_fire = nbr.sel(time='2023').mean('time')
dnbr = pre_fire - post_fire
burned = dnbr.where(dnbr >= 0.1, np.nan)
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 4, figsize=(15, 3))
pre_fire.index.plot(ax=ax[0], x='x', y='y', robust=True)
post_fire.index.plot(ax=ax[1], x='x', y='y', robust=True)
dnbr.index.plot(ax=ax[2], x='x', y='y', robust=True)
burned.index.plot(ax=ax[3], x='x', y='y', robust=True)
plt.tight_layout()
burn_level = xr.where(burned < 0.27, 1, xr.where(burned < 0.44, 2, xr.where(burned < 0.66, 3, 4)))
burn_level = burn_level.where(burned.notnull())
burn_level.index.plot(x='x', y='y')
plt.hist(burn_level.index.values.flatten())
plt.show()

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0219_dnbr_classification', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
