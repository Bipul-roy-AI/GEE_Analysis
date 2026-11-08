"""National products with explicit units, QA and meaningful native-scale exports.
All date intervals are half-open. No fine-scale resampling is called downscaling.
"""
import ee
from .core import Product, boundaries

THEMES = ('climate', 'vegetation', 'drought', 'water', 'flood', 'terrain',
          'landcover', 'forest', 'agriculture', 'urban', 'population',
          'air_quality', 'soil', 'water_quality', 'snow', 'ocean')


def collection(asset, start, end):
    return ee.ImageCollection(asset).filterDate(start, end).filterBounds(boundaries()[0])


def s2(start, end):
    def clean(i):
        scl = i.select('SCL')
        mask = scl.neq(0).And(scl.neq(1)).And(scl.neq(3)).And(scl.neq(8)).And(
            scl.neq(9)).And(scl.neq(10)).And(scl.neq(11))
        return i.select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']).multiply(0.0001).updateMask(mask).copyProperties(i, ['system:time_start'])
    return collection('COPERNICUS/S2_SR_HARMONIZED', start, end).map(clean)


def nd(i, a, b, name):
    # expression avoids normalizedDifference's implicit negative-input masking.
    x, y = i.select(a), i.select(b)
    return x.subtract(y).divide(x.add(y)).updateMask(x.add(y).abs().gt(1e-6)).rename(name)


def mod_ndvi(start, end):
    def clean(i):
        return i.select('NDVI').multiply(.0001).updateMask(i.select('SummaryQA').lte(1)).rename('NDVI').copyProperties(i, ['system:time_start'])
    return collection('MODIS/061/MOD13Q1', start, end).map(clean)


def products(theme, start='2024-01-01', end='2025-01-01'):
    if theme == 'climate':
        rain = collection('UCSB-CHG/CHIRPS/DAILY', start, end).select('precipitation')
        era = collection('ECMWF/ERA5_LAND/DAILY_AGGR', start, end)
        wind = era.map(lambda i: i.select('u_component_of_wind_10m').pow(2).add(i.select('v_component_of_wind_10m').pow(2)).sqrt())
        return [Product('rain_total', rain.sum(), 5566, 'mm'),
                Product('wet_days_ge1mm', rain.map(lambda i: i.gte(1)).sum(), 5566, 'days'),
                Product('heavy_rain_days_ge50mm', rain.map(lambda i: i.gte(50)).sum(), 5566, 'days'),
                Product('air_temperature_mean', era.select('temperature_2m').mean().subtract(273.15), 11132, 'degC'),
                Product('wind_speed_mean', wind.mean(), 11132, 'm/s')]
    if theme == 'vegetation':
        c = mod_ndvi(start, end)
        annual = ee.ImageCollection.fromImages([mod_ndvi(f'{y}-01-01', f'{y+1}-01-01').mean().addBands(
            ee.Image.constant(y).float().rename('year')).select(['year','NDVI']) for y in range(2001, 2025)])
        return [Product('NDVI_mean', c.mean(), 250, 'dimensionless'),
                Product('NDVI_valid_composites', c.count(), 250, 'observations'),
                Product('NDVI_Sen_slope_2001_2024', annual.reduce(ee.Reducer.sensSlope()), 250, 'NDVI/year; offset NDVI')]
    if theme == 'drought':
        # Compare the same calendar month with its climatology to avoid seasonal bias.
        month = int(start[5:7])
        baseline = mod_ndvi('2001-01-01','2021-01-01').filter(ee.Filter.calendarRange(month, month, 'month'))
        target = mod_ndvi(start, end).filter(ee.Filter.calendarRange(month, month, 'month')).mean()
        low, high = baseline.min(), baseline.max()
        spread = high.subtract(low)
        vci = target.subtract(low).divide(spread).multiply(100).updateMask(spread.gt(.01)).clamp(0,100).rename('VCI')
        return [Product(f'VCI_month_{month:02d}_baseline_2001_2020', vci, 250, 'percent')]
    if theme in ('water', 'water_quality'):
        comp = s2(start, end).median()
        mndwi = nd(comp, 'B3', 'B11', 'MNDWI')
        water = mndwi.gt(0).And(nd(comp,'B8','B4','NDVI').lt(.3))
        if theme == 'water':
            return [Product('MNDWI', mndwi, 20, 'dimensionless'),
                    Product('spectral_water_screen', water.rename('water'), 20, 'class', 'categorical', (0,1)),
                    Product('historical_water_occurrence_1984_2021', ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence'), 30, 'percent')]
        return [Product('NDTI_turbidity_proxy', nd(comp,'B4','B3','NDTI').updateMask(water),20,'dimensionless; uncalibrated proxy'),
                Product('green_blue_ratio', comp.select('B3').divide(comp.select('B2')).updateMask(water.And(comp.select('B2').gt(.001))).rename('green_blue'),20,'dimensionless; uncalibrated proxy')]
    if theme == 'flood':
        # Bangladesh August 2024 event; separate dates from generic annual settings.
        def radar(a,b):
            return collection('COPERNICUS/S1_GRD', a,b).filter(ee.Filter.eq('instrumentMode','IW')).filter(
                ee.Filter.eq('orbitProperties_pass','DESCENDING')).filter(
                ee.Filter.listContains('transmitterReceiverPolarisation','VH')).select('VH')
        before_c, after_c = radar('2024-07-01','2024-08-01'), radar('2024-08-20','2024-09-01')
        # Match relative orbits present in both windows to reduce geometry bias.
        common = ee.List(before_c.aggregate_array('relativeOrbitNumber_start')).distinct()
        common = common.removeAll(common.removeAll(ee.List(after_c.aggregate_array('relativeOrbitNumber_start')).distinct()))
        before = before_c.filter(ee.Filter.inList('relativeOrbitNumber_start',common)).median().focalMedian(30,'circle','meters')
        after = after_c.filter(ee.Filter.inList('relativeOrbitNumber_start',common)).median().focalMedian(30,'circle','meters')
        drop = before.subtract(after).rename('VH_drop_dB')
        permanent = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('seasonality').gte(10)
        slope = ee.Terrain.slope(ee.Image('USGS/SRTMGL1_003'))
        candidate = drop.gt(3).And(after.lt(-17)).And(permanent.Not()).And(slope.lt(5))
        candidate = candidate.And(candidate.selfMask().connectedPixelCount(100,True).gte(8)).rename('flood_candidate')
        return [Product('VH_drop_2024Aug',drop,30,'dB'), Product('flood_candidate_2024Aug',candidate,30,'class','categorical',(1,))]
    if theme == 'terrain':
        dem = ee.Image('USGS/SRTMGL1_003')
        return [Product('elevation',dem,30,'m EGM96'), Product('slope',ee.Terrain.slope(dem),30,'degrees'),
                Product('aspect',ee.Terrain.aspect(dem),30,'degrees clockwise from north')]
    if theme == 'landcover':
        c = collection('GOOGLE/DYNAMICWORLD/V1',start,end)
        probabilities = c.select(['water','trees','grass','flooded_vegetation','crops','shrub_and_scrub','built','bare','snow_and_ice']).mean()
        return [Product('DW_modal_class',c.select('label').mode(),10,'class','categorical',tuple(range(9))),
                Product('DW_mean_probabilities',probabilities,10,'probability')]
    if theme == 'forest':
        # Version explicitly pinned; loss != deforestation, gain ends in 2012.
        h = ee.Image('UMD/hansen/global_forest_change_2024_v1_12')
        return [Product('treecover2000',h.select('treecover2000'),30,'percent'),
                Product('lossyear_2001_2024',h.select('lossyear'),30,'year since 2000','categorical',tuple(range(1,25)))]
    if theme == 'agriculture':
        lc = collection('MODIS/061/MCD12Q1',start,end).select('LC_Type1').first()
        crops = ee.Image(lc).eq(12).Or(ee.Image(lc).eq(14)).rename('cropland_or_mosaic')
        return [Product('cropland_or_mosaic',crops,500,'class','categorical',(0,1)),
                Product('cropland_NDVI',mod_ndvi(start,end).mean().updateMask(crops),250,'dimensionless')]
    if theme == 'urban':
        def lst_clean(i):
            qa = i.select('QC_Day')
            return i.select('LST_Day_1km').multiply(.02).subtract(273.15).updateMask(qa.bitwiseAnd(3).eq(0).And(qa.rightShift(6).bitwiseAnd(3).lte(1)))
        lst = collection('MODIS/061/MOD11A2',start,end).map(lst_clean).mean()
        light = collection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG',start,end).map(
            lambda i:i.select('avg_rad').updateMask(i.select('cf_cvg').gt(0))).mean()
        return [Product('daytime_LST',lst,1000,'degC; surface not air temperature'),
                Product('night_radiance',light,500,'nW/cm2/sr')]
    if theme == 'population':
        # Fixed census-model epoch, not a claim of current population.
        pop = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020').select('population_count')
        return [Product('population_2020',pop,100,'people','count')]
    if theme == 'air_quality':
        return [Product(name,collection(asset,start,end).select(band).mean(),1113,unit)
                for name,asset,band,unit in [
                    ('NO2_column','COPERNICUS/S5P/OFFL/L3_NO2','tropospheric_NO2_column_number_density','mol/m2'),
                    ('CO_column','COPERNICUS/S5P/OFFL/L3_CO','CO_column_number_density','mol/m2'),
                    ('CH4_column','COPERNICUS/S5P/OFFL/L3_CH4','CH4_column_volume_mixing_ratio_dry_air','ppb')]]
    if theme == 'soil':
        soil = collection('ECMWF/ERA5_LAND/DAILY_AGGR',start,end).select('volumetric_soil_water_layer_1').mean()
        return [Product('soil_water_top_7cm',soil,11132,'m3/m3'),
                Product('soil_pH_topsoil',ee.Image('OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02').select('b0').divide(10),250,'pH')]
    if theme == 'snow':
        def clean(i):
            snow=i.select('NDSI_Snow_Cover')
            return snow.updateMask(snow.lte(100)).gte(50).rename('snow_observed')
        c=collection('MODIS/061/MOD10A1',start,end).map(clean)
        return [Product('snow_observed_days',c.sum(),500,'valid observations with snow'),
                Product('snow_valid_days',c.count(),500,'valid observations')]
    if theme == 'ocean':
        # Strict national land boundary yields coastal mixed pixels or no data.
        c=collection('HYCOM/sea_temp_salinity',start,end)
        return [Product('surface_salinity',c.select('salinity_0').mean().multiply(.001).add(20),8905,'psu'),
                Product('surface_temperature',c.select('water_temp_0').mean().multiply(.001).add(20),8905,'degC')]
    raise ValueError(f'Unknown theme: {theme}')
