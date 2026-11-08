# Bangladesh adaptation: 0227_climate_bootcamp_session10
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0227_climate_bootcamp_session10'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""10_class10_climate_data_clustering.ipynb


Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Climate Data Analysis Bootcamp using GEE and Python - Session10: Climate Data Clustering
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
roi = BD_ROI
roi
'# **ERA5 Image Collection**'
era = ee.ImageCollection('ECMWF/ERA5_LAND/MONTHLY_AGGR').filterDate('2010', '2020').select('temperature_2m', 'total_precipitation_sum')
era
'# **to Xarray**'
from xee import helpers
from shapely.geometry import shape
import xarray as xr
grid_30km = helpers.fit_geometry(geometry=shape(roi.getInfo()), grid_crs='EPSG:3857', grid_scale=(30000, -30000))
ds = xr.open_dataset(era, engine='ee', **grid_30km)
ds = ds.sortby('time') * 1
ds
'# **PCA**'
import xeofs as xe
pca_model = xe.single.EOF(n_modes=5)
pca_model.fit(ds, dim='time')
comp = pca_model.components()
comp
comp.temperature_2m.plot(x='x', y='y', robust=True, col='mode')
comp.total_precipitation_sum.plot(x='x', y='y', robust=True, col='mode')
'# **Clustring**'
df = comp.to_dataframe().dropna().unstack('mode')
df
from sklearn.cluster import KMeans
cluster_model = KMeans(n_clusters=7)
df['label'] = cluster_model.fit_predict(df)
cluster_map = df['label'].to_xarray().rename('label')
cluster_map.plot.pcolormesh(x='x', y='y', edgecolor='face', alpha=0.8, cmap='turbo')
import numpy as np
cluster_map = cluster_map.reindex(x=ds.x, y=ds.y)
cl3 = ds.where(cluster_map == 2, np.nan).mean(dim=['x', 'y']).to_dataframe()
cl3
cl3.total_precipitation_sum.plot()
cl3.total_precipitation_sum.plot()
class_val = np.unique(cluster_map.values)
class_val = class_val[~np.isnan(class_val)]
class_val
for i in class_val:
    target_class = (cluster_map == i).astype(int).sum(dim=['y', 'x']).item()
    pixel_area = 30000 * 30000 / 1000000.0
    class_area = target_class * pixel_area
    print(f'number of pixels in class {i} is: {target_class}')
    print(f'area of the class {i} is: {class_area} km2')
    print('-----------------------------------')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0227_climate_bootcamp_session10', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
