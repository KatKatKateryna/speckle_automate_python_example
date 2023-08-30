

import math
from typing import List
from scipy.linalg import expm, norm

import numpy as np
from numpy import cross, eye, dot
from operator import add
from specklepy.objects.geometry import Mesh, Point, Line 


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

def containsPoint(pt: np.array, mesh: List):
    from shapely.geometry import Point
    from shapely.geometry.polygon import Polygon

    point = Point(pt[0], pt[1])
    polygon = Polygon([ (m[0],m[1],m[2]) for i,m in enumerate(mesh) ])
    result = polygon.contains(point)
    return result


def M(axis, theta):
    # https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
    return expm(cross(eye(3), axis/norm(axis)*theta))

def rotate_vector(pt_origin, vector, half_angl_degrees=70):

    half_angle = np.deg2rad(half_angl_degrees)
    step = 10 # degrees

    vectors = []
    axis = vector # direction
    #vectors.append( np.array( list( map(add, pt_origin, vector) )) )

    count = int(half_angl_degrees/step)
    for c in range(0, count+1):
        # xy plane
        x = vector[0] * math.cos(half_angle*c/count) - vector[1] * math.sin(half_angle*c/count)
        y = vector[0] * math.sin(half_angle*c/count) + vector[1] * math.cos(half_angle*c/count)
        
        v = [x,y,vector[2]]
        if c==0:
            vectors.append( np.array( list( map(add, pt_origin, v) )) ) 
            continue 
        
        for a in range(0,360,step):
            theta = a*math.pi / 180 
            M0 = M(vector, theta)
            newDir = dot(M0,v)
            vectors.append( np.array( list( map(add, pt_origin, newDir) )) ) 

    return vectors

def getAllPlanes(mesh: Mesh):
    meshList = []

    i = 0
    fs = mesh.faces
    for count, f in enumerate(fs):
        if i >= len(fs)-1: break
        current_face_index = fs[i]
        pt_list = []
        for x in range(i+1, i+fs[i]+1):
            ind = fs[x]
            pt_list.append( [mesh.vertices[3*ind], mesh.vertices[3*ind+1], mesh.vertices[3*ind+2]] )
        #pt1 = [mesh.vertices[3*fs[i+1]], mesh.vertices[3*fs[i+1]+1], mesh.vertices[3*fs[i+1]+2]]
        #pt2 = [mesh.vertices[3*fs[i+2]], mesh.vertices[3*fs[i+2]+1], mesh.vertices[3*fs[i+2]+2]]
        #pt3 = [mesh.vertices[3*fs[i+3]], mesh.vertices[3*fs[i+3]+1], mesh.vertices[3*fs[i+3]+2]]
        meshList.append(pt_list)
        i += fs[i] + 1 
    return meshList
    
def projectToPolygon(point: List[float], vectors: List[List[float]], usedVectors: dict, mesh: Mesh):
    allIntersections = []

    meshes = getAllPlanes(mesh)
    for m in meshes: 

        pt1, pt2, pt3 = m[:3]
        plane = createPlane(pt1, pt2, pt3)

        #Define plane
        planeNormal = np.array(plane["normal"])
        planePoint = np.array(plane["origin"]) #Any point on the plane

        #Define ray
        for i, direct in enumerate(vectors):
            rayPoint = np.array(point) #Any point along the ray
            dir = np.array(direct) - rayPoint

            normalOriginal = normalize( dir )

            collision = LinePlaneCollision(planeNormal, planePoint, dir, rayPoint)
            if collision is None: continue 

            normalCollision = normalize( np.array(collision)-rayPoint )
            if int(normalCollision[0]*1000) != int(normalOriginal[0]*1000): continue # if different direction 

            result = containsPoint(collision, m)

            if result is True:
                #allIntersections.append(planePoint)
                pt_dir = Point.from_list([planePoint[0], planePoint[1], planePoint[2]])
                pt_dir.vectorId = i

                pt_intersect = Point.from_list([collision[0], collision[1], collision[2]])
                pt_intersect.vectorId = i

                allIntersections.append(pt_intersect)

                try: val = usedVectors[i] + 1
                except: val = 1
                usedVectors.update({i:val})

            # only 1 vector
            #break
        # only 1 side of building 
        #break

    return allIntersections, usedVectors



