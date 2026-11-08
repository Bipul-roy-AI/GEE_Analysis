# Bangladesh adaptation: 0201_xee_ndvi_scatterplot
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'vegetation' / '0201_xee_ndvi_scatterplot'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00005_ndvi_scatter_plot_analysis.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-194: NDVI Scatterplot Analysis in Python
This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
None
None
import geemap
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi

def ndvi(img):
    prob = img.select('probability')
    clear_pixels = prob.lt(20)
    sr = img.select('B.*').multiply(0.0001)
    index = sr.normalizedDifference(['B8', 'B4']).rename('ndvi')
    bands = sr.select(['B4', 'B8'], ['red', 'nir'])
    stack = ee.Image.cat([bands, index]).updateMask(clear_pixels)
    return stack
sen2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').linkCollection(ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY'), 'probability').filterDate('2025', '2026').filterBounds(roi).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).map(ndvi).median()
sen2
from shapely.geometry import shape
vec = shape(roi.getInfo())
vec
from xee import helpers
grid_params = helpers.fit_geometry(geometry=vec, grid_crs='EPSG:3857', grid_scale=(30, -30))
import xarray as xr
ds = xr.open_dataset(sen2, engine='ee', **grid_params)
ds = ds.squeeze('time').drop_vars('time') * 1
import matplotlib.pyplot as plt
ds
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
ds.red.plot(x='x', y='y', ax=ax[0], robust=True)
ds.nir.plot(x='x', y='y', ax=ax[1], robust=True)
ds.ndvi.plot(x='x', y='y', ax=ax[2], cmap='RdYlGn')
plt.tight_layout()
red_vals = ds.red.values.flatten()
nir_vals = ds.nir.values.flatten()
ndvi_vals = ds.ndvi.values.flatten()
fig, ax = plt.subplots(figsize=(6, 4))
scatter = ax.scatter(x=red_vals, y=nir_vals, c=ndvi_vals, cmap='RdYlGn')
cbar = fig.colorbar(scatter, ax=ax, cmap='RdYlGn', pad=0.02)
cbar.set_label('NDVI', fontsize=12)
cbar.ax.tick_params(labelsize=12)
ax.set_ylabel('NIR Reflectance', fontsize=12)
ax.set_xlabel('Red Reflectance', fontsize=12)
ax.set_title('NIR-RED Scatter Plot', fontsize=15)
ax.tick_params(axis='both', direction='in', right=True, top=True, labelsize=12)
ax.grid(ls=':', alpha=0.7)
plt.savefig('ndvi_scatter.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0201_xee_ndvi_scatterplot', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
