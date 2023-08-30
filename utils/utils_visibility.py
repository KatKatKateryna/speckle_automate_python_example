

import math
from typing import List
from scipy.linalg import expm, norm

import numpy as np
from numpy import cross, eye, dot
from operator import add
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
        #raise RuntimeError("no intersection or line is within plane")
        return None 

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


def M(axis, theta):
    # https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
    return expm(cross(eye(3), axis/norm(axis)*theta))

def rotate_vector(pt_origin, vector, half_angl_degrees=60):

    half_angle = np.deg2rad(half_angl_degrees)
    step = 10 # degrees

    vectors = []
    axis = vector # direction
    count = int(half_angl_degrees/step)
    for c in range(1, count+1):
        # xy plane
        x = vector[0] * math.cos(half_angle*c/count) - vector[1] * math.sin(half_angle*c/count)
        y = vector[0] * math.sin(half_angle*c/count) + vector[1] * math.cos(half_angle*c/count)
        #vectors.append([x, y, pt_origin[2] + vector[2]] )
        
        v = [x,y,vector[2]]
        for a in range(0,360,step):
            theta = a*math.pi / 180 
            M0 = M(vector, theta)
            newDir = dot(M0,v)
            vectors.append( np.array( list( map(add, pt_origin, newDir) )) ) 

        #for c in range(count):
        #    # yz plane
        #    vector1 = vectors[len(vectors)-1]
        #    y = vector1[1] * math.cos(half_angle*c/count) - vector1[2] * math.sin(half_angle*c/count)
        #    z = vector1[1] * math.sin(half_angle*c/count) + vector1[2] * math.cos(half_angle*c/count)
        #    vectors.append(np.array( [pt_origin[0] + vector1[0], y, z] ))
        
        x = vector[0] * math.cos(-half_angle*c/count) - vector[1] * math.sin(-half_angle*c/count)
        y = vector[0] * math.sin(-half_angle*c/count) + vector[1] * math.cos(-half_angle*c/count)
        #vectors.append( [x, y, pt_origin[2] + vector[2]])

    return vectors

def getAllPlanes(mesh: Mesh):
    meshList = []

    i = 0
    fs = mesh.faces
    for count, f in enumerate(fs):
        if i >= len(fs)-1: break
        current_face_index = fs[i]
        pt1 = [mesh.vertices[3*fs[i]+1], mesh.vertices[3*fs[i]+2], mesh.vertices[3*fs[i]+3]]
        pt2 = [mesh.vertices[3*fs[i]+4], mesh.vertices[3*fs[i]+5], mesh.vertices[3*fs[i]+6]]
        pt3 = [mesh.vertices[3*fs[i]+7], mesh.vertices[3*fs[i]+8], mesh.vertices[3*fs[i]+9]]
        meshList.append([pt1, pt2, pt3])
        i += fs[i] + 1 
    return meshList
    
def projectToPolygon(point: List[float], vectors: List, mesh: Mesh):
    allIntersections = []

    meshes = getAllPlanes(mesh)
    for m in meshes: 

        pt1, pt2, pt3 = m 
        plane = createPlane(pt1, pt2, pt3)
        #z = project_to_plane_on_z(point, plane)

        #Define plane
        planeNormal = np.array(plane["normal"])
        planePoint = np.array(plane["origin"]) #Any point on the plane

        #Define ray
        
        #rayDirection = np.array([0, -1, -1])
        for direct in vectors:
            rayPoint = np.array(point) #Any point along the ray
            dir = np.array(direct)

            Psi = LinePlaneCollision(planeNormal, planePoint, dir, rayPoint)
            if Psi is None: continue 

            #print (f"intersection at {Psi}")

            result = containsPoint(Psi, mesh)
            if result is True:
                allIntersections.append(Psi)

    return allIntersections



