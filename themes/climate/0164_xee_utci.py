# Bangladesh adaptation: 0164_xee_utci
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
_OUTPUT_DIR = Path(os.environ.get('BDGEE_OUTPUT_DIR', _REPO_ROOT / 'outputs' / 'climate' / '0164_xee_utci'))
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(_OUTPUT_DIR)
"""GEE_0088_utci.ipynb

Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee
Tutorial Video: Google Earth Engine Tutorial-169: Universal Thermal Climate Index using FLDAS 

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
fldas = ee.ImageCollection('NASA/FLDAS/NOAH01/C/GL/M/V001').filterDate('2020', '2021').select(['Tair_f_tavg', 'Wind_f_tavg', 'Qair_f_tavg', 'RadT_tavg'], ['tas', 'sfcWind', 'hurs', 'mrt']).map(lambda img: img.select('sfcWind', 'hurs').addBands(img.select('tas', 'mrt').subtract(273.15)))
fldas
import xarray as xr
ds = xr.open_dataset(fldas, engine='ee', crs='EPSG:4326', scale=0.11, geometry=BD_ROI)
ds = ds.sortby('time') * 1
ds.tas.plot(x='lon', y='lat', col='time', col_wrap=6, robust=True)
from xclim.indicators.convert import universal_thermal_climate_index
tas = ds.tas
tas.attrs['units'] = 'degC'
hurs = ds.hurs
hurs.attrs['units'] = ''
sfcWind = ds.sfcWind
sfcWind.attrs['units'] = 'm s-1'
mrt = ds.mrt
mrt.attrs['units'] = 'degC'
utci = universal_thermal_climate_index(tas=tas, hurs=hurs, sfcWind=sfcWind, mrt=mrt)
utci_cel = utci - 273.15
utci_cel.plot(x='lon', y='lat', robust=True, col='time', col_wrap=6)

# Review these task plans; task creation does not start exports.
os.chdir(_REPO_ROOT)
bd_tasks = export_outputs(globals(), 'climate', '0164_xee_utci', scale=1000)
# Set an appropriate native scale above before creating plans.
# for task in bd_tasks: task.start()
# upload_local(_OUTPUT_DIR, 'climate')  # explicit upload; requires Drive OAuth scope
