# Bangladesh adaptation: 0171_xee_pr_downscale
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0171_xee_pr_downscale'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0094_pr_downscale_dl.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-176: Precipitation Downscaling using Deep Learning Model

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
roi = BD_ROI
roi
time_start = ee.Date('2002')
time_end = ee.Date('2025')
time_dif = time_end.difference(time_start, 'month').round()
time_list = ee.List.sequence(0, ee.Number(time_dif).subtract(1)).map(lambda x: time_start.advance(x, 'month'))

def monthly(date_list, col):
    start_date = ee.Date(date_list)
    end_date = start_date.advance(1, 'month')
    col_agg = col.filterDate(start_date, end_date).mean()
    return col_agg.set('system:time_start', start_date.millis())
pr = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').filterDate(time_start, time_end).select(['precipitation'], ['pr'])
veg = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate(time_start, time_end).select(['NDVI', 'EVI'], ['ndvi', 'evi'])
temp = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(time_start, time_end).select(['LST_Day_1km', 'LST_Night_1km'], ['temp_day', 'temp_night'])
et = ee.ImageCollection('MODIS/061/MOD16A2GF').filterDate(time_start, time_end).select(['ET'], ['et'])
veg_monthly = ee.ImageCollection(time_list.map(lambda x: monthly(x, veg)))
temp_monthly = ee.ImageCollection(time_list.map(lambda x: monthly(x, temp)))
et_monthly = ee.ImageCollection(time_list.map(lambda x: monthly(x, et)))
pr_monthly = ee.ImageCollection(time_list.map(lambda x: monthly(x, pr)))
landcover = ee.ImageCollection('MODIS/061/MCD12Q1').filterDate(time_start, time_end).mode().select(['LC_Type1'], ['lc'])
topo = ee.Image('USGS/GTOPO30').rename('dem')
collection = veg_monthly.combine(temp_monthly).combine(et_monthly).combine(pr_monthly).map(lambda x: x.addBands(landcover).addBands(topo))
collection
import xarray as xr
ds10km = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.1, geometry=BD_ROI)
ds10km = ds10km.sortby('time') * 1
df10km = ds10km.to_dataframe().dropna()
df10km
from sklearn.preprocessing import StandardScaler
x10km = df10km[['ndvi', 'evi', 'temp_day', 'temp_night', 'et', 'lc', 'dem']]
scaler_x10km = StandardScaler()
x10km_standard = scaler_x10km.fit_transform(x10km)
x10km_standard
y10km.values.reshape(-1, 1).shape
y10km = df10km['pr']
scaler_y10km = StandardScaler()
y10km_standard = scaler_y10km.fit_transform(y10km.values.reshape(-1, 1))
y10km_standard
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x10km_standard, y10km_standard, test_size=0.2, random_state=42)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
x10km.shape[1]
model = Sequential()
model.add(Dense(64, activation='relu', input_dim=x10km.shape[1]))
model.add(Dense(32, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.fit(x_train, y_train, batch_size=8, epochs=50, validation_split=0.2, verbose=1)
model_evaluation = model.evaluate(x_test, y_test)
ds1km = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', geometry=BD_ROI, scale=0.01)
ds1km = ds1km.sortby('time') * 1
df1km = ds1km.to_dataframe().dropna()
x1km = df1km[['ndvi', 'evi', 'temp_day', 'temp_night', 'et', 'lc', 'dem']]
scaler_x1km = StandardScaler()
x1km_standard = scaler_x1km.fit_transform(x1km)
x1km_standard
y1km = df1km['pr']
scaler_y1km = StandardScaler()
y1km_standard = scaler_y1km.fit_transform(y1km.values.reshape(-1, 1))
y1km_standard
df1km['pr1km'] = scaler_y1km.inverse_transform(model.predict(x1km_standard))
result = df1km[['pr', 'pr1km']].to_xarray().sortby(['time', 'lat', 'lon'])
result_sub = result.sel(time='2020')
result_sub.pr.plot(x='lon', y='lat', col='time', robust=True, col_wrap=6)
result_sub.pr1km.plot(x='lon', y='lat', col='time', robust=True, col_wrap=6)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0171_xee_pr_downscale', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
