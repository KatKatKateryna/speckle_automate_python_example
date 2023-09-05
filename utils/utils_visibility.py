
import math
import random
from typing import List
#from scipy.linalg import expm, norm

import numpy as np
from numpy import cross, eye, dot
from operator import add, sub
from specklepy.objects.geometry import Mesh, Point

from utils.convex_shape import remapPt
from utils.vectors import createPlane, normalize 