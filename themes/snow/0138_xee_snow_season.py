# Bangladesh adaptation: 0138_xee_snow_season
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'snow' / '0138_xee_snow_season'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0054_snow_start_end.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-143: Snow Cover, Start Day and End Day, in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xee
import xarray as xr
None
None
map = geemap.Map(basemap='TERRAIN')
map
roi = BD_ROI
roi
collection = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR').filterDate('2010', '2020').select('snow_cover')
collection.limit(10)
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.11, geometry=BD_ROI)
ds.snow_cover.attrs['units'] = 'kg m-2'
ds
from xclim.indicators.land import snw_season_start, snw_season_end
snow_start = snw_season_start(snw=ds.snow_cover, thresh='4 kg m-2', window=14, freq='YS-JAN')
snow_start.plot(x='lon', y='lat', col='time', col_wrap=5, cmap='Spectral', robust=True)
snow_end = snw_season_end(snw=ds.snow_cover, thresh='4 kg m-2', window=14, freq='YS-JAN')
import matplotlib.pyplot as plt
snow_end.plot(x='lon', y='lat', col='time', col_wrap=5, cmap='Spectral', robust=True)
plt.savefig('snow_end.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'snow', '0138_xee_snow_season', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'snow')  # explicit upload; requires Drive OAuth scope
