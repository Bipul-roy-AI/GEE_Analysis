# Bangladesh adaptation: 0105_xee_correlation_map
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'methods' / '0105_xee_correlation_map'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0013_correlation_map.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-110: Corraltion Map, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!

"""
import ee
import xarray as xr
import xee
None
None
col = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate('2010', '2020').select('pr', 'tmmn', 'tmmx')
loc = [41.86012129914674, 25.315629595884804, 66.20582442414674, 39.902491623606075]
ds = xr.open_dataset(col, engine='ee', crs='EPSG:4326', scale=0.05, geometry=BD_ROI)
ds
pr_annual = ds.pr.resample(time='YE').sum('time')
pr_annual
import matplotlib.pyplot as plt
pr_annual.plot(x='lon', y='lat', cmap='Blues', col='time', col_wrap=5, robust=True)
temp = ((ds.tmmn + ds.tmmx) / 2 * 0.1).round(2).rename('temp')
temp
temp_annual = temp.resample(time='YE').mean('time')
temp_annual
temp_annual.plot(x='lon', y='lat', cmap='coolwarm', robust=True, col='time', col_wrap=5)
cor_map = xr.corr(temp_annual, pr_annual, dim='time')
cor_map
cor_map.plot(x='lon', y='lat', robust=True)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'methods', '0105_xee_correlation_map', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'methods')  # explicit upload; requires Drive OAuth scope
