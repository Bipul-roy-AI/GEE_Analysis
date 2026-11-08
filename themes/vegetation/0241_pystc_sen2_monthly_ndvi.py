# Bangladesh adaptation: 0241_pystc_sen2_monthly_ndvi
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'vegetation' / '0241_pystc_sen2_monthly_ndvi'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""0008_pystac_sen2_ndvi.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: PySTAC Tutorial-1: Sentinel-2 Monthly NDVI Analysis in Python
This code is part of a tutorial series on python eo programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor


"""
from pystac_client import Client
catalog = Client.open('https://earth-search.aws.element84.com/v1')
for collections in catalog.get_collections():
    print(collections.id)
bbox = BD_BBOX
search = catalog.search(collections=['sentinel-2-c1-l2a'], bbox=bbox, datetime='2023/2025', query={'eo:cloud_cover': {'lt': '10'}})
items = search.item_collection()
len(items)
items[0]
items[0].assets.keys()
import stackstac
ds = stackstac.stack(items, assets=['red', 'rededge1', 'nir'], bounds_latlon=bbox, epsg=3857, resolution=20)
ds_clean = ds.to_dataset('band').reset_coords(drop=True).drop_attrs()
import rioxarray
ds_clean = ds_clean.rio.write_crs('EPSG:3857').rio.clip([BD_ROI.getInfo()], crs='EPSG:4326')
ds_clean
nir = ds_clean['nir']
red = ds_clean['red']
rededge = ds_clean['rededge1']
ndvi = ((nir - red) / (nir + red)).rename('ndvi')
ndre = ((nir - rededge) / (nir + rededge)).rename('ndre')
import xarray as xr
ds_merge = xr.merge([ndvi, ndre])
ds_monthly = ds_merge.resample(time='M').max('time')
from dask.diagnostics import ProgressBar
import warnings
import logging
warnings.filterwarnings('ignore', category=RuntimeWarning)
logging.getLogger('rasterio._env').setLevel(logging.ERROR)
with ProgressBar():
    ds_monthly = ds_monthly.compute()
ds_month = ds_monthly.groupby('time.month').mean('time')
ds_month
ds_month.ndvi.plot(robust=True, col='month', col_wrap=6)
ds_month.ndre.plot(robust=True, col='month', col_wrap=6)
df = ds_monthly.sel(x=48.827533, y=31.959757, method='nearest').to_dataframe().drop(['x', 'y'], axis=1)
ds_monthly.mean(dim=['x', 'y']).to_dataframe().plot()
import rioxarray
ndvi_out = ds_monthly['ndvi'].sel(time='2024').copy()
ndvi_out = ndvi_out.rio.write_crs('EPSG:3857')
ndvi_out = ndvi_out.rio.set_spatial_dims(x_dim='x', y_dim='y')
ndvi_out = ndvi_out.rio.write_coordinate_system(inplace=True)
ndvi_out.rio.to_raster('ndvi.tiff')

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'vegetation', '0241_pystc_sen2_monthly_ndvi', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'vegetation')  # explicit upload; requires Drive OAuth scope
