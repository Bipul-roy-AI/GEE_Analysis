# Bangladesh adaptation: 0231_terrain_metrics
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'terrain' / '0231_terrain_metrics'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""00020_terrain_metrics.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-207: Terrain Metrics using Xarray - Spatial
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
'# **DEM**'
srtm = ee.Image('USGS/SRTMGL1_003')
srtm
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_100m = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:4326', grid_scale=(0.001, -0.001))
ds = xr.open_dataset(srtm, engine='ee', **grid_100m)
ds = ds.squeeze('time').drop_vars('time') * 1
ds
'# **Elevation**'
ds.elevation.plot(x='x', y='y', robust=True, cmap='terrain')
'# **Xarray Spatial**'
from xrspatial import slope, aspect, tpi, tri, landforms
ds['slope'] = slope(ds.elevation)
ds.slope.plot(x='x', y='y', robust=True)
ds['aspect'] = aspect(ds.elevation)
ds['aspect'].plot(x='x', y='y', robust=True)
ds['tpi'] = tpi(ds.elevation)
ds['tpi'].plot(x='x', y='y', robust=True)
ds['tri'] = tri(ds.elevation)
ds['tri'].plot(x='x', y='y', robust=True)
ds['landforms'] = landforms(ds.elevation)
ds['landforms'].plot(x='x', y='y', robust=True, cmap='turbo')
import hvplot.xarray
ds['landforms'].hvplot(x='x', y='y', robust=True, cmap='turbo', height=500)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'terrain', '0231_terrain_metrics', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'terrain')  # explicit upload; requires Drive OAuth scope
