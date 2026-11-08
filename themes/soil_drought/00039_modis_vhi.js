// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'soil_drought';
var BD_SOURCE = '00039_modis_vhi';
var BD_FOLDER = 'BD_GEE_' + BD_THEME;
var BD_SCALE = 1000; // EDIT to native analysis resolution; 1000 is a review default.
var BD_CREATE_EXPORTS = false; // Set true AFTER reviewing science, units and task volume.
var BD_COUNTRY = ee.FeatureCollection('FAO/GAUL/2015/level0')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var BD_DISTRICTS = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var BD_ROI = BD_COUNTRY.geometry();
// Aliases also replace missing drawn/imported study-area variables, not training labels.
var roi = BD_ROI, geometry = BD_ROI, table = BD_COUNTRY;
var coordinates = BD_ROI.coordinates();
var BD_serial = 0;
function BD_name(text) {
  BD_serial += 1;
  return (BD_SOURCE + '_' + BD_serial + '_' + text).replace(/[^A-Za-z0-9_-]/g, '_').slice(0, 95);
}
var BD_imageExport = Export.image.toDrive;
var BD_tableExport = Export.table.toDrive;
// Route existing exports to the national boundary and theme folder.
Export.image.toDrive = function(options) {
  if (!BD_CREATE_EXPORTS) { print('Export disabled; review BD_CREATE_EXPORTS', options.description); return; }
  options.folder = BD_FOLDER;
  options.description = BD_name(options.description || 'raster');
  options.fileNamePrefix = options.description;
  options.region = BD_ROI;
  options.image = ee.Image(options.image).clip(BD_ROI).toFloat();
  options.maxPixels = 1e13;
  return BD_imageExport(options);
};
Export.table.toDrive = function(options) {
  if (!BD_CREATE_EXPORTS) { print('Export disabled; review BD_CREATE_EXPORTS', options.description); return; }
  options.folder = BD_FOLDER;
  options.description = BD_name(options.description || 'table');
  options.fileNamePrefix = options.description;
  return BD_tableExport(options);
};
// Every displayed EE raster gets a raw GeoTIFF and regional descriptive table.
// For categorical products use the national toolkit's class-area workflow instead
// of interpreting this generic descriptive table as a class statistic.
var BD_addLayer = Map.addLayer;
Map.addLayer = function(object, vis, name, shown, opacity) {
  var result = BD_addLayer(object, vis, name, shown, opacity);
  if (BD_CREATE_EXPORTS && object instanceof ee.Image) {
    var image = ee.Image(object).clip(BD_ROI);
    Export.image.toDrive({image:image, description:name || 'map', region:BD_ROI,
      scale:BD_SCALE, crs:'EPSG:6933', fileFormat:'GeoTIFF',
      formatOptions:{cloudOptimized:true}});
    var stats = image.reduceRegions({collection:BD_DISTRICTS.merge(BD_COUNTRY),
      reducer:ee.Reducer.mean().combine({reducer2:ee.Reducer.minMax(), sharedInputs:true})
        .combine({reducer2:ee.Reducer.count(), sharedInputs:true}),
      scale:BD_SCALE, crs:'EPSG:6933', tileScale:4})
      .map(function(f){return f.setGeometry(null).set('source',BD_SOURCE);});
    Export.table.toDrive({collection:stats, description:(name || 'map')+'_descriptive_stats', fileFormat:'CSV'});
  }
  return result;
};
// Export the values underlying image-series charts, not a screenshot of a chart.
var BD_series = ui.Chart.image.series;
ui.Chart.image.series = function(collection, region, reducer, scale, xProperty) {
  var originalArgs=Array.prototype.slice.call(arguments);
  if (collection && collection.imageCollection) {
    var opts=collection; collection=opts.imageCollection; region=opts.region;
    reducer=opts.reducer;scale=opts.scale;xProperty=opts.xProperty;
  }
  if (BD_CREATE_EXPORTS) {
    var rows = ee.ImageCollection(collection).toList(ee.ImageCollection(collection).size()).map(function(item) {
      var image = ee.Image(item);
      var values = image.reduceRegion({reducer:reducer || ee.Reducer.mean(),
        geometry:BD_ROI, scale:scale || BD_SCALE, maxPixels:1e13,tileScale:4});
      return ee.Feature(null,values).set('time_start',image.get(xProperty || 'system:time_start'));
    });
    Export.table.toDrive({collection:ee.FeatureCollection(rows),description:'chart_values',fileFormat:'CSV'});
  }
  return BD_series.apply(null,originalArgs);
};
Map.centerObject(BD_ROI,7);
// Preserve printed scalar/dictionary results as CSV as well as Console output.
var BD_print = print;
print = function() {
  for (var j = 0; j < arguments.length; j++) {
    var value = arguments[j];
    if (BD_CREATE_EXPORTS && (value instanceof ee.Number || value instanceof ee.Dictionary)) {
      var props = value instanceof ee.Dictionary ? value : ee.Dictionary({value:value});
      BD_tableExport({collection:ee.FeatureCollection([ee.Feature(null,props)]),
        description:BD_name('console_value'), folder:BD_FOLDER, fileFormat:'CSV'});
    }
  }
  return BD_print.apply(null,arguments);
};
var BD_histogram = ui.Chart.image.histogram;
ui.Chart.image.histogram = function(image, region, scale, maxBuckets, minBucketWidth, maxRaw) {
  var originalArgs=Array.prototype.slice.call(arguments);
  if (image && image.image) {
    var opts=image;image=opts.image;region=opts.region;scale=opts.scale;maxBuckets=opts.maxBuckets;
  }
  if (BD_CREATE_EXPORTS) {
    var histogram = ee.Image(image).reduceRegion({reducer:ee.Reducer.autoHistogram(maxBuckets || 128),
      geometry:BD_ROI,scale:scale || BD_SCALE,maxPixels:1e13,tileScale:4});
    Export.table.toDrive({collection:ee.FeatureCollection([ee.Feature(null,histogram)]),
      description:'histogram_bucket_values_counts',fileFormat:'CSV'});
  }
  return BD_histogram.apply(null,originalArgs);
};
var BD_seriesByRegion = ui.Chart.image.seriesByRegion;
ui.Chart.image.seriesByRegion = function(collection, regions, reducer, band, scale, xProperty, seriesProperty) {
  var originalArgs=Array.prototype.slice.call(arguments);
  if (collection && collection.imageCollection) {
    var opts=collection;collection=opts.imageCollection;regions=opts.regions;
    reducer=opts.reducer;band=opts.band;scale=opts.scale;xProperty=opts.xProperty;seriesProperty=opts.seriesProperty;
  }
  if (BD_CREATE_EXPORTS) {
    var rows = ee.ImageCollection(collection).toList(ee.ImageCollection(collection).size()).map(function(item) {
      var image=ee.Image(item);
      if (band) image=image.select(band);
      return image.reduceRegions({collection:BD_DISTRICTS,reducer:reducer || ee.Reducer.mean(),
        scale:scale || BD_SCALE,tileScale:4}).map(function(f){
          return f.setGeometry(null).set('time_start',image.get(xProperty || 'system:time_start'));
        });
    });
    Export.table.toDrive({collection:ee.FeatureCollection(rows).flatten(),description:'series_by_district',fileFormat:'CSV'});
  }
  return BD_seriesByRegion.apply(null,originalArgs);
};


/*
Tutorial Code by Amirhossein Ahrari
YouTube: https://www.youtube.com/@amirhosseinahrarigee

This code is part of a tutorial series on Earth Engine programming techniques
presented on the Amirhossein Ahrari YouTube channel. You are free to use and modify
this code for academic and non-academic purposes. Don't forget to subscribe to
the Amirhossein Ahrari channel and follow the videos to support the instructor!
*/

var cor = [
  [45.65354975558493,36.50321863483044],
  [46.59837397433493,36.50321863483044],
  [46.59837397433493,37.27644180666329],
  [45.65354975558493,37.27644180666329],
  [45.65354975558493,36.50321863483044]
  ]

var roi = BD_ROI

Map.centerObject(roi);

var time_start = '2001', time_end = '2024'

var ndvi= ee.ImageCollection("MODIS/061/MOD13A2")
.select('NDVI')
.filterDate(time_start, time_end);


var temp= ee.ImageCollection("MODIS/061/MOD11A2")
.select('LST_Day_1km')
.filterDate(time_start, time_end);

// vci: vegetation condition index
// ndvi, ndvi_min, ndvi_max
// vci = (ndvi - ndvi_min)/(ndvi_max - ndvi_min)

var ndvi_min = ndvi.min().multiply(0.0001)
var ndvi_max = ndvi.max().multiply(0.0001)

// temporal function to convert data into monthly format

function temporal_collection(collection, start, count, interval, unit){
  var seq = ee.List.sequence(0, ee.Number(count).subtract(1));
  var origin_date = ee.Date(start);
  return ee.ImageCollection(seq.map(function(i){
    var start_date = origin_date.advance(ee.Number(interval).multiply(i), unit);
    var end_date = origin_date.advance(ee.Number(interval).multiply(ee.Number(i).add(1)), unit);
    return collection.filterDate(start_date, end_date).mean()
    .set('system:time_start', start_date.millis())
    .set('system:time_end', end_date.millis())
    }))
  }
  
// monthly ndvi image collection

var ndvi_monthly = temporal_collection(ndvi, time_start, 276, 1, 'month');

// vci

var vci = ndvi_monthly.map(function(img){
  var index = img.expression('(ndvi - min) / (max - min)',
  {'ndvi': img.select('NDVI').multiply(0.0001), 'min': ndvi_min, 'max': ndvi_max})
  return index.rename('VCI')
  .copyProperties(img, img.propertyNames())
  });
  

// tci: thermal condition index
// lst_max, lst_min
// tci = (max - lst) / (max  - min)

var temp_max = temp.max().multiply(0.02);
var temp_min = temp.min().multiply(0.02);

var temp_monthly = temporal_collection(temp, time_start, 276, 1, 'month');

var tci = temp_monthly.map(function(img){
  var index = img.expression('(max - lst)/(max - min)',
  {'max': temp_max, 'min': temp_min, 'lst': img.multiply(0.02)})
  return index.rename('TCI')
  .copyProperties(img,img.propertyNames())
  }) ;
  

var modis_indices = vci.combine(tci);


// vhi: vegetation health index
// vci = 0.5 * vci + (1 - 0.5) * tci


var drought = modis_indices.map(function(img){
  var vhi = img.expression('0.5 * vci + (1 - 0.5) * tci',{
    'vci': img.select('VCI'), 'tci': img.select('TCI')
    }).rename('VHI')
  return img.addBands(vhi)
  .copyProperties(img, img.propertyNames())
  });
  

print(
  ui.Chart.image.series(drought, roi, ee.Reducer.mean(),
  1000, 'system:time_start')
  )
  
print(
  ui.Chart.image.series(drought.select('VCI','TCI'), roi, ee.Reducer.mean(),
  1000, 'system:time_start')
  )

print(
  ui.Chart.image.series(drought.select('VHI'), roi, ee.Reducer.mean(),
  1000, 'system:time_start')
  )

Map.addLayer(drought.select('VHI').filterDate('2005','2006').toBands().clip(roi),[],'VHI', false)

Export.image.toDrive({
  image: drought.filterDate('2005','2006').select('VHI').toBands(), 
  description: 'modis_drought_vhi',
  scale: 1000, 
  crs: 'EPSG:4326', 
  maxPixels: 1e13, 
  region: roi
  })

Export.image.toDrive({
  image: drought.filterDate('2005','2006').select('TCI').toBands(), 
  description: 'modis_drought_tci',
  scale: 1000, 
  crs: 'EPSG:4326', 
  maxPixels: 1e13, 
  region: roi
  })
  
Export.image.toDrive({
  image: drought.filterDate('2005','2006').select('VCI').toBands(), 
  description: 'modis_drought_vci',
  scale: 1000, 
  crs: 'EPSG:4326', 
  maxPixels: 1e13, 
  region: roi
  })
