# Bangladesh adaptation: 0191_xee_cartopy
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0191_xee_cartopy'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00001_cartopy.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-190: Global Mapping using Cartopy

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map()
map
roi = BD_ROI
roi
pdsi = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate('2000', '2026').select('pdsi').mean()
pdsi
import xarray as xr
ds = xr.open_dataset(pdsi, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=1)
ds = ds.squeeze('time').drop_vars('time') * 0.01
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
ds
plt.figure()
ax = plt.axes(projection=ccrs.EqualEarth())
ds.pdsi.plot(x='lon', y='lat', transform=ccrs.PlateCarree(), robust=True, cmap='RdBu', levels=10, cbar_kwargs={'orientation': 'horizontal', 'pad': 0.07, 'shrink': 0.7})
ax.coastlines(resolution='110m')
ax.set_global()
ax.gridlines(draw_labels=True, alpha=0.5)
ax.set_title('Global Drought Map (2000 - 2025)', fontsize=18)
plt.savefig('drought_map.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0191_xee_cartopy', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
