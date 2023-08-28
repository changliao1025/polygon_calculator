#import gdal 
import os
from osgeo import ogr, osr


def calculate_polygon_difference():

    sFilename_base = '/qfs/people/liao313/workspace/python/polygon_calculator/data/structured/198001.geojson'
    sFilename_new = '/qfs/people/liao313/workspace/python/polygon_calculator/data/unstructured/198001.geojson'
    sFilename_output_in = '/qfs/people/liao313/workspace/python/polygon_calculator/data/198001_diff.geojson'

    #read the base file
    pDriver_geojson = ogr.GetDriverByName('GeoJSON')
    #delete if file exist
    if os.path.exists(sFilename_output_in):
        os.remove(sFilename_output_in)
    pDataset_out = pDriver_geojson.CreateDataSource(sFilename_output_in)
    pSpatial_reference_gcs = osr.SpatialReference()  
    pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/lon

    pLayerOut = pDataset_out.CreateLayer('runoff_diff', pSpatial_reference_gcs, ogr.wkbMultiLineString)
    # Add one attribute
    pLayerOut.CreateField(ogr.FieldDefn('polygonid', ogr.OFTInteger64)) #long type for high resolution
    pLayerOut.CreateField(ogr.FieldDefn('runoff_diff', ogr.OFTReal)) #long type for high resolution
   
    pLayerDefn = pLayerOut.GetLayerDefn()
    pFeatureOut = ogr.Feature(pLayerDefn)  

    pDataset_base = pDriver_geojson.Open(sFilename_base, 0)
    #read the new file
    pDataset_new = pDriver_geojson.Open(sFilename_new, 0)

    #find the numebr of geometries in the base file
    pLayer_base = pDataset_base.GetLayer()
    nFeature_base = pLayer_base.GetFeatureCount()

    #do the same for the new file
    pLayer_new = pDataset_new.GetLayer()
    nFeature_new =  pLayer_new.GetFeatureCount()
    lID_polygon = 1
    for i in range(nFeature_base):
        pFeature_base = pLayer_base.GetFeature(i)
        pGeometry_base = pFeature_base.GetGeometryRef()
        dRunoff_base = pFeature_base.GetField("qsur")

        for j in range(nFeature_new):
            pFeature_new = pLayer_new.GetFeature(j)
            pGeometry_new = pFeature_new.GetGeometryRef()
            iFlag_intersect = pGeometry_new.Intersects( pGeometry_base )
            if( iFlag_intersect == True):
                iFlag_intersected = 1
                pGeometry_intersect = pGeometry_new.Intersection(pGeometry_base)                     
                pGeometrytype_intersect = pGeometry_intersect.GetGeometryName()
                if pGeometrytype_intersect == 'POLYGON':
                    dRunoff_new = pFeature_new.GetField("qsur")
                    runoff_diff  = dRunoff_new - dRunoff_base
                    pFeatureOut.SetGeometry(pGeometry_intersect)
                    pFeatureOut.SetField("polygonid", lID_polygon)         
                    pFeatureOut.SetField("runoff_diff", runoff_diff)    
                      
                    pLayerOut.CreateFeature(pFeatureOut)    
                    lID_polygon = lID_polygon + 1
    
    #close files
    pDataset_base = None
    pDataset_new = None
    
    return None

if __name__ == '__main__':
    calculate_polygon_difference()