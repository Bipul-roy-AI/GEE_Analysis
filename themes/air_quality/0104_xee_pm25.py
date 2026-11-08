# Bangladesh adaptation: 0104_xee_pm25
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'air_quality' / '0104_xee_pm25'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0012_PM25.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-109: PM25 Mapping, using Python API (Xee)

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
col = ee.ImageCollection('NASA/GSFC/MERRA/aer/2').select('DUSCAT25')
time_start = ee.Date('2008')
time_end = ee.Date('2009')
time_dif = time_end.difference(time_start, 'days').round()
time_list = ee.List.sequence(0, ee.Number(time_dif).subtract(1)).map(lambda interval: time_start.advance(interval, 'days'))

def daily_agg(date):
    start_date = ee.Date(date)
    end_date = start_date.advance(1, 'days')
    image = col.filterDate(start_date, end_date).mean()
    return image.set('system:time_start', start_date.millis())
col_daily = ee.ImageCollection(time_list.map(daily_agg))
loc = [42.537376918517644, 24.73555588205892, 65.91628316851765, 40.01810716361305]
ds = xr.open_dataset(col_daily, engine='ee', crs='EPSG:4326', scale=0.5, geometry=BD_ROI)
ds
point = ds.sel(lon=49.217064418517644, lat=31.173987446501265, method='nearest')
point
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(point.time, point.DUSCAT25, ls=':', marker='o', ms=3, color='red')
ax.set_xlabel('date')
ax.set_ylabel('DUSCAT25')
ax.set_title('PM25 Variation')
plt.savefig('pm25.png', dpi=360, bbox_inches='tight')
ds_mean = ds.mean('time')
ds_mean.DUSCAT25.plot(x='lon', y='lat', cmap='coolwarm', robust=True)
ds_mean.DUSCAT25.to_dataframe().describe()
monthly = ds.resample(time='M').mean('time')
monthly
monthly.DUSCAT25.plot(x='lon', y='lat', col='time', col_wrap=4, cmap='coolwarm', robust=True)
plt.savefig('pm25_monthly.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'air_quality', '0104_xee_pm25', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'air_quality')  # explicit upload; requires Drive OAuth scope
