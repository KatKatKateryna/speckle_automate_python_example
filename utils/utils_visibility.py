

import math
from typing import List

import numpy as np
from specklepy.objects.geometry import Mesh


def cross_product(pt1, pt2):
    return [ (pt1[1] * pt2[2]) - (pt1[2] * pt2[1]),
             (pt1[2] * pt2[0]) - (pt1[0] * pt2[2]),
             (pt1[0] * pt2[1]) - (pt1[1] * pt2[0]) ]

def dot(pt1: List, pt2: List):
    return (pt1[0] * pt2[0]) + (pt1[1] * pt2[1]) + (pt1[2] * pt2[2])

def normalize(pt: List, tolerance= 1e-10):
    magnitude = dot(pt, pt) ** 0.5
    if abs(magnitude - 1) < tolerance:
        return pt

    if magnitude !=0: scale = 1.0 / magnitude
    else: scale = 1.0
    normalized_vector = [coordinate * scale for coordinate in pt]
    return normalized_vector 

def createPlane(pt1: List, pt2: List, pt3: List):
    vector1to2 = [ pt2[0]-pt1[0], pt2[1]-pt1[1], pt2[2]-pt1[2] ]
    vector1to3 = [ pt3[0]-pt1[0], pt3[1]-pt1[1], pt3[2]-pt1[2] ]

    u_direction = normalize(vector1to2)
    normal = cross_product( u_direction, vector1to3 )
    return {'origin': pt1, 'normal': normal}

#def project_to_plane_on_z(point: List, plane: dict):
#    d = dot(plane["normal"], plane["origin"])
#    z_value_on_plane = (d - (plane["normal"][0] * point[0]) - (plane["normal"][1] * point[1])) / plane["normal"][2] 
#    return z_value_on_plane

def LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
    # https://gist.github.com/TimSC/8c25ca941d614bf48ebba6b473747d72
    ndotu = planeNormal.dot(rayDirection)
    if abs(ndotu) < epsilon:
        raise RuntimeError("no intersection or line is within plane")

    w = rayPoint - planePoint
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si * rayDirection + planePoint
    return Psi

def containsPoint(pt: np.array, mesh: Mesh):
    from shapely.geometry import Point
    from shapely.geometry.polygon import Polygon

    point = Point(pt[0], pt[1])
    polygon = Polygon([ (mesh.vertices[i*3], mesh.vertices[i*3+1]) for i,v in enumerate(mesh.vertices) if i*3<len(mesh.vertices)])
    result = polygon.contains(point)
    return result

def rotate_vector(vector, half_angle=60):

    half_angle = np.deg2rad(half_angle)

    vectors = []
    count = 10
    for c in range(count):
        # xy plane
        x = vector[0] * math.cos(half_angle*c/count) - vector[1] * math.sin(half_angle*c/count)
        y = vector[0] * math.sin(half_angle*c/count) + vector[1] * math.cos(half_angle*c/count)
        vectors.append([x, y, vector[2]] )
        for c in range(count):
            # yz plane
            vector1 = vectors[len(vectors)-1]
            y = vector1[1] * math.cos(half_angle*c/count) - vector1[2] * math.sin(half_angle*c/count)
            z = vector1[1] * math.sin(half_angle*c/count) + vector1[2] * math.cos(half_angle*c/count)
            vectors.append(np.array( [vector1[0], y, z] ))
        
        x = vector[0] * math.cos(-half_angle*c/count) - vector[1] * math.sin(-half_angle*c/count)
        y = vector[0] * math.sin(-half_angle*c/count) + vector[1] * math.cos(-half_angle*c/count)
        vectors.append( [x, y, vector[2]])
        for c in range(count):
            # yz plane
            vector2 = vectors[len(vectors)-1]
            y = vector2[1] * math.cos(half_angle*c/count) - vector2[2] * math.sin(half_angle*c/count)
            z = vector2[1] * math.sin(half_angle*c/count) + vector2[2] * math.cos(half_angle*c/count)
            vectors.append(np.array( [vector2[0], y, z] ))
    
    return vectors

def projectToPolygon(point: List[float], direction: List[float], mesh: Mesh):
    allIntersections = []

    pt1 = mesh.vertices[0:3]
    pt2 = mesh.vertices[3:6]
    pt3 = mesh.vertices[6:9]
    plane = createPlane(pt1, pt2, pt3)
    #z = project_to_plane_on_z(point, plane)

    #Define plane
    planeNormal = np.array(plane["normal"])
    planePoint = np.array(plane["origin"]) #Any point on the plane

    #Define ray
    vectors = rotate_vector(direction)
    #rayDirection = np.array([0, -1, -1])
    for direct in vectors:
        rayPoint = np.array(point) #Any point along the ray
        dir = np.array(direct)

        Psi = LinePlaneCollision(planeNormal, planePoint, dir, rayPoint)
        print ("intersection at", Psi)

        result = containsPoint(Psi, mesh)
        print(result)
        if result is True:
            allIntersections.append(Psi)

    return allIntersections



