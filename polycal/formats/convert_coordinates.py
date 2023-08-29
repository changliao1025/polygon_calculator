import importlib
from polycal.classes.vertex import pyvertex
from polycal.classes.edge import pyedge


from polycal.classes.cell import pycell


from polycal.external.pyearth.gis.gdal.gdal_functions import reproject_coordinates
iFlag_cython = importlib.util.find_spec("cython") 
if iFlag_cython is not None:
    from polycal.algorithms.cython.kernel import calculate_angle_betwen_vertex
    from polycal.algorithms.cython.kernel import calculate_distance_to_plane
else:
    from polycal.external.pyearth.gis.gdal.gdal_functions import  calculate_angle_betwen_vertex
    from polycal.external.pyearth.gis.gdal.gdal_functions import calculate_distance_to_plane

def convert_gcs_coordinates_to_cell(    
                                    dLongitude_center_in,     
                                    dLatitude_center_in,         
                                    aCoordinates_gcs_in,        
                                    iFlag_simplify_in=None):
    
    
   

    if iFlag_simplify_in is None:
        iFlag_simplify_in = 0
    else:
        iFlag_simplify_in = iFlag_simplify_in

    #the closed polygon has a duplicate point (start and end are the same)
    npoint = len(aCoordinates_gcs_in)    
    aVertex=list()              
    aEdge=list()    
    for i in range(npoint-1):
        x = aCoordinates_gcs_in[i][0]
        y = aCoordinates_gcs_in[i][1]
        dummy = dict()
        dummy['dLongitude_degree'] = x
        dummy['dLatitude_degree'] = y
        pVertex = pyvertex(dummy)
        aVertex.append(pVertex)

    if iFlag_simplify_in ==1:
        aVertex_simple=list()  

        for i in range(npoint-1):
            if i == 0 : #the first one
                pv_start = aVertex[npoint-2]
                pv_middle = aVertex[i]
                pv_end = aVertex[i+1]                
            else:
                if i == npoint-2: #the last one
                    pv_start = aVertex[i-1]
                    pv_middle = aVertex[i]
                    pv_end = aVertex[0]
                else:
                    pv_start = aVertex[i-1]
                    pv_middle = aVertex[i]
                    pv_end = aVertex[i+1]
                    
            #calculate the angle between the three points
            x1 = pv_start.dLongitude_degree
            y1 = pv_start.dLatitude_degree
            x2 = pv_middle.dLongitude_degree
            y2 = pv_middle.dLatitude_degree
            x3 = pv_end.dLongitude_degree
            y3 = pv_end.dLatitude_degree
            angle3deg = calculate_angle_betwen_vertex(x1,y1, x2,y2, x3,y3)
            if  angle3deg > 175: #care
                pass
            else:
                #the center is a actual vertex
                aVertex_simple.append(pv_middle)
                
        #replace the original vertex
        aVertex = aVertex_simple
        pass
    else:
        pass

    npoint2 = len(aVertex) 
    for j in range(npoint2-1):
        pEdge = pyedge( aVertex[j], aVertex[j+1] )
        aEdge.append(pEdge)

    #add the last one    
    pEdge = pyedge( aVertex[npoint2-1], aVertex[0] )
    aEdge.append(pEdge)
    

    pCell = pycell( dLongitude_center_in, dLatitude_center_in, aEdge, aVertex)
    return pCell
   



