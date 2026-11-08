# Bangladesh adaptation: 0145_xee_embedding_kmeans
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'landcover' / '0145_xee_embedding_kmeans'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0063_embedding_unsupervised_learning.ipynb

utorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-150: Satellite Embedding Mapping using KMeans Clustering, in Python API (Xee)

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
import ee
import geemap
import xarray as xr
import xee
import rioxarray
None
None
map = geemap.Map(basemap='SATELLITE')
map
roi = BD_ROI
roi
image = ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL').filterDate('2021', '2022').filterBounds(roi).mosaic()
image
ds = xr.open_dataset(image, engine='ee', crs='EPSG:4326', scale=0.001, geometry=BD_ROI)
ds.A01.plot(x='lon', y='lat', robust=True)
df = ds.to_dataframe()
df
from sklearn.cluster import KMeans
model = KMeans(n_clusters=7, random_state=42)
model.fit(df)
df['cluster'] = model.predict(df)
dx = df.to_xarray().sortby(['lat', 'lon'])
dx.cluster.plot(x='lon', y='lat', vmin=0, vmax=6)
output = dx.cluster.isel(time=0).drop_vars('time')
output = output.rio.write_crs('EPSG:4326', inplace=True)
output = output.rio.set_spatial_dims(x_dim='lon', y_dim='lat', inplace=True)
output = output.rio.write_coordinate_system(inplace=True)
output = output.transpose('lat', 'lon')
output.rio.to_raster('embedding_cluster.tif')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'landcover', '0145_xee_embedding_kmeans', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'landcover')  # explicit upload; requires Drive OAuth scope
