import json
from mpl_toolkits.basemap import Basemap
import numpy as np

def export_basemap_to_json(resolution='l', proj='robin'):
    m = Basemap(projection=proj, resolution=resolution, lat_0=0, lon_0=0)
    
    coastlines = m.drawcoastlines()
    countries = m.drawcountries()
    states = m.drawstates()
    rivers = m.drawrivers()
    
    data = {
        "type": "FeatureCollection",
        "features": []
    }
    
    def add_feature(geom, feature_type):
        for path in geom.get_paths():
            coordinates = path.vertices
            if len(coordinates) > 1:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates.tolist()
                    },
                    "properties": {
                        "type": feature_type
                    }
                }
                data["features"].append(feature)
    
    add_feature(coastlines, "coastline")
    add_feature(countries, "country")
    add_feature(states, "state")
    add_feature(rivers, "river")

    return data

map_data = export_basemap_to_json()

with open('world_map_topology.json', 'w') as f:
    json.dump(map_data, f)

print("Map data exported to 'world_map_topology.json'")