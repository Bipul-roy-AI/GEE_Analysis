// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'soil_drought';
var BD_SOURCE = '00055_soilmoisture_downscaling';
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
      scale:BD_SCALE, crs:'EPSG:4326', fileFormat:'GeoTIFF',
      formatOptions:{cloudOptimized:true}});
    var stats = image.reduceRegions({collection:BD_DISTRICTS.merge(BD_COUNTRY),
      reducer:ee.Reducer.mean().combine({reducer2:ee.Reducer.minMax(), sharedInputs:true})
        .combine({reducer2:ee.Reducer.count(), sharedInputs:true}),
      scale:BD_SCALE, crs:'EPSG:4326', tileScale:4})
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
  [45.69105798238498,28.274725424381415],
  [52.45863610738498,28.274725424381415],
  [52.45863610738498,34.24300069681132], 
  [45.69105798238498,34.24300069681132],
  [45.69105798238498,28.274725424381415]
  ]

var geometry = BD_ROI


Map.centerObject(geometry)

var time_start = ee.Date('2023'), time_end = ee.Date('2024')

var sm = ee.ImageCollection("NASA/SMAP/SPL3SMP_E/006")
.select('soil_moisture_am')
.filterDate(time_start, time_end)

var list_10days = ee.List.sequence(0, time_end.difference(time_start, 'day'), 10)
    .map(function(i){
      return ee.Date.fromYMD(2023, 1, 1).advance(i, 'days')
      })

var sm_10days = ee.ImageCollection(list_10days.map(function(start_date){
  start_date = ee.Date(start_date)
  var end_date = start_date.advance(10, 'days')
  var img = sm.filterDate(start_date, end_date).median()
  var resample = img.resample().reproject({crs: img.projection().crs(), scale: 1000})
  return resample.multiply(100).toInt()
  .set('system:time_start', start_date.millis())
  .set('system:time_end', end_date.millis())
  .set('system:index', start_date.format('YYYY-MM-dd'))
  }));
  
Map.addLayer(sm_10days.toBands().clip(geometry), [], 'sm_9km', false)

var temp = ee.ImageCollection("MODIS/061/MOD11A1")
.select('LST_.*')
.filterDate(time_start, time_end)


var temp_10days = ee.ImageCollection(list_10days.map(function(start_date){
  start_date = ee.Date(start_date)
  var end_date = start_date.advance(10, 'days')
  var img = temp.filterDate(start_date, end_date).mean()
  var lst_day = img.select('LST_Day_1km').multiply(0.02)
  var lst_night = img.select('LST_Night_1km').multiply(0.02)
  var lst_delta = lst_day.subtract(lst_night).rename('LST_delta')
  return lst_day.addBands(lst_delta)
  .set('system:time_start', start_date.millis())
  .set('system:time_end', end_date.millis())
  .set('system:index', start_date.format('YYYY-MM-dd'))
  }));


var sr = ee.ImageCollection("MODIS/061/MOD09GA")
.select('sur.*').combine(temp.select('LST_Day.*'))
.filterDate(time_start, time_end)
.map(function(img){
  var masked_bands = img.select('sur.*').updateMask(img.select('LST.*')).multiply(0.0001)
  var ndvi = masked_bands.normalizedDifference(['sur_refl_b02','sur_refl_b01']).rename('ndvi')
  return masked_bands.select('sur_refl_b0[5-7]').addBands(ndvi)
  .copyProperties(img, img.propertyNames())
  })
  
var sr_10days = ee.ImageCollection(list_10days.map(function(start_date){
  start_date = ee.Date(start_date)
  var end_date = start_date.advance(10, 'days')
  var ndvi = sr.select('ndvi').filterDate(start_date, end_date).max()
  var ms = sr.select('sur.*').filterDate(start_date, end_date).median()
  return ms.addBands(ndvi)
  .set('system:time_start', start_date.millis())
  .set('system:time_end', end_date.millis())
  .set('system:index', start_date.format('YYYY-MM-dd'))
  }));
  

Map.addLayer(sr.toBands().clip(geometry),[],'sr',false)

var landcover = ee.ImageCollection("MODIS/061/MCD12Q1").mode().select('LC_Type1')

var collection = sr_10days.combine(temp_10days).combine(sm_10days)
    .map(function(img){
      return img.addBands(landcover)
      .copyProperties(img, img.propertyNames())
      })

var sm_1km = collection.map(function(img){
  
  var training_data = img.stratifiedSample({
    numPoints: 10, classBand: 'soil_moisture_am', region: geometry, scale: 1000
    });
    
  var model = ee.Classifier.smileGradientTreeBoost(80).train({
    features: training_data, classProperty: 'soil_moisture_am', inputProperties: img.bandNames()
    }).setOutputMode('REGRESSION');
    
  var band_name = img.bandNames().remove('soil_moisture_am')  
    
  var result = img.select(band_name).classify(model).rename('SM_1km').divide(100.0).toFloat()
  
  return result.addBands(img.select(['soil_moisture_am'],['SM_9km']))
  .copyProperties(img, ['system:time_start', 'system:time_end'])
  
  })

var sm_1km_mean = sm_1km.select('SM_1km').mean()

var sm_cor =  sm_1km.map(function(img){
  var sm1km = img.select('SM_1km')
  var sm9km = img.select('SM_9km').divide(100.0).toFloat()
  var cor = sm1km.add(sm9km.subtract(sm_1km_mean)).rename('SM_1km_cor')
  return cor
  .copyProperties(img, img.propertyNames())
  })


print(sm_cor)


Map.addLayer(sm_cor.toBands().clip(geometry), [], 'sm_1km', false)


Export.image.toDrive({
  image: sm_cor.toBands().clip(geometry), 
  description: 'sm_1km_cor', 
  folder: 'test', 
  region: geometry, 
  scale: 1000, 
  crs: 'EPSG:4326'
  })


