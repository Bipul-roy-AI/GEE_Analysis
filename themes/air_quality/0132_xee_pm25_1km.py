# Bangladesh adaptation: 0132_xee_pm25_1km
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'air_quality' / '0132_xee_pm25_1km'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0047_pm25_1km.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-137: High Resolution PM2.5 Analysis in Python API (Xee)

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
daily_col = ee.ImageCollection('projects/sat-io/open-datasets/GHAP/GHAP_D1K_PM25').filterDate('2017', '2022')
daily_col
daily_ds = xr.open_dataset(daily_col, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.001)
daily_ds
daily_ave = daily_ds.mean(dim=['lat', 'lon']) * 0.1
daily_ave
daily_df = daily_ave.to_dataframe()
daily_df.to_csv('daily_pm25.csv')
daily_df.plot()
monthly_col = ee.ImageCollection('projects/sat-io/open-datasets/GHAP/GHAP_M1K_PM25').filterDate('2017', '2023')
monthly_ds = xr.open_dataset(monthly_col, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
monthly_ds
month_mean = monthly_ds.groupby('time.month').mean('time') * 0.1
import matplotlib.pyplot as plt
month_mean.b1.plot(x='lon', y='lat', col='month', robust=True, col_wrap=4, cmap='OrRd')
plt.savefig('monthly_pm25.png', dpi=360, bbox_inches='tight')
monthly_ave = monthly_ds.mean(dim=['lat', 'lon']) * 0.1
monthly_ave
monthly_df = monthly_ave.to_dataframe()
monthly_df.plot()
annual_ds = monthly_ds.resample(time='YE').mean('time') * 0.1
annual_ds.b1.plot(x='lon', y='lat', robust=True, col='time', col_wrap=3, cmap='OrRd')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'air_quality', '0132_xee_pm25_1km', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'air_quality')  # explicit upload; requires Drive OAuth scope
