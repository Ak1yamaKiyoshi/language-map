import json
from mpl_toolkits.basemap import Basemap
import numpy as np

def export_latlon_to_json(resolution='l'):
    # Use PlateCarree projection (equivalent to no projection) for lat/lon coordinates
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, 
                llcrnrlon=-180, urcrnrlon=180, resolution=resolution)
    
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
                # No need to convert coordinates, they are already in lat/lon
                valid_coords = [(lon, lat) for lon, lat in coordinates
                                if -180 <= lon <= 180 and -90 <= lat <= 90]
                
                if len(valid_coords) > 1:  # Ensure we still have a valid line after filtering
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": valid_coords
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

map_data = export_latlon_to_json()

with open('world_map_latlon.json', 'w') as f:
    json.dump(map_data, f)

print("Latitude/Longitude map data exported to 'world_map_latlon.json'")