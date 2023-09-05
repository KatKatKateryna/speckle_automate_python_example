
import math
from typing import List
from specklepy.api.operations import receive, send
from specklepy.objects.geometry import Line, Point, Pointcloud 
from specklepy.objects.other import Collection

import numpy as np 
from operator import add, sub 
import matplotlib as mpl

from flatten import iterateBase
from utils.getComment import get_comments

from utils.utils_other import RESULT_BRANCH, cleanPtsList, findMeshesNearby, sortPtsByMesh
from utils.utils_visibility import getAllPlanes, projectToPolygon, rotate_vector, expandPtsList

HALF_VIEW_DEGREES = 70
STEP_DEGREES = 5

def run(client, server_transport, keyword):
    return