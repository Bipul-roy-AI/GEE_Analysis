# Bangladesh adaptation: 0222_forest_loss_drivers
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'forest' / '0222_forest_loss_drivers'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00016_forest_loss_drivers.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-204: Forest Loss Drivers Mapping using Google Deep Mind
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
map = geemap.Map()
map
roi = BD_ROI
roi
'# **Forest Loss Drivers**'
img = ee.Image('projects/landandcarbon/assets/wri_gdm_drivers_forest_loss_1km/v1_3_2001_2025').select('classification')
img
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(1, -1))
ds = xr.open_dataset(img, engine='ee', **grid_params)
ds = ds.squeeze('time').drop_vars('time') * 1
'# **Visualization**'
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
ds
fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.Robinson()})
ds.classification.plot(ax=ax, x='x', y='y', robust=True, cmap='turbo', transform=ccrs.PlateCarree(), cbar_kwargs={'orientation': 'horizontal', 'shrink': 0.4, 'pad': 0.07})
ax.set_global()
ax.coastlines()
ax.gridlines(draw_labels=True, alpha=0.5, ls=':')
ax.set_title('Global Forest Loss Drivers', fontsize=15)
plt.savefig('forest_drivers.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'forest', '0222_forest_loss_drivers', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'forest')  # explicit upload; requires Drive OAuth scope
