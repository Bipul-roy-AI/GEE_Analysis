# Bangladesh adaptation: 0207_flood_intelligence_5
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'flood' / '0207_flood_intelligence_5'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""05_session5_flood_risk_mapping.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Flood Intelligence Workshop - Session5: Flood Risk Mapping
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
map = geemap.Map()
map
point = BD_ROI
point
province = BD_ROI
map.addLayer(province, {}, 'province')
'# **Image Collections**'
flood = ee.ImageCollection('JRC/CEMS_GLOFAS/FloodHazard/v2_1').filterBounds(province).select(['RP10_depth'], ['flood']).mean()
ndvi = ee.ImageCollection('MODIS/061/MOD13A1').filterDate('2020', '2026').select('NDVI', 'EVI').median()
pr = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').filterDate('2020', '2025').select('pr').mean()
lc = ee.ImageCollection('MODIS/061/MCD12Q1').filterDate('2020', '2025').select('LC_Type1').mode()
dem = ee.Image('USGS/SRTMGL1_003')
dataset = ee.Image.cat([ndvi, pr, lc, dem, flood])
dataset
'# **Image Collection to Xarray**'
from shapely.geometry import shape
from xee import helpers
import xarray as xr
grid_params = helpers.fit_geometry(geometry=shape(province.getInfo()), grid_crs='EPSG:3857', grid_scale=(500, -500))
ds = xr.open_dataset(dataset, engine='ee', **grid_params)
ds = ds.squeeze('time').drop_vars('time') * 1
ds
'# **Image Clip**'
import rioxarray
import geopandas as gpd
province_gdf = geemap.ee_to_gdf(ee.FeatureCollection(province))
province_proj = province_gdf.to_crs('EPSG:3857')
ds_clip = ds.rio.clip(province_proj.geometry, province_proj.crs)
ds_clip.flood.plot(x='x', y='y', robust=True)
'# **Risk Modelling**'
ds_clip['flood_bin'] = (ds_clip.flood > 1).astype(int)
df = ds_clip.to_dataframe().dropna().drop(['spatial_ref', 'flood'], axis=1)
df
x = df.drop('flood_bin', axis=1)
y = df['flood_bin']
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x_train, y_train)
y_pred = model.predict(x_test)
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))
df['risk'] = model.predict_proba(x)[:, 1]
dx = df.to_xarray().sortby(['y', 'x'])
'# **Visualization**'
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
province_proj.plot(ax=ax, alpha=0.5, color='black')
dx.risk.plot(x='x', y='y', robust=True, vmin=0.8, ax=ax)
'# **Risky Area**'
x_res, y_res = dx.rio.resolution()
pixel_size = abs(x_res * y_res)
(dx.risk == 1).sum(dim=['y', 'x']).item() * pixel_size / 1000000.0

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'flood', '0207_flood_intelligence_5', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'flood')  # explicit upload; requires Drive OAuth scope
