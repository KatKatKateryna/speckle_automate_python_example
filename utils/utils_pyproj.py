

from pyproj import CRS
from pyproj import Transformer

def createCRS(lat: float, lon: float):

    newCrsString = "+proj=tmerc +ellps=WGS84 +datum=WGS84 +units=m +no_defs +lon_0=" + str(lon) + " lat_0=" + str(lat) + " +x_0=0 +y_0=0 +k_0=1"
    crs2 = CRS.from_string(newCrsString)
    return crs2

def reprojectToCrs(lat: float, lon: float, crs_from, crs_to, direction = "FORWARD"):

    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
    pt = transformer.transform(lon, lat, direction=direction)

    return pt[0], pt[1] 
