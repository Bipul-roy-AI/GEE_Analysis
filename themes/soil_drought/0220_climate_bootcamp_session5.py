# Bangladesh adaptation: 0220_climate_bootcamp_session5
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0220_climate_bootcamp_session5'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""05_class5_spei_mapping_classification.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session5: Drought Monitroing using SPEI
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
'# **SPEI Image Collection**'
spei = ee.ImageCollection('CSIC/SPEI/2_11').filterDate('2000', '2026').select('SPEI_12_month')
spei
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.55, -0.55))
ds = xr.open_dataset(spei, engine='ee', **grid_params)
ds = ds.sortby('time') * 1
'# **Visualization**'
spei_mean = ds.mean(dim='time')
spei_mean.SPEI_12_month.plot.contourf(x='x', y='y', robust=True, figsize=(7, 3), levels=10)
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.EqualEarth()})
spei_mean.SPEI_12_month.plot.contourf(x='x', y='y', ax=ax, transform=ccrs.PlateCarree(), robust=True, levels=10, cbar_kwargs={'orientation': 'horizontal', 'shrink': 0.5, 'pad': 0.07})
ax.set_global()
ax.coastlines()
ax.gridlines(draw_labels=True, alpha=0.5, ls=':')
ax.set_title('Global Drought Average [2000 - 2025]', fontsize=15)
plt.savefig('spei_map.png', dpi=360, bbox_inches='tight')
'# **Classification**'
spei_classes = xr.where(ds >= 2.0, 3, xr.where(ds >= 1.5, 2, xr.where(ds >= 1.0, 1, xr.where(ds > -1, 0, xr.where(ds >= -1.5, -1, xr.where(ds >= -2, -2, -3))))))
spei_classes = spei_classes.where(ds.notnull())
spei_classes.isel(time=10).SPEI_12_month.plot(x='x', y='y', figsize=(10, 5))
spei_annual = spei_classes.resample(time='YE').median('time')
spei_annual.sel(time='2024').SPEI_12_month.plot(x='x', y='y', figsize=(10, 5))
point = spei_annual.sel(x=-81.57695312500002, y=38.431816872255325, method='nearest')
point.to_dataframe()['SPEI_12_month'].plot()
'# **Area Calculation**'
spei2024 = spei_annual.sel(time='2024')
classes = [-3, -2, -1, 0, 1, 2, 3]
for i in classes:
    class_i_pixels = spei2024.SPEI_12_month.isin(i).astype(int).sum(dim=['y', 'x']).item()
    pixel_area = 55 * 55
    class_i_area = class_i_pixels * pixel_area
    print(f'class {i} area {class_i_area} km2')
plt.hist(spei2024.SPEI_12_month.values.flatten())

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0220_climate_bootcamp_session5', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
