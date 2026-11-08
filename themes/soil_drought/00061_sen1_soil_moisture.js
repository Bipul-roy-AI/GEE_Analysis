// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'soil_drought';
var BD_SOURCE = '00061_sen1_soil_moisture';
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
  [48.10178521249212,30.724369816411947],
  [49.06308892342962,30.724369816411947],
  [49.06308892342962,31.444134120146206],
  [48.10178521249212,31.444134120146206],
  [48.10178521249212,30.724369816411947]
  ]


var geometry = BD_ROI

Map.centerObject(geometry);

var time_start = ee.Date('2017')
var time_end = ee.Date('2024')
var time_dif = time_end.difference(time_start, 'day')

var sen1 = ee.ImageCollection("COPERNICUS/S1_GRD")
.filterDate(time_start, time_end)
.filterBounds(geometry)
.filter(ee.Filter.listContains('transmitterReceiverPolarisation','VV'))
.filter(ee.Filter.eq('instrumentMode','IW')).select('VV')


print(sen1.aggregate_array('orbitProperties_pass').distinct())


var asc = sen1
.filter(ee.Filter.eq('orbitProperties_pass','ASCENDING'))

var des = sen1
.filter(ee.Filter.eq('orbitProperties_pass','DESCENDING'))


var list_dates = ee.List.sequence(0, time_dif, 10).map(function(interval){
  return ee.Date.fromYMD(2017, 1, 1).advance(interval, 'days')
  })


var asc_10days = ee.ImageCollection(list_dates.map(function(dates){
  var start_date  = ee.Date(dates)
  var end_date = start_date.advance(10, 'days')
  var composite = asc.filterDate(start_date, end_date).mean()
  var bands = composite.bandNames().size()
  return composite
  .set('system:time_start', start_date.millis())
  .set('system:time_end', end_date.millis())
  .set('band_number', bands)
  })).filter(ee.Filter.eq('band_number',1));
  
var des_10days = ee.ImageCollection(list_dates.map(function(dates){
  var start_date  = ee.Date(dates)
  var end_date = start_date.advance(10, 'days')
  var composite = des.filterDate(start_date, end_date).mean()
  var bands = composite.bandNames().size()
  return composite
  .set('system:time_start', start_date.millis())
  .set('system:time_end', end_date.millis())
  .set('band_number', bands)
  })).filter(ee.Filter.eq('band_number',1));
  

var asc_sigma = asc_10days.map(function(img){
  var sigma = ee.Image(10).pow(img.divide(10)).rename('sigma')
  var speckel = sigma.focalMean(30, 'square', 'meters');
  return speckel
  .copyProperties(img, img.propertyNames())
  });
  
var des_sigma = des_10days.map(function(img){
  var sigma = ee.Image(10).pow(img.divide(10)).rename('sigma')
  var speckel = sigma.focalMean(30, 'square', 'meters');
  return speckel
  .copyProperties(img, img.propertyNames())
  });
  
  
var water_mask = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").select('label')
.filterDate(time_start, time_end)
.filterBounds(geometry).mode().eq(0).not()

var urban_mask = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").select('label')
.filterDate(time_start, time_end)
.filterBounds(geometry).mode().eq(6).not()


var asc_min = asc_sigma.min()
var asc_max = asc_sigma.max()

var asc_sm = asc_sigma.map(function(img){
  var index = (img.subtract(asc_min)).divide(asc_max.subtract(asc_min))
  var date = img.date().format('YYYY-MM-dd')
  return index.multiply(water_mask).multiply(urban_mask).rename('sm_asc')
  .copyProperties(img,['system:time_start'])
  .set('date', ee.String(date))
  })
  
Map.addLayer(asc_sm.filterDate('2020','2021').toBands().clip(geometry),[],'sm_asc',false)

var cor2 = [
  [48.54810479257024,30.974198964042525],
  [48.56321099374212,30.974198964042525],
  [48.56321099374212,30.984795502612585],
  [48.54810479257024,30.984795502612585],
  [48.54810479257024,30.974198964042525]
  ]

var geometry2 = BD_ROI

print(
  ui.Chart.image.series(asc_sm, geometry2, ee.Reducer.mean(), 30, 'system:time_start')
  )



var des_min = des_sigma.min()
var des_max = des_sigma.max()

var des_sm = des_sigma.map(function(img){
  var index = (img.subtract(des_min)).divide(des_max.subtract(des_min))
  var date = img.date().format('YYYY-MM-dd')
  return index.multiply(water_mask).multiply(urban_mask).rename('sm_asc')
  .copyProperties(img,['system:time_start'])
  .set('date', ee.String(date))
  })
  
Map.addLayer(des_sm.filterDate('2020','2021').toBands().clip(geometry),[],'sm_des',false)


print(
  ui.Chart.image.series(des_sm, geometry2, ee.Reducer.mean(), 30, 'system:time_start')
  )


Export.image.toDrive({
  image: des_sm.filterDate('2020','2021').toBands().clip(geometry),
  description: 'des_sm', 
  scale: 30, 
  region: geometry, 
  crs: 'EPSG:4326', 
  folder: 'test', 
  maxPixels: 1e13
  })
