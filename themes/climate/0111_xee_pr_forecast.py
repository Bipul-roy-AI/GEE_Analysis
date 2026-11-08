# Bangladesh adaptation: 0111_xee_pr_forecast
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0111_xee_pr_forecast'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0019_precipitaion_forecast.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-116: Precipitation Forecast, using Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
import ee
import geemap as gee
import xarray as xr
import xee
None
None
map = gee.Map(basemap='SATELLITE')
map
roi = BD_ROI
collection = ee.ImageCollection('NOAA/PERSIANN-CDR').filterDate('2005', '2024')
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.27)
ds
ds_mean = ds.mean('time')
ds_mean
ds_mean.precipitation.plot(x='lon', y='lat', robust=True)
ds_var = ds.var('time')
ds_var.precipitation.plot(x='lon', y='lat', robust=True)
monthly = ds.resample(time='M').sum()
monthly
point = monthly.sel(lon=48.73310048088049, lat=31.808809525085334, method='nearest')
point
df = point.to_dataframe()['precipitation']
df
df.plot()
from statsmodels.tsa.statespace.sarimax import SARIMAX
model = SARIMAX(df, order=(1, 1, 1), seasonal_order=(1, 1, 0, 48))
result = model.fit()
forecast = result.get_forecast(steps=10 * 12)
df.plot()
forecast.predicted_mean.plot()
forecast.predicted_mean.to_csv('pr_forecasted.csv')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0111_xee_pr_forecast', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
