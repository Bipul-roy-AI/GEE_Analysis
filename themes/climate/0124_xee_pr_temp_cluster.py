# Bangladesh adaptation: 0124_xee_pr_temp_cluster
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'climate' / '0124_xee_pr_temp_cluster'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0036_pr_temp_clustering.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-129: Precipiotation Temporal Clustering, in Python API (Xee)

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
pr = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07').select('precipitation').filterDate('2000', '2025')
pr
ds = xr.open_dataset(pr, engine='ee', scale=0.1, crs='EPSG:4326', geometry=BD_ROI)
ds = ds * 730.0
ds
point = ds.sel(lon=46.99490187913968, lat=36.71625745730625, method='nearest')
point
df = point.to_dataframe()['precipitation'].reset_index()
df
from sklearn.cluster import KMeans
model = KMeans(n_clusters=4, random_state=42)
df['class'] = model.fit_predict(df[['precipitation']])
df
df_index = df.set_index('time')
df_index
df_index.groupby('class').describe()
label = {0: 'heavy', 1: 'moderate', 2: 'high', 3: 'low'}
df_index['label'] = df_index['class'].map(label)
import pandas as pd
df_index
df_index.to_csv('pr_dataset.csv')
colors = {'heavy': 'red', 'high': 'orange', 'moderate': 'green', 'low': 'blue'}
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 3))
for label, group in df_index.groupby('label'):
    ax.bar(group.index, group.precipitation, label=label, width=20, color=colors.get(label))
ax.legend(loc='upper left')
ax.set_ylabel('precipitation (mm/month)')
plt.savefig('pr_clustering.png', dpi=360, bbox_inches='tight')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0124_xee_pr_temp_cluster', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
