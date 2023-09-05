
import math
from typing import List
from specklepy.api.operations import receive, send
from specklepy.objects.geometry import Line, Point, Pointcloud 
from specklepy.objects.other import Collection

import numpy as np 
from operator import add, sub 
import matplotlib as mpl

from utils.utils_other import RESULT_BRANCH

HALF_VIEW_DEGREES = 70
STEP_DEGREES = 5

def run(client, server_transport, keyword):
    return