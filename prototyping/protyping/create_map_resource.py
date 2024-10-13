from lib_maputils import MapUtils
from lib_mapvis import MapVis
import json
import numpy as np
import cv2 as cv
from tqdm import tqdm

import time


def lerp(v, from_min, from_max, to_min, to_max):
    return (v - from_min) / (from_max - from_min) * (to_max - to_min) + to_min


min_mercator = np.array((-20037508.34, -20037508.34))
max_mercator = np.array((20037508.34, 20037508.34))


def init_map_img(width, height):
    def read_json_map(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        return data

    def read_map(data, out):
        for feature in data["features"]:
            coords = feature["geometry"]["coordinates"]
            out.append(coords)

    filename = "world_map_latlon.json"

    map_data = read_json_map(filename)
    out = []
    read_map(map_data, out)
    mercator_all = []
    for polygon in out:
        mercator_all += polygon

    min_mercator = np.array((-20037508.34, -20037508.34))
    max_mercator = np.array((20037508.34, 20037508.34))

    img = np.ones((width, height, 3), dtype=np.uint8) * 220

    for feature in tqdm(map_data["features"]):
        coords = feature["geometry"]["coordinates"]
        coords = np.array(coords)
        feature_type = feature["properties"]["type"]

        mercator = []
        for latlon in coords:
            mercator.append(MapUtils.latlon_to_mercator(*latlon[::-1]))
        mercator = np.array(mercator)

        mercator2pixel = (
            lerp(mercator, min_mercator, max_mercator, 0, height)
            .reshape((-1, 1, 2))
            .astype(np.int32)
        )
        if feature_type == "state":
            img = cv.polylines(img, [mercator2pixel], False, (50, 50, 50), 2)
        elif feature_type == "country":
            img = cv.polylines(img, [mercator2pixel], False, (0, 150, 150), 2)
        elif feature_type == "river":
            img = cv.polylines(img, [mercator2pixel], False, (120, 30, 30), 1)
        elif feature_type == "coastline":
            img = cv.polylines(img, [mercator2pixel], False, (0, 0, 0), 2)
    return img

import os
#os.mkdir("map_resource")
res = 2**12
while res < 2**16:
    img = init_map_img(res, res)
    cv.imwrite(f"map_resource/{res:05d}x{res:05d}.png",img)

    print(res)
    res*= 2