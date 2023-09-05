

r'''
- to install poetry, in cmd: 
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install poetry 
- to add modules, in vs code:
poetry shell
poetry add numpy

# Reprojecting:
https://pyproj4.github.io/pyproj/stable/examples.html

# Network analysis:
https://networkx.org/documentation/stable/auto_examples/index.html#examples-gallery
https://github.com/networkx/networkx
pandana
osmnet

# Satellite imagery
https://github.com/yannforget/landsatxplore

# Styling: 
https://github.com/pysal/mapclassify 

# Download elevation
https://github.com/bopen/elevation 

# Work with shapes
https://pypi.org/project/shapely/ 

# Geospatial data abstraction
https://pypi.org/project/GDAL/ 
first, download whl file here https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal , then pip install "....whl"

# Geospatial analysis 
https://github.com/geopandas/geopandas 

'''
from copy import copy
import json
import math
from typing import List
from specklepy.transports.server import ServerTransport
from specklepy.api.credentials import get_local_accounts
from specklepy.api.operations import receive, send
from specklepy.api.client import SpeckleClient
from specklepy.objects import Base
from specklepy.objects.geometry import Mesh, Line, Point, Pointcloud 
from specklepy.objects.other import Collection
from specklepy.api.models import Branch 

import numpy as np 
from operator import add, sub 
import matplotlib as mpl

from flatten import flatten_base, iterateBase
from utils.convex_shape import concave_hull_create, remapPt
from utils.getComment import get_comments
#from utils.utils_network import calculateAccessibility
from utils.utils_osm import getBuildings, getRoads
from utils.utils_other import RESULT_BRANCH, cleanPtsList, findMeshesNearby, sortPtsByMesh
from utils.utils_visibility import containsPoint, getAllPlanes, projectToPolygon, rotate_vector, expandPtsList
from utils.vectors import createPlane

r'''
mesh = [ [50,10,0], [50,10,10], [60,0,10], [60,0,0] ]
pt = [55,5,5]

plane3d = createPlane(*mesh[:3])
vert2d = remapPt(pt, True, plane3d)
mesh2d = [ remapPt(m, True, plane3d) for m in mesh ]

res = containsPoint(np.array(pt), mesh)

exit()
'''

server_url = "https://latest.speckle.dev/" #"https://speckle.xyz/" # project_data.speckle_server_url
project_id = "04a609b47c" #"4ea6a03993"# Kate's tests #"17b0b76d13" #project_data.project_id
#model_id = "main"
#version_id = "5d720c0998" #project_data.version_id
RADIUS = 50 #float(project_data.radius) 
KEYWORD = "window"
HALF_VIEW_DEGREES = 30
STEP_DEGREES = 5
#model_id = #project_data.model_id

account = get_local_accounts()[0]
client = SpeckleClient(server_url)
client.authenticate_with_token(account.token)
#branch: Branch = client.branch.get(project_id, model_id, 1)

#commit = branch.commits.items[0] 
server_transport = ServerTransport(project_id, client)


#exit()
r'''
# to delete:
commit = client.commit.get(project_id, version_id)
#################################

base = receive(commit.referencedObject, server_transport)

objects = [b for b in flatten_base(base)]
print(objects)
'''


def run(client, server_transport):
    
    onlyIllustrate = False 

    #model_id = "main"
    project_id = server_transport.stream_id
    pt_origin = [0, 0, 50]
    dir = [1,-1,-0.5]

    comments = get_comments(
        client,
        project_id,
    )
    pt_origin = None
    commitId = None
    for item in comments["comments"]["items"]:
        if KEYWORD.lower() in item["rawText"].lower():
            #viewerResources = item["viewerResources"]
            viewerState = item["viewerState"]
            commitId = viewerState["resources"]["request"]["resourceIdString"].split("@")[1]
            pt_origin: List[float] = viewerState["ui"]["selection"]

            pos: List[float] = viewerState["ui"]["camera"]["position"]
            target: List[float] = viewerState["ui"]["camera"]["target"]
            pt_origin = target
            dir = list( map(sub, pos, target) )
            break 
    if pt_origin is None or commitId is None: 
        return 

    commit = client.commit.get(project_id, commitId)
    base = receive(commit.referencedObject, server_transport)
    objects = [b for b in iterateBase(base)]

    lines = []
    cloud = []
    dir = np.array(dir)
    start = Point.from_list(pt_origin)
    vectors = rotate_vector(pt_origin, dir, HALF_VIEW_DEGREES, STEP_DEGREES)
    endPt = list( map(add,pt_origin,dir) )

    # just to find the line
    if onlyIllustrate is True:
        line = Line(start = start, end = Point.from_list(list( map(add,pt_origin,dir) )))
        line.units = "m"
        lines.append(line)
        for v in vectors:
            line = Line(start = start, end = Point.from_list( [v[0], v[1], v[2]]))
            line.units = "m"
            lines.append(line)
    
    ###########################
    else:
        usedVectors = {}
        all_pts = []
        count = 0
        all_geom = []
        for bld in objects:
            # get all intersection points 
            meshes = getAllPlanes(bld)
            for mesh in meshes:
                all_geom.append(mesh)
                pts, usedVectors = projectToPolygon(pt_origin, vectors, usedVectors, mesh, count) #Mesh.create(vertices = [0,0,0,5,0,0,5,19,0,0,14,0], faces=[4,0,1,2,3]))
                all_pts.extend(pts)
                count +=1

        cleanPts = cleanPtsList(pt_origin, all_pts, usedVectors)
        mesh_nearby = findMeshesNearby(cleanPts)

        ### expand number of pts around filtered rays 
        expandedPts2 = []
        expandedPts2, usedVectors2 = expandPtsList(pt_origin, cleanPts, {}, STEP_DEGREES, all_geom, mesh_nearby)

        ### expand number of pts around filtered rays 
        expandedPts3 = []
        clean_extended_pts = cleanPts + expandedPts2
        mesh_nearby = findMeshesNearby(clean_extended_pts)
        expandedPts3, usedVectors3 = expandPtsList(pt_origin, clean_extended_pts, {}, STEP_DEGREES/2.5, all_geom, mesh_nearby)
        
        ### expand number of pts around filtered rays 
        expandedPts4 = []
        clean_extended_pts = clean_extended_pts + expandedPts3
        mesh_nearby = findMeshesNearby(clean_extended_pts)
        expandedPts4, usedVectors4 = expandPtsList(pt_origin, clean_extended_pts, {}, STEP_DEGREES/5, all_geom, mesh_nearby)

        sortedPts = sortPtsByMesh(cleanPts + expandedPts2 + expandedPts3 + expandedPts4)
        visible_areas = []

        points = []
        colors = []
        distances = []

        for ptList in sortedPts:
            flat_list = []
            for p in ptList:
                points.extend([p.x, p.y, p.z])
                distances.append(p.distance)

        for d in distances:
            fraction = math.pow( (max(distances)-d)/max(distances), 0.4 )
            # https://matplotlib.org/stable/tutorials/colors/colormaps.html
            cmap = mpl.colormaps['jet']
            mapColor = cmap(fraction)
            r = int(mapColor[0]*255) # int(poly.count / maxCount)*255
            g = int(mapColor[1]*255) # int(poly.count / maxCount)*255
            b = int(mapColor[2]*255) # 255 - int( poly.count / maxCount)*255

            color = (255<<24) + (r<<16) + (g<<8) + b # argb
            colors.append(color)
        if len(points)==0 or len(colors)==0: return             
        cloud = [ Pointcloud(points = points, colors = colors )]

        print(len(vectors))
        print(len(cleanPts))

        visibility = (len(vectors) - len(cleanPts))/len(vectors) * 100
        print(f"Visible sky: {visibility}%")
    
    if onlyIllustrate is True:
        visibleObj = Collection(elements = lines, units = "m", name = "Context", collectionType = "VisibilityAnalysis")
    else:
        visibleObj = Collection(elements = cloud, units = "m", name = "Context", collectionType = "VisibilityAnalysis")
    
    # create branch if needed 
    existing_branch = client.branch.get(project_id, RESULT_BRANCH, 1)  
    if existing_branch is None: 
        br_id = client.branch.create(stream_id = project_id, name = RESULT_BRANCH, description = "") 

    objId = send(visibleObj, transports=[server_transport]) 
    commit_id = client.commit.create(
                stream_id=project_id,
                object_id=objId,
                branch_name=RESULT_BRANCH,
                message="Automate Pointcloud",
                source_application="Python",
            )

run(client, server_transport) 
