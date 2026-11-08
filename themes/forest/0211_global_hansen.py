# Bangladesh adaptation: 0211_global_hansen
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'forest' / '0211_global_hansen'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00010_hansen_forest_mapping2.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutotrial-199: Global Forest Loss Mapping using Hansen Product
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
None
None
'# ***Study Area***'
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
'# ***Hansen GEE Image***'
hansen = ee.Image('UMD/hansen/global_forest_change_2025_v1_13').select('lossyear', 'loss')
hansen
'# ***to Xarray Format***'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.5, -0.5))
ds = xr.open_dataset(hansen, engine='ee', **grid_params)
ds = ds.squeeze('time').drop_vars('time') * 1
'# ***Loss Mask***'
import numpy as np
ds_loss = ds['loss'].where(ds['loss'] == 1, np.nan)
ds_lossyear = ds['lossyear'].where(ds['loss'] == 1, np.nan)
'# ***Visualization***'
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(15, 10), subplot_kw={'projection': ccrs.EqualEarth()})
ds_loss.plot(ax=ax[0], x='x', y='y', cmap='Reds', transform=ccrs.PlateCarree(), cbar_kwargs={'orientation': 'horizontal', 'pad': 0.05, 'shrink': 0.6})
ax[0].set_global()
ax[0].coastlines()
ax[0].set_title('Loss Area')
ax[0].gridlines(draw_labels=True, ls=':')
ds_lossyear.plot.contourf(ax=ax[1], x='x', y='y', transform=ccrs.PlateCarree(), robust=True, cmap='turbo', cbar_kwargs={'orientation': 'horizontal', 'pad': 0.05, 'shrink': 0.6})
ax[1].set_global()
ax[1].coastlines()
ax[1].set_title('Loss Year')
ax[1].gridlines(draw_labels=True, ls=':')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0211_global_hansen', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
