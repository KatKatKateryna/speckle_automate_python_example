

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

from flatten import flatten_base
from utils.convex_shape import concave_hull_create, remapPt
from utils.getComment import get_comments
#from utils.utils_network import calculateAccessibility
from utils.utils_osm import getBuildings, getRoads
from utils.utils_other import RESULT_BRANCH, cleanPtsList, sortPtsByMesh
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

server_url = "https://speckle.xyz/" # project_data.speckle_server_url
project_id = "17b0b76d13" #project_data.project_id
model_id = "revit tests"
version_id = "5d720c0998" #project_data.version_id
RADIUS = 50 #float(project_data.radius) 
KEYWORD = "rays"
HALF_VIEW_DEGREES = 30
STEP_DEGREES = 5
onlyIllustrate = False 
#model_id = #project_data.model_id

account = get_local_accounts()[2]
client = SpeckleClient(server_url)
client.authenticate_with_token(account.token)
branch: Branch = client.branch.get(project_id, model_id, 1)

commit = branch.commits.items[0] 
server_transport = ServerTransport(project_id, client)


pt_origin = [0, 0, 50]
dir = [1,-1,-0.5]

comments = get_comments(
    client,
    project_id,
)
#print(comments)
for item in comments["comments"]["items"]:
    if KEYWORD.lower() in item["rawText"].lower():
        viewerState = item["viewerState"]
        pt_origin: List[float] = viewerState["ui"]["selection"]

        pos: List[float] = viewerState["ui"]["camera"]["position"]
        target: List[float] = viewerState["ui"]["camera"]["target"]
        dir = list( map(sub, pos, target) )
        break 
#exit()
r'''
# to delete:
commit = client.commit.get(project_id, version_id)
#################################

base = receive(commit.referencedObject, server_transport)

objects = [b for b in flatten_base(base)]
print(objects)
'''


def run():
    #projInfo = base["info"] #[o for o in objects if o.speckle_type.endswith("Revit.ProjectInfo")][0] 
    #angle_rad = projInfo["locations"][0]["trueNorth"]
    #angle_deg = np.rad2deg(angle_rad)
    #lon = np.rad2deg(projInfo["longitude"])
    #lat = np.rad2deg(projInfo["latitude"])

    lat = 42.35866165161133
    lon = -71.0567398071289

    crsObj = None
    commitObj = Collection(elements = [], units = "m", name = "Context", collectionType = "VilibilityLayer")
    blds = getBuildings(lat, lon, RADIUS)
    bases = [Base(units = "m", displayValue = [b]) for b in blds]
    bldObj = Collection(elements = bases, units = "m", name = "Context", collectionType = "BuildingsLayer")

    lines = []
    cloud = []
    dir = [ int(i*1) for i in dir]
    start = Point.from_list(pt_origin)
    vectors = rotate_vector(pt_origin, dir, HALF_VIEW_DEGREES, STEP_DEGREES)

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
        for bld in blds:
            # get all intersection points 
            meshes = getAllPlanes(bld)
            for mesh in meshes:
                all_geom.append(mesh)
                pts, usedVectors = projectToPolygon(pt_origin, vectors, usedVectors, mesh, count) #Mesh.create(vertices = [0,0,0,5,0,0,5,19,0,0,14,0], faces=[4,0,1,2,3]))
                all_pts.extend(pts)
                count +=1

        cleanPts = cleanPtsList(pt_origin, all_pts, usedVectors)

        ### expand number of pts around filtere rays 
        cleanPts2 = []
        expandedPts2, usedVectors2 = expandPtsList(pt_origin, cleanPts, {}, STEP_DEGREES, all_geom)
        cleanPts2 = cleanPtsList(pt_origin, expandedPts2, usedVectors2)
        ### expand number of pts around filtere rays 
        cleanPts3 = []
        #clean_extended_pts = cleanPts + cleanPts2
        #expandedPts3, usedVectors3 = expandPtsList(pt_origin, clean_extended_pts, {}, int(STEP_DEGREES/2.5), all_geom)
        #cleanPts3 = cleanPtsList(pt_origin, expandedPts3, usedVectors3)

        for pt in cleanPts:
            end = pt #Point.from_list(list(pt))
            line = Line(start = start, end = end)
            line.units = "m"
            lines.append(line)
        
        sortedPts = sortPtsByMesh(cleanPts + cleanPts2 + cleanPts3)
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
            map = cmap(fraction)
            r = int(map[0]*255) # int(poly.count / maxCount)*255
            g = int(map[1]*255) # int(poly.count / maxCount)*255
            b = int(map[2]*255) # 255 - int( poly.count / maxCount)*255

            color = (255<<24) + (r<<16) + (g<<8) + b # argb
            colors.append(color)
                    
        cloud = [ Pointcloud(points = points, colors = colors )]

        print(len(vectors))
        print(len(lines))

        visibility = (len(vectors) - len(lines))/len(vectors) * 100
        print(f"Visible sky: {visibility}%")
    
    visibleLines = Collection(elements = lines, units = "m", name = "Context", collectionType = "VisibilityAnalysis")
    visibleObj = Collection(elements = cloud, units = "m", name = "Context", collectionType = "VisibilityAnalysis")

    # create branch if needed 
    existing_branch = client.branch.get(project_id, RESULT_BRANCH, 1)  
    if existing_branch is None: 
        br_id = client.branch.create(stream_id = project_id, name = RESULT_BRANCH, description = "") 

    #commitObj.elements.append(bldObj)
    if onlyIllustrate is True: commitObj.elements.append(visibleLines)
    else: commitObj.elements.append(visibleObj)

    objId = send(commitObj, transports=[server_transport]) 
    commit_id = client.commit.create(
                stream_id=project_id,
                object_id=objId,
                branch_name=RESULT_BRANCH,
                message="Automate",
                source_application="Python",
            )
    
run() 
