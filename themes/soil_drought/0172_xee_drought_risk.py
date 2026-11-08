# Bangladesh adaptation: 0172_xee_drought_risk
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'soil_drought' / '0172_xee_drought_risk'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0095_drought_risk.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-177: Drought Risk Mapping using Random Forest Modelling

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
water_mask = ee.ImageCollection('MODIS/061/MCD12Q1').mode().select('LC_Type1').eq(17).Not()
collection = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate('2000', '2025').select('aet', 'pr', 'soil', 'tmmn', 'tmmx', 'pdsi').map(lambda x: x.updateMask(water_mask).copyProperties(x, ['system:time_start']))
collection
import xarray as xr
ds = xr.open_dataset(collection, engine='ee', crs='EPSG:4326', scale=0.5, geometry=BD_ROI)
ds
ds = ds.sortby('time') * 1
df = ds.to_dataframe().dropna()
x = df[['aet', 'pr', 'soil', 'tmmn', 'tmmx']]
x
df['drought'] = (df['pdsi'] * 0.01 < -2.0).astype(int)
df
y = df['drought']
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=500, random_state=42)
model.fit(x_train, y_train)
y_prob = model.predict_proba(x_test)[:, 1]
from sklearn.metrics import roc_auc_score
test = roc_auc_score(y_test, y_prob)
test
df['risk'] = model.predict_proba(x)[:, 1]
dx = df.to_xarray().sortby(['time', 'lat', 'lon'])
dx
risk_map = dx.risk.median(dim='time')
risk_map.plot.contourf(x='lon', y='lat', robust=True, cmap='turbo', levels=20)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'soil_drought', '0172_xee_drought_risk', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'soil_drought')  # explicit upload; requires Drive OAuth scope
