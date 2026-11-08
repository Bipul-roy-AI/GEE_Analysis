# Bangladesh adaptation: 0182_xee_visualization_p1
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'methods' / '0182_xee_visualization_p1'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0106_xee_xarray_plot.ipynb
Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-187: Visualization and Plotting (Part -1)

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
point = BD_ROI
point
roi = BD_ROI
map.addLayer(roi, {}, 'roi')
spei = ee.ImageCollection('CSIC/SPEI/2_10').filterDate('2000', '2025').select('SPEI_12_month')
spei
import xarray as xr
ds = xr.open_dataset(spei, engine='ee', crs='EPSG:4326', scale=0.5, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds_season = ds.groupby('time.season').mean('time')
ds_season.SPEI_12_month.plot(x='lon', y='lat', col='season')
shp = geemap.ee_to_gdf(ee.FeatureCollection(roi))
import rioxarray
ds_rename = ds_season.rename({'lon': 'x', 'lat': 'y'})
ds_clip = ds_rename.rio.clip(shp.geometry, shp.crs)
ds_clip.SPEI_12_month.plot.contourf(x='x', y='y', col='season', robust=True, cmap='turbo_r', levels=10)
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 4, figsize=(20, 3.5))
plt.tight_layout(w_pad=2.5)
ax1 = ax[0]
plot = ds_clip.sel(season='DJF').SPEI_12_month.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, ax=ax1)
ax1.set_title('Winter')
ax2 = ax[1]
plot = ds_clip.sel(season='MAM').SPEI_12_month.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, ax=ax2)
ax2.set_title('Spring')
ax3 = ax[2]
plot = ds_clip.sel(season='JJA').SPEI_12_month.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, ax=ax3)
ax3.set_title('Summer')
ax4 = ax[3]
plot = ds_clip.sel(season='SON').SPEI_12_month.plot.contourf(x='x', y='y', robust=True, cmap='turbo_r', levels=10, ax=ax4)
ax4.set_title('Autumn')
plt.savefig('spei_seasonal.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0182_xee_visualization_p1', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
