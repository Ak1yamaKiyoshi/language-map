import json
import numpy as np
from lib_maputils import MapUtils

import math





def read_json_map(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def plot_map(data):
    all_coords = []
    for feature in data['features']:
      coords = feature['geometry']['coordinates']
      feature_type = feature['properties']['type']
      all_coords += coords

    min_latlon = np.min(all_coords, axis=0)
    max_latlon = np.max(all_coords, axis=0)
    min_mercator = MapUtils.latlon_to_mercator(*min_latlon[::-1])
    max_mercator = MapUtils.latlon_to_mercator(*max_latlon[::-1])
    
    print(min_mercator, max_mercator)
    


filename = 'world_map_latlon.json'
map_data = read_json_map(filename)

plot_map(map_data)