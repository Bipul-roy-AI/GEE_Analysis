# Bangladesh adaptation: 0114_xee_growing_season_length
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'agriculture' / '0114_xee_growing_season_length'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0022_growing_season_length.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-119: Growing Season Length, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap
import xarray as xr
import xee
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
collection = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').filterDate('2000', '2020').select('temperature_2m').map(lambda img: img.subtract(273.15).copyProperties(img, img.propertyNames()))
collection.limit(10)
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.27, geometry=BD_ROI)
ds
xr.infer_freq(ds.time)
ds['temperature_2m'].attrs['units'] = 'degC'
ds
import xclim
gsl = xclim.indices.growing_season_length(tas=ds.temperature_2m, thresh='5.0 degC', window=6, mid_date='07-01', freq='YS')
gsl
import matplotlib.pyplot as plt
gsl.plot(x='lon', y='lat', col='time', col_wrap=5, robust=True)
plt.savefig('gsl.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'agriculture', '0114_xee_growing_season_length', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'agriculture')  # explicit upload; requires Drive OAuth scope
