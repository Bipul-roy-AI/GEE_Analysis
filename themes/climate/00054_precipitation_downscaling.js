// Bangladesh tutorial adaptation. Select cloud project axial-paratext-491911-b6
// in the Earth Engine Code Editor. This example has NOT been remotely validated.
// Original author: Amirhossein Ahrari. Original attribution retained below.
// Adaptation sets national land boundary; original dates/method assumptions remain.
var BD_THEME = 'climate';
var BD_SOURCE = '00054_precipitation_downscaling';
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




var cor1 = [
  [42.49966365960427,23.30989641960812],
  [64.47231990960427,23.30989641960812],
  [64.47231990960427,42.47851790347444],
  [42.49966365960427,42.47851790347444],
  [42.49966365960427,23.30989641960812]
  ]

var geometry  = BD_ROI



var time_start = '2023', time_end = '2024'

var pr = ee.ImageCollection("NOAA/PERSIANN-CDR")
.filterDate(time_start, time_end);

var month_list = ee.List.sequence(1,12)

var pr_monthly = ee.ImageCollection(month_list.map(function(month){
  var month_img = pr.filter(ee.Filter.calendarRange(month, month, 'month')).sum()
  var date = ee.Date.fromYMD(2023, month, 1)
  var resample = month_img.resample().reproject({crs: month_img.projection().crs(), scale: 500})
  return resample.toInt()
  .set('system:time_start', date.millis())
  .set('system:index', date.format('YYYY-MM-dd'))
  }))

// independent variabls

var lc = ee.ImageCollection("MODIS/061/MCD12Q1")
.mode().select('LC_Type1')

var dem = ee.Image("USGS/GTOPO30")

var ndvi = ee.ImageCollection("MODIS/061/MOD13A1")
.select('NDVI')
.filterDate(time_start, time_end)

var ndvi_monthly = ee.ImageCollection(month_list.map(function(month){
  var month_img = ndvi.filter(ee.Filter.calendarRange(month, month, 'month')).median()
  var date = ee.Date.fromYMD(2023, month, 1);
  return month_img.multiply(0.0001)
  .set('system:time_start', date.millis())
  .set('system:index', date.format('YYYY-MM-dd'))
  }))
  
var temp = ee.ImageCollection("MODIS/061/MOD11A2")
.select('LST_Day_1km')
.filterDate(time_start, time_end)


var temp_monthly = ee.ImageCollection(month_list.map(function(month){
  var month_img = temp.filter(ee.Filter.calendarRange(month, month, 'month')).median()
  var date = ee.Date.fromYMD(2023, month, 1);
  return month_img.multiply(0.02)
  .set('system:time_start', date.millis())
  .set('system:index', date.format('YYYY-MM-dd'))
  }))
  

var collection = ndvi_monthly.combine(temp_monthly).combine(pr_monthly).map(function(img){
  return img.addBands(dem).addBands(lc)
  .copyProperties(img, img.propertyNames())
  })

// modelling 


var pr_model = collection.map(function(img){
  var band_names = img.bandNames();
  var band_names_indep  = img.bandNames().remove('precipitation')
  
  var training = img.stratifiedSample({
    numPoints: 100, classBand: 'precipitation', region: geometry, scale: 1000
    });
    
  var model = ee.Classifier.smileGradientTreeBoost(100).train({
    features: training, classProperty: 'precipitation', inputProperties: band_names
    }).setOutputMode('REGRESSION');
    
  var pr1000 = img.select(band_names_indep).classify(model)
  
  return pr1000.rename('pr1000').addBands(img.select(['precipitation'],['pr27000']))
  .copyProperties(img, img.propertyNames())
  
  });
  
var cor = [45.9347467400223,36.93317086167252]

var geometry2 = BD_ROI

var roi = BD_COUNTRY
  

  
Map.centerObject(roi)
Map.addLayer(roi)
  
Map.addLayer(pr_model.select(['pr27000']).toBands().clip(roi), [], 'pr_initial', false)
Map.addLayer(pr_model.select(['pr1000']).toBands().clip(roi), [], 'pr_sharpened', false)


var pr_mean = pr_model.select('pr1000').mean()

var pr_1km_cor = pr_model.map(function(img){
  return img.select('pr1000').add(img.select('pr27000').subtract(pr_mean))
  .copyProperties(img,img.propertyNames())
  })


Map.addLayer(pr_1km_cor.toBands().clip(roi), [], 'pr_sharpened_cor', false)

Export.image.toDrive({
  image:  pr_1km_cor.toBands().clip(roi), 
  description: 'pr_1km_cor_v2', 
  region: roi, 
  crs: 'EPSG:4326', 
  folder: 'test', 
  scale: 1000
  })


Export.image.toDrive({
  image:  pr_model.select(['pr27000']).toBands().clip(roi), 
  description: 'pr_27km', 
  region: roi, 
  crs: 'EPSG:4326', 
  folder: 'test', 
  scale: 27000
  })

Export.image.toDrive({
  image:  pr_model.select(['pr1000']).toBands().clip(roi), 
  description: 'pr_1km', 
  region: roi, 
  crs: 'EPSG:4326', 
  folder: 'test', 
  scale: 1000
  })


