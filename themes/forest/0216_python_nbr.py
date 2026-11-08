# Bangladesh adaptation: 0216_python_nbr
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'forest' / '0216_python_nbr'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""Untitled0.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-202: Wildfire Severity Analysis using dNBR Index
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
'# **Study Area**'
hansen = ee.Image('UMD/hansen/global_forest_change_2025_v1_13').select('loss', 'lossyear')
wf2023 = hansen.select('loss').eq(1).And(hansen.select('lossyear').eq(23))
import geemap
map = geemap.Map(basemap='SATELLITE')
map.addLayer(wf2023, {}, 'wf2023')
map
roi = BD_ROI
'# **MODIS Image Collection**'
modis = ee.ImageCollection('MODIS/061/MOD09A1').filterDate('2022', '2024').select('sur_refl_b02', 'sur_refl_b07')
modis
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:3857', grid_scale=(500, -500))
ds = xr.open_dataset(modis, engine='ee', **grid_params)
ds = ds.sortby('time') * 0.0001
'# **Normalized Burn Ratio (NBR)**'
nir = ds['sur_refl_b02']
swir = ds['sur_refl_b07']
nbr = (nir - swir) / (nir + swir)
pre_fire = nbr.sel(time='2022').mean(dim='time')
pre_fire.plot(x='x', y='y', robust=True)
post_fire = nbr.sel(time='2023').mean(dim='time')
post_fire.plot(x='x', y='y', robust=True)
dnbr = pre_fire - post_fire
dnbr.plot(x='x', y='y', robust=True)
import numpy as np
result = dnbr.where(dnbr >= 0.1, np.nan)
result.plot(x='x', y='y', robust=True, cmap='turbo')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0216_python_nbr', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
