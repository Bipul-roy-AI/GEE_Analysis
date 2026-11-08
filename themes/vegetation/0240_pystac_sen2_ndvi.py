# Bangladesh adaptation: 0240_pystac_sen2_ndvi
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
_OUTPUT_DIR = _REPO_ROOT / 'outputs' / 'vegetation' / '0240_pystac_sen2_ndvi'
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""Untitled0.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: PySTAC Tutorial-1: Sentinel-2 NDVI
This code is part of a tutorial series on python eo programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
from pystac_client import Client
catalog = Client.open('https://earth-search.aws.element84.com/v1')
for collection in catalog.get_collections():
    print(collection.id)
bbox = BD_BBOX
search = catalog.search(collections=['sentinel-2-l2a'], bbox=bbox, datetime='2025', query={'eo:cloud_cover': {'lt': '20'}})
items = search.item_collection()
len(items)
items[0].assets.keys()
import stackstac
ds = stackstac.stack(items, assets=['red', 'rededge1', 'nir'], bounds_latlon=bbox, epsg=3857, resolution=10)
ds_clean = ds.to_dataset('band').reset_coords(drop=True).drop_attrs()
import rioxarray
ds_clean = ds_clean.rio.write_crs('EPSG:3857').rio.clip([BD_ROI.getInfo()], crs='EPSG:4326')
ds_clean
red = ds_clean['red'].clip(min=0)
red_edge = ds_clean['rededge1'].clip(min=0)
nir = ds_clean['nir'].clip(min=0)
ndvi = (nir - red) / (nir + red)
ndre = (nir - red_edge) / (nir + red_edge)
ndvi
ndvi_mean = ndvi.mean(dim='time')
ndre_mean = ndre.mean(dim='time')
from dask.diagnostics import ProgressBar
import warnings
import logging
warnings.filterwarnings('ignore', category=RuntimeWarning)
logging.getLogger('rasterio._env').setLevel(logging.ERROR)
with ProgressBar():
    ndvi_mean = ndvi_mean.compute()
ndvi_mean.plot(robust=True)
with ProgressBar():
    ndre_mean = ndre_mean.compute()
ndre_mean.plot(robust=True)
import rioxarray
out = ndre_mean.copy()
out = out.rio.write_crs('EPSG:3857')
out = out.rio.set_spatial_dims(x_dim='x', y_dim='y')
out = out.rio.write_coordinate_system(inplace=True)
out
out.rio.to_raster('ndre_mean.tiff')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0240_pystac_sen2_ndvi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
