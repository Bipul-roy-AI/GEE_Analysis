# Bangladesh adaptation: 0158_xee_landsat_et_model
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'soil_drought' / '0158_xee_landsat_et_model'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0081_openet_modelling.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-163: Landsat Evapotranspiration Modelling using Python API (Xee)

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
time_start = ee.Date('2024')
time_end = ee.Date('2025')
time_dif = time_end.difference(time_start, 'month').round()
time_list = ee.List.sequence(0, ee.Number(time_dif).subtract(1)).map(lambda x: time_start.advance(x, 'month'))

def monthly(date, col):
    start_date = ee.Date(date)
    end_date = start_date.advance(1, 'month')
    col_img = col.filterDate(start_date, end_date).median()
    return col_img.set('system:time_start', start_date.millis())
et = ee.ImageCollection('OpenET/ENSEMBLE/CONUS/GRIDMET/MONTHLY/v2_0').filterDate(time_start, time_end).filterBounds(roi).select('et_ensemble_mad')
monthly_et = ee.ImageCollection(time_list.map(lambda x: monthly(x, et)))

def oli(img):
    qa = img.select('QA_PIXEL')
    dil = qa.bitwiseAnd(1 << 1).neq(0)
    cir = qa.bitwiseAnd(1 << 2).neq(0)
    clo = qa.bitwiseAnd(1 << 3).neq(0)
    sha = qa.bitwiseAnd(1 << 4).neq(0)
    mask = dil.Or(cir).Or(clo).Or(sha)
    sr = img.select('SR_.*').multiply(2.75e-05).add(-0.2)
    ndvi = sr.normalizedDifference(['SR_B5', 'SR_B4']).rename('ndvi')
    temp = img.select('ST_B10').multiply(0.00341802).add(149).rename('lst')
    return ndvi.addBands(temp).updateMask(mask.Not()).copyProperties(img, ['system:time_start'])
l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(time_start, time_end).filterBounds(roi).map(oli)
l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate(time_start, time_end).filterBounds(roi).map(oli)
landsat = l8.merge(l9).sort('system:time_start')
landsat_monthly = ee.ImageCollection(time_list.map(lambda x: monthly(x, landsat)))
collection = landsat_monthly.combine(monthly_et)
collection
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds
ds = ds.sortby('time') * 1
ndvi_et = xr.corr(ds.ndvi, ds.et_ensemble_mad, dim='time')
ndvi_et.plot(x='lon', y='lat', robust=True)
temp_et = xr.corr(ds.lst, ds.et_ensemble_mad, dim='time')
temp_et.plot(x='lon', y='lat', robust=True)
df = ds.to_dataframe().dropna()
df
from sklearn.model_selection import train_test_split
x = df[['ndvi', 'lst']]
y = df['et_ensemble_mad']
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42, test_size=0.2)
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(x_train, y_train)
from sklearn.metrics import mean_squared_error, r2_score
y_pred = model.predict(x_test)
r2 = r2_score(y_test, y_pred)
r2
import numpy as np
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
rmse
df['et_pred'] = model.predict(df[['ndvi', 'lst']])
dfx = df.to_xarray().sortby(['lon', 'lat', 'time'])
dfx.et_ensemble_mad.plot(x='lon', y='lat', robust=True, col='time', col_wrap=6)
dfx.et_pred.plot(x='lon', y='lat', robust=True, col='time', col_wrap=6)
map2 = geemap.Map(basemap='SATELLITE')
map2
roi2 = BD_ROI
roi2
l8_2 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(time_start, time_end).filterBounds(roi2).map(oli)
l9_2 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2').filterDate(time_start, time_end).filterBounds(roi2).map(oli)
landsat2 = l8_2.merge(l9_2).sort('system:time_start')
landsat_monthly2 = ee.ImageCollection(time_list.map(lambda x: monthly(x, landsat2)))
landsat_monthly2
ds2 = xr.open_dataset(landsat_monthly2, engine='ee', crs='EPSG:4326', scale=0.0003, geometry=BD_ROI)
ds2 = ds2.sortby('time') * 1
df2 = ds2.to_dataframe()
df2
df2['et'] = model.predict(df2[['ndvi', 'lst']])
dfx2 = df2.to_xarray().sortby(['lat', 'lon', 'time'])
dfx2.et.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True)
et_mean = dfx2.mean(dim=['lat', 'lon']).to_dataframe()['et']
et_mean.plot(marker='o')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0158_xee_landsat_et_model', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
