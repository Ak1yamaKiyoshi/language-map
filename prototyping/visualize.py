import cv2
import numpy as np
from drawlib import *
from collections import defaultdict

def calculate_center(points):
    return tuple(np.mean(points, axis=0).astype(int))

def create_single_color_gradient(shape, points, color, border_weight=0.5):
    gradient = combined_gradient(shape, points, border_weight)
    eased_gradient = cubic_ease(gradient)
    color_array = np.array(color, dtype=np.uint8)
    return (eased_gradient[..., np.newaxis] * color_array).astype(np.uint8)

def draw_dashed_lines(img, points, color, thickness=1, dash_length=10):
    points = np.array(points, dtype=np.int32)
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        dist = np.linalg.norm(end - start)
        num_dashes = max(int(dist / (2 * dash_length)), 1)
        
        for j in range(num_dashes):
            pt1 = start + (end - start) * (2 * j) / (2 * num_dashes)
            pt2 = start + (end - start) * (2 * j + 1) / (2 * num_dashes)
            cv2.line(img, tuple(pt1.astype(int)), tuple(pt2.astype(int)), color, thickness)

labelspath = "world_map_topology.cool_file_format"
imagepath = "world_map_topology.png"

with open(labelspath, "r") as f:
    labels = [eval(strlabel) for strlabel in f.read().split("\n")]

img = cv2.imread(imagepath)
shape = (np.array(img.shape[:2]) // 2).astype(int)
img = cv2.resize(img, (shape[1], shape[0]))

res = np.zeros((*shape, 3), dtype=np.uint8)

colors =[
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (255, 192, 203),  # Pink
    (128, 0, 128),    # Purple
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (128, 128, 128),  # Gray
    (0, 0, 0),        # Black
    (255, 255, 255),  # White
    (128, 255, 0),    # Lime Green
    (0, 128, 255),    # Sky Blue
    (75, 0, 130),     # Indigo
    (240, 128, 128),  # Light Coral
    (255, 218, 185),  # Peach Puff
    (0, 128, 0)       # Dark Green
]

lang_groups = defaultdict(list)
for label in labels:
    lang_groups[label['lang']].append(label)

for i, (lang, group) in enumerate(lang_groups.items()):
    color = colors[i % len(colors)]
    merged_mask = np.zeros(shape, dtype=np.uint8)
    all_points = []

    for label in group:
        points = (np.array(label['coords']) / 2).astype(int)
        all_points.extend(points)
        mask = create_mask(shape, points)
        merged_mask = cv2.bitwise_or(merged_mask, mask)

        draw_dashed_lines(res, points, color, thickness=1, dash_length=5)

    gradient_img = create_single_color_gradient(shape, all_points, color, border_weight=1.0)

    res += cv2.bitwise_and(gradient_img, gradient_img, mask=merged_mask)

    center_point = calculate_center(all_points)
    text_color = (255, 255, 255)  # White text
    cv2.putText(res, lang, (center_point[0] + 10, center_point[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)

    print(f"Drawn {lang}")

cv2.imwrite("world_map_visualization.jpeg", res)

cv2.imshow("World Map Visualization", res)
cv2.waitKey(0)
cv2.destroyAllWindows()