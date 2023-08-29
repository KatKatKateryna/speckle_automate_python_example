

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
from typing import List
from specklepy.transports.server import ServerTransport
from specklepy.api.credentials import get_local_accounts
from specklepy.api.operations import receive, send
from specklepy.api.client import SpeckleClient
from specklepy.objects import Base
from specklepy.objects.other import Collection
from specklepy.api.models import Branch 

from flatten import flatten_base
#from utils.utils_network import calculateAccessibility
from utils.utils_osm import getBuildings, getRoads
from utils.utils_other import RESULT_BRANCH

server_url = "https://speckle.xyz/" # project_data.speckle_server_url
project_id = "17b0b76d13" #project_data.project_id
model_id = "revit tests"
version_id = "5d720c0998" #project_data.version_id
RADIUS = 300 #float(project_data.radius) 

#model_id = #project_data.model_id

account = get_local_accounts()[2]
client = SpeckleClient(server_url)
client.authenticate_with_token(account.token)
branch: Branch = client.branch.get(project_id, model_id, 1)

commit = branch.commits.items[0] 
server_transport = ServerTransport(project_id, client)

r'''
# to delete:
commit = client.commit.get(project_id, version_id)
#################################

base = receive(commit.referencedObject, server_transport)

objects = [b for b in flatten_base(base)]
print(objects)
'''

try:

    import numpy as np 
    #projInfo = base["info"] #[o for o in objects if o.speckle_type.endswith("Revit.ProjectInfo")][0] 
    #angle_rad = projInfo["locations"][0]["trueNorth"]
    #angle_deg = np.rad2deg(angle_rad)
    #lon = np.rad2deg(projInfo["longitude"])
    #lat = np.rad2deg(projInfo["latitude"])

    lat = 42.35866165161133
    lon = -71.0567398071289

    #print(angle_rad)
    #print(lon)
    #print(lat)

    crsObj = None
    commitObj = Collection(elements = [], units = "m", name = "Context", collectionType = "BuildingsLayer")

    blds = getBuildings(lat, lon, RADIUS)
    bases = [Base(units = "m", displayValue = [b]) for b in blds]
    bldObj = Collection(elements = bases, units = "m", name = "Context", collectionType = "BuildingsLayer")
        
    roads, meshes, analysisMeshes = getRoads(lat, lon, RADIUS)
    roadObj = Collection(elements = roads, units = "m", name = "Context", collectionType = "RoadsLayer")
    roadMeshObj = Collection(elements = meshes, units = "m", name = "Context", collectionType = "RoadMeshesLayer")
    analysisObj = Collection(elements = analysisMeshes, units = "m", name = "Context", collectionType = "RoadAnalysisLayer")
        
    # create branch if needed 
    existing_branch = client.branch.get(project_id, RESULT_BRANCH, 1)  
    if existing_branch is None: 
        br_id = client.branch.create(stream_id = project_id, name = RESULT_BRANCH, description = "") 

    commitObj.elements.append(bldObj)
    commitObj.elements.append(roadObj)
    commitObj.elements.append(roadMeshObj)

    objId = send(commitObj, transports=[server_transport]) 
    commit_id = client.commit.create(
                stream_id=project_id,
                object_id=objId,
                branch_name=RESULT_BRANCH,
                message="Context from Automate",
                source_application="Python",
            )
    
    commitObj.elements = []
    commitObj.elements.append(bldObj)
    commitObj.elements.append(analysisObj)

    objId = send(commitObj, transports=[server_transport]) 
    commit_id = client.commit.create(
                stream_id=project_id,
                object_id=objId,
                branch_name=RESULT_BRANCH,
                message="Space Syntax from Automate",
                source_application="Python",
            )
            
except Exception as e: 
    raise e 

