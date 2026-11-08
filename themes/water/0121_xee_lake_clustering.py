# Bangladesh adaptation: 0121_xee_lake_clustering
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'water' / '0121_xee_lake_clustering'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0030_lake_clustering.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-126: Lake Mapping using Clustering Technique, in Python API (Xee)

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
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(roi).filterDate('2021', '2025')

def ndwi(img):
    qa = img.select('QA_PIXEL')
    cloud = qa.bitwiseAnd(1 << 3).neq(0)
    cirrus = qa.bitwiseAnd(1 << 2).neq(0)
    shadow = qa.bitwiseAnd(1 << 4).neq(0)
    mask = cloud.Or(cirrus).Or(shadow)
    bands = img.select('SR.*').multiply(2.75e-05).add(-0.2)
    index = bands.normalizedDifference(['SR_B3', 'SR_B5']).rename('ndwi')
    return index.updateMask(mask.Not()).copyProperties(img, img.propertyNames())
landsat_ndwi = landsat.map(ndwi)
ds = xr.open_dataset(landsat_ndwi, engine='ee', crs='EPSG:4326', scale=0.003, geometry=BD_ROI)
ds
ds_mean = ds.mean('time')
ds_mean.ndwi.plot(x='lon', y='lat', robust=True)
from sklearn.cluster import KMeans
model = KMeans(n_clusters=2, random_state=42)
df = ds_mean.to_dataframe()
df['clustering'] = model.fit_predict(df[['ndwi']])
xarr = df.to_xarray().sortby('lon').sortby('lat')
xarr
xarr.clustering.plot(x='lon', y='lat', cmap='Blues')
lake_pixels = (xarr.clustering == 0).sum(dim=['lon', 'lat'])
lake_area = lake_pixels * 300 * 300 / 1000000.0
lake_area

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'water', '0121_xee_lake_clustering', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'water')  # explicit upload; requires Drive OAuth scope
