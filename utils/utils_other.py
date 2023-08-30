
from copy import copy
from typing import List
import math

import numpy as np
from specklepy.objects.geometry import Mesh, Point, Line 

RESULT_BRANCH = "automate"
COLOR_ROAD = (255<<24) + (50<<16) + (50<<8) + 50 # argb
COLOR_BLD = (255<<24) + (200<<16) + (200<<8) + 200 # argb
COLOR_VISIBILITY = (255<<24) + (255<<16) + (10<<8) + 10 # argb

def sortPtsByMesh(cleanPts: List[Point]) -> List[List[tuple]]:
    ptsGroups: List[List[np.array]] = []
    
    usedMeshIds = []
    for pt in cleanPts:
        if pt.meshId in usedMeshIds: continue

        meshId = pt.meshId
        morePts: [List[tuple]] = [ ( p.x, p.y, p.z ) for p in cleanPts if p.meshId == meshId]
        ptsGroups.append(morePts)
        usedMeshIds.append(meshId)

    return ptsGroups

def cleanPtsList(pt_origin, all_pts, usedVectors):
    
    cleanPts = []
    checkedPtIds = []
    p1 = np.array(pt_origin)
    
    for i, pt in enumerate(all_pts):
        if i in checkedPtIds: continue
        
        vectorId = pt.vectorId
        meshId = pt.meshId
        vectorCount = usedVectors[pt.vectorId]
        if vectorCount>1:
            pack = [ [np.array([p.x, p.y, p.z]),x,p.meshId]  for x,p in enumerate(all_pts) if p.vectorId == vectorId]
            competingPts = [ x[0] for x in pack]
            competingPtIds = [ x[1] for x in pack]
            competingPtMeshIds = [ x[2] for x in pack]

            distance = None
            finalPt = pt
            for x, p2 in enumerate(competingPts):
                
                squared_dist = np.sum((p1-p2)**2, axis=0)
                dist = np.sqrt(squared_dist)
                if (distance is None) or (dist < distance and dist>0): 
                    distance=dist
                    finalPt = Point.from_list([p2[0], p2[1], p2[2]])
                    finalPt.meshId = competingPtMeshIds[x]
                    finalPt.vectorId = vectorId
            if distance is not None:
                cleanPts.append(finalPt)
                checkedPtIds.extend(competingPtIds)
        else:
            cleanPts.append(pt)
    return cleanPts

def cleanString(text: str) -> str:
    symbols = r"/[^\d.-]/g, ''"
    new_text = text
    for s in symbols:
        new_text = new_text.split(s)[0]#.replace(s, "")
    return new_text

def fillList(vals: list, lsts: list) -> List[list]:
    if len(vals)>1: 
        lsts.append([])
    else: return

    for i, v in enumerate(vals):
        if v not in lsts[len(lsts)-1]: lsts[len(lsts)-1].append(v)
        else: 
            if len(lsts[len(lsts)-1])<=1: lsts.pop(len(lsts)-1)
            vals = copy(vals[i-1:])
            fillList(vals, lsts)
    return lsts 
    