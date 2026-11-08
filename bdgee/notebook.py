"""Helpers for adapted tutorial notebooks; exports are planned, never auto-submitted."""
from pathlib import Path
import json
import numbers
import ee
from .core import Product, plan_product, safe_name


def export_outputs(namespace, theme, source, scale=1000):
    """Export named EE rasters/tables, local arrays, scalar values, and figures.

    Returns tasks for explicit review/start. Collections stay lazy and their
    per-date regional values are exported as CSV; a mean map is also planned.
    Intermediate globals are included intentionally so results are not omitted.
    Set scale per analysis: the 1000m tutorial default is NOT native resolution.
    """
    root=Path('outputs')/theme/source
    root.mkdir(parents=True,exist_ok=True)
    tasks=[]; errors={}; scalars={}; seen=set()
    from .core import boundaries
    country, _=boundaries()
    for name, value in list(namespace.items()):
        if name.startswith('_') or id(value) in seen:continue
        seen.add(id(value))
        try:
            if isinstance(value,ee.Image):
                tasks.extend(plan_product(Product(name,value,scale,'see source method'),theme,source))
            elif isinstance(value,ee.ImageCollection):
                tasks.extend(plan_product(Product(name+'_mean',value.mean(),scale,'see source method'),theme,source))
                def row(image):
                    return ee.Feature(None,image.reduceRegion(ee.Reducer.mean(),country.geometry(),scale,tileScale=4,maxPixels=1e13)).set('time_start',image.get('system:time_start'))
                table=ee.FeatureCollection(value.toList(value.size()).map(lambda i:row(ee.Image(i))))
                tasks.append(ee.batch.Export.table.toDrive(collection=table,description=safe_name(source+'_'+name+'_series'),folder='BD_GEE_'+theme,fileFormat='CSV'))
            elif isinstance(value,ee.FeatureCollection):
                tasks.append(ee.batch.Export.table.toDrive(collection=value,description=safe_name(source+'_'+name),folder='BD_GEE_'+theme,fileFormat='GeoJSON'))
            elif isinstance(value,(ee.Number,ee.String,ee.Dictionary)):
                props=value if isinstance(value,ee.Dictionary) else {'value':value}
                tasks.append(ee.batch.Export.table.toDrive(collection=ee.FeatureCollection([ee.Feature(None,props)]),description=safe_name(source+'_'+name),folder='BD_GEE_'+theme,fileFormat='CSV'))
            elif isinstance(value,numbers.Number):scalars[name]=float(value)
            elif hasattr(value,'to_netcdf'):
                # The tutorial analysis must have already clipped/masked its arrays.
                value.to_netcdf(root/(safe_name(name)+'.nc'))
                dims=[d for d in value.dims if d.lower() in ('x','y','lon','lat','longitude','latitude')]
                summary=value.mean(dim=dims,skipna=True) if dims else value
                summary.to_dataframe().to_csv(root/(safe_name(name)+'_summary.csv'))
            elif hasattr(value,'to_csv'):value.to_csv(root/(safe_name(name)+'.csv'))
        except Exception as exc:errors[name]=str(exc)
    (root/'scalars.json').write_text(json.dumps(scalars,indent=2,allow_nan=True))
    (root/'export_errors.json').write_text(json.dumps(errors,indent=2))
    try:
        import matplotlib.pyplot as plt
        for n in plt.get_fignums():plt.figure(n).savefig(root/f'figure_{n}.png',dpi=200,bbox_inches='tight')
    except ImportError:pass
    print(f'{len(tasks)} EE tasks planned, {len(errors)} failures. Local outputs: {root}. Inspect export_errors.json.')
    return tasks


def upload_local(folder, theme):
    """Explicit upload of local plots, tables and NetCDF to the same themed Drive folder.

    Uses the user's Earth Engine OAuth credentials WITH Drive scope. Do not use
    service accounts unless their Drive permissions/storage have been configured.
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    credentials=ee.data.get_persistent_credentials()
    drive=build('drive','v3',credentials=credentials)
    title='BD_GEE_'+theme
    result=drive.files().list(q=f"name = '{title}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",fields='files(id,name)').execute()['files']
    if len(result)>1:raise RuntimeError('Duplicate themed Drive folders; resolve ambiguity in Drive before uploading')
    parent=result[0]['id'] if result else drive.files().create(body={'name':title,'mimeType':'application/vnd.google-apps.folder'},fields='id').execute()['id']
    for file in sorted(Path(folder).rglob('*')):
        if file.is_file():
            name=safe_name(str(file.relative_to(folder).with_suffix('')))+file.suffix
            drive.files().create(body={'name':name,'parents':[parent]},media_body=MediaFileUpload(str(file),resumable=True),fields='id').execute()
