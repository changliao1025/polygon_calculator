#import gdal 
import os
from datetime import datetime
from osgeo import ogr, osr
import rtree

def calculate_polygon_diff_using_rtree():
    start_time = datetime.now()
    sFilename_base = '/qfs/people/liao313/workspace/python/polygon_calculator/data/structured/198001.geojson'
    sFilename_new = '/qfs/people/liao313/workspace/python/polygon_calculator/data/unstructured/198001.geojson'
    sFilename_output_in = '/qfs/people/liao313/workspace/python/polygon_calculator/data/198001_diff_rtree.geojson'

    #read the base file
    pDriver_geojson = ogr.GetDriverByName('GeoJSON')
    #delete if file exist
    if os.path.exists(sFilename_output_in):
        os.remove(sFilename_output_in)
        
    pDataset_out = pDriver_geojson.CreateDataSource(sFilename_output_in)
    pSpatial_reference_gcs = osr.SpatialReference()  
    pSpatial_reference_gcs.ImportFromEPSG(4326)    # WGS84 lat/lon

    pLayerOut = pDataset_out.CreateLayer('runoff_diff', pSpatial_reference_gcs, ogr.wkbPolygon)
    # Add one attribute
    pLayerOut.CreateField(ogr.FieldDefn('polygonid', ogr.OFTInteger64)) #long type for high resolution
    pLayerOut.CreateField(ogr.FieldDefn('runoff_diff', ogr.OFTReal)) #long type for high resolution
   
    pLayerDefn = pLayerOut.GetLayerDefn()
    pFeatureOut = ogr.Feature(pLayerDefn)  
    #read the base file

    pDataset_base = pDriver_geojson.Open(sFilename_base, 0)
    #find the numebr of geometries in the base file
    pLayer_base = pDataset_base.GetLayer()
    nFeature_base = pLayer_base.GetFeatureCount()
    index_base = rtree.index.Index()
    aRunoff_base = list()
    for i in range(nFeature_base):
        lID = i 
        pFeature_base = pLayer_base.GetFeature(i)
        pGeometry_base = pFeature_base.GetGeometryRef()    
        left, right, bottom, top= pGeometry_base.GetEnvelope()   
        pBound= (left, bottom, right, top)
        index_base.insert(lID, pBound)  #
        dRunoff_base = pFeature_base.GetField("qsur")
        aRunoff_base.append(dRunoff_base)

    #read the new file
    pDataset_new = pDriver_geojson.Open(sFilename_new, 0)
    pLayer_new = pDataset_new.GetLayer()
    nFeature_new =  pLayer_new.GetFeatureCount()
    lID_polygon = 1
    for j in range(nFeature_new):
        lID = j
        pFeature_new = pLayer_new.GetFeature(j)
        pGeometry_new = pFeature_new.GetGeometryRef()                    
        
        left, right, bottom, top= pGeometry_new.GetEnvelope()   
        pBound= (left, bottom, right, top)
        aIntersect = list(index_base.intersection(pBound))
        
        dRunoff_new = pFeature_new.GetField("qsur")
        for k in aIntersect:
            pFeature_base = pLayer_base.GetFeature(k)
            pGeometry_base = pFeature_base.GetGeometryRef()        
            dRunoff_base = aRunoff_base[k]     
            runoff_diff  = dRunoff_new - dRunoff_base
            iFlag_intersect = pGeometry_new.Intersects( pGeometry_base )
            if( iFlag_intersect == True):
                pGeometry_intersect = pGeometry_new.Intersection(pGeometry_base)   
                pGeometrytype_intersect = pGeometry_intersect.GetGeometryName()
                if pGeometrytype_intersect == 'POLYGON':  
                    pFeatureOut.SetGeometry(pGeometry_intersect)
                    pFeatureOut.SetField("polygonid", lID_polygon)         
                    pFeatureOut.SetField("runoff_diff", runoff_diff)    
                    pLayerOut.CreateFeature(pFeatureOut)    
                    lID_polygon = lID_polygon + 1
                else:
                    print('pGeometrytype_intersect:', lID_polygon, pGeometrytype_intersect)
    
    #close files
    pDataset_base = None
    pDataset_new = None
    end_time = datetime.now()
    # get difference
    delta = end_time - start_time
    
    sec = delta.total_seconds()
    print('difference in seconds:', sec)
    
    min = sec / 60
    print('difference in minutes:', min)
    
    return None

if __name__ == '__main__':
    calculate_polygon_diff_using_rtree()