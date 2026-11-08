# Bangladesh adaptation: 0242_pystac_ndvi_map
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'vegetation' / '0242_pystac_ndvi_map'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""0011_ndvi_landcovers.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: PySTAC Tutorial-3: Sentinel-2 Monthly NDVI Analysis using Python
This code is part of a tutorial series on python eo programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
from pystac_client import Client
catalog = Client.open('https://earth-search.aws.element84.com/v1')
for collections in catalog.get_collections():
    print(collections.id)
roi = [45.400845, 36.99289, 45.517881, 37.073503]
search = catalog.search(collections=['sentinel-2-c1-l2a'], bbox=roi, datetime='2023/2025', query={'eo:cloud_cover': {'lt': '10'}})
items = search.item_collection()
len(items)
items[0]
import stackstac
items[0].assets.keys()
ds = stackstac.stack(items, bounds_latlon=roi, assets=['red', 'nir'], epsg=3857, resolution=30)
ds_clean = ds.to_dataset('band').reset_coords(drop=True).drop_attrs()
import rioxarray
ds_clean = ds_clean.rio.write_crs('EPSG:3857').rio.clip([BD_ROI.getInfo()], crs='EPSG:4326')
red = ds_clean['red']
nir = ds_clean['nir']
ndvi = (nir - red) / (nir + red)
ndvi_monthly = ndvi.resample(time='M').max('time')
from dask.diagnostics import ProgressBar
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
import logging
logging.getLogger('rasterio._env').setLevel(logging.ERROR)
with ProgressBar():
    ndvi_monthly = ndvi_monthly.compute()
ndvi_month = ndvi_monthly.groupby('time.month').mean('time')
ndvi_month.plot(robust=True, cmap='RdYlGn', col='month', col_wrap=6)
import xarray as xr
ndvi_classes = xr.where(ndvi_monthly < 0, 1, xr.where(ndvi_monthly < 0.2, 2, xr.where(ndvi_monthly < 0.4, 3, xr.where(ndvi_monthly < 0.6, 4, 5))))
ndvi_classes.sel(time='2023').plot(robust=True, cmap='turbo', col='time', col_wrap=6)
from scipy import stats
ndvi_classes.shape[0]
ndvi_mode = stats.mode(ndvi_classes.values, axis=0, nan_policy='omit').mode
ndvi_mode = xr.DataArray(ndvi_mode, coords={'y': ndvi_classes.y, 'x': ndvi_classes.x}, dims=['y', 'x'])
ndvi_mode.plot(robust=True, cmap='turbo')
import numpy as np
cls_num = np.unique(ndvi_mode.values)
for i in cls_num:
    pixels = ndvi_mode.isin(i).sum(dim=['y', 'x']).item()
    area = pixels * (30 * 30) / 1000000.0
    print(f'class {i} pixels: {pixels}')
    print(f'class {i} area: {area} km2')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0242_pystac_ndvi_map', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
