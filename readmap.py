import json
import numpy as np
import matplotlib.pyplot as plt

def read_json_map(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def plot_map(data):
    plt.figure(figsize=(212//4, 160 //4))
    
    for feature in data['features']:
        coords = np.array(feature['geometry']['coordinates'])
        feature_type = feature['properties']['type']

        if feature_type == 'coastline':
            plt.plot(coords[:, 0], coords[:, 1], color='black', linewidth=0.5)
        elif feature_type == 'country':
            plt.plot(coords[:, 0], coords[:, 1], color='gray', linewidth=0.3)
        elif feature_type == 'state':
            plt.plot(coords[:, 0], coords[:, 1], color='lightgray', linewidth=0.1)
        elif feature_type == 'river':
            plt.plot(coords[:, 0], coords[:, 1], color='blue', linewidth=0.1)

    plt.axis('equal')
    plt.axis('off')
    plt.title('World Map')
    plt.tight_layout()
    plt.savefig("world_map_topology")
    plt.show()


filename = 'world_map_topology.json'
map_data = read_json_map(filename)

plot_map(map_data)