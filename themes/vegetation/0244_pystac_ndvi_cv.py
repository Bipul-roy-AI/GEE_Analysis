# Bangladesh adaptation: 0244_pystac_ndvi_cv
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'vegetation' / '0244_pystac_ndvi_cv'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""0015_ndvi_coef.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: PySTAC Tutorial-5: Sentinel-2 NDVI Coefficient of Variation Analysis using Python
This code is part of a tutorial series on python eo programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor

"""
from pystac_client import Client
catalog = Client.open('https://earth-search.aws.element84.com/v1')
for collection in catalog.get_collections():
    print(collection.id)
roi = [45.734485, 36.85907, 45.805873, 36.914839]
search = catalog.search(collections=['sentinel-2-c1-l2a'], bbox=roi, datetime='2023/2025', query={'eo:cloud_cover': {'lt': '45'}})
items = search.item_collection()
len(items)
items[0].assets.keys()
import stackstac
ds = stackstac.stack(items, assets=['nir', 'red', 'scl'], bounds_latlon=roi, epsg=3857, resolution=10)
ds_clean = ds.to_dataset('band').reset_coords(drop=True).drop_attrs()
import rioxarray
ds_clean = ds_clean.rio.write_crs('EPSG:3857').rio.clip([BD_ROI.getInfo()], crs='EPSG:4326')
cloud = ds_clean.scl.isin([3, 8, 9, 10]).astype(int)
veg = ds_clean.scl.isin(4).astype(int)
ds_mask = ds_clean[['nir', 'red']].where(cloud == 0)
ds_veg = ds_mask.where(veg)
nir = ds_veg['nir']
red = ds_veg['red']
ndvi = (nir - red) / (nir + red)
ndvi_mean = ndvi.mean(dim=['time'])
ndvi_std = ndvi.std(dim=['time'])
cv = ndvi_std / ndvi_mean * 100
cv
from dask.diagnostics import ProgressBar
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
import logging
logging.getLogger('rasterio._env').setLevel(logging.ERROR)
with ProgressBar():
    cv = cv.compute()
cv.plot(robust=True)
import rioxarray
out = cv.copy()
out = out.rio.write_crs('EPSG:3857')
out = out.rio.set_spatial_dims(x_dim='x', y_dim='y')
out = out.rio.write_coordinate_system(inplace=True)
out.rio.to_raster('ndvi_co.tiff')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0244_pystac_ndvi_cv', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
