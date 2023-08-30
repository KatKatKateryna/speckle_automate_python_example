
from typing import List, Union
import json
import numpy as np
from shapely.geometry import MultiLineString
from shapely.ops import unary_union, polygonize
from scipy.spatial import Delaunay
from collections import Counter
import itertools

from specklepy.objects.geometry import Polyline, Point, Mesh, Line

from utils.utils_other import COLOR_VISIBILITY 

def concave_hull_create(coords: List[np.array]):  # coords is a 2D numpy array

    from shapely import to_geojson, convex_hull, concave_hull, MultiPoint, Polygon
    vertices = []
    colors = []

    if len(coords) < 4: return None
    else:
        vertices2d = [ remapPt(p, toHorizontal = True) for p in coords ]

        hull = convex_hull(MultiPoint([(pt[0], pt[1], pt[2]) for pt in vertices2d]) )#, ratio=0.1)
        area = to_geojson(hull) # POLYGON to geojson 
        area = json.loads(area)
        if len(area["coordinates"]) > 1: return None
        new_coords = area["coordinates"][0]
    
    for i,c in enumerate(new_coords):
        if i != len(new_coords)-1:
            vert2d = c + [0] 
            vert3d = remapPt(vert2d, toHorizontal = False)

            if vert3d is not None:
                vertices.extend(vert3d)
            colors.append(COLOR_VISIBILITY)
    
    mesh = Mesh.create(vertices=vertices, colors = colors, faces= [ int(len(vertices)/3) ] + list(range( int(len(vertices)/3) )) )
    return mesh

def remapPt( pt: Union[np.array, list], toHorizontal = True ):
    pt3d = None
    return pt