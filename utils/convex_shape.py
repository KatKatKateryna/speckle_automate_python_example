
import json
import numpy as np
from shapely.geometry import MultiLineString
from shapely.ops import unary_union, polygonize
from scipy.spatial import Delaunay
from collections import Counter
import itertools

from specklepy.objects.geometry import Polyline, Point, Mesh, Line

from utils.utils_other import COLOR_VISIBILITY 

def concave_hull(coords):  # coords is a 2D numpy array
    from shapely import to_geojson, convex_hull, MultiPoint, Polygon
    hull = convex_hull(MultiPoint([(pt[0], pt[1], pt[2]) for pt in coords]))
    area = to_geojson(hull) # POLYGON to geojson 
    area = json.loads(area)

    vertices = []
    colors = []

    for i,c in enumerate(area["coordinates"][0]):
        if i != len(area["coordinates"][0])-1:
            if len(c)<3:
                vertices.extend( c+[coords[0][2]] )
            else: vertices.extend(c)
            colors.append(COLOR_VISIBILITY)
    
    mesh = Mesh.create(vertices=vertices, colors = colors, faces= [ int(len(vertices)/3) ] + list(range( int(len(vertices)/3) )) )
    return mesh
