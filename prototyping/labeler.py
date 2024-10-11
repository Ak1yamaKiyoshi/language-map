from lib_maputils import MapUtils
from lib_mapvis import MapVis

import json, time, os
import numpy as np
import cv2 as cv


from tqdm import tqdm


def capture_movement(event, x, y, flags, param):
    global mouse_pos
    mouse_pos = np.array([x, y], dtype=int)


def get_map():
    global resolution, maps, VIEWPORT_SIZE
    image = maps[resolution].copy() #  cv.imread(map_imagepaths[resolution])
    original_height, original_width = image.shape[:2]

    aspect_ratio = original_width / original_height
    new_width = int(VIEWPORT_SIZE * aspect_ratio)

    return image#cv.resize(image, (VIEWPORT_SIZE, new_width)) 


def zoom_at(img, zoom=1, coord=None, angle=0, ):
    cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
    new_cx = cx 
    new_cy = cy 
    
    rot_mat = cv.getRotationMatrix2D((float(cx),float(cy)), angle, zoom)
    result = cv.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)
    return result, (new_cx, new_cy)


VIEWPORT_SIZE = (720)
ZOOM_RESIZE_STRENGHT = 1.2

maps_cache_path = 'maps-cache'
map_imagepaths = sorted([os.path.join(maps_cache_path, i) for i in os.listdir(maps_cache_path)])
maps = [cv.imread(i) for i in map_imagepaths[:-2]]

resolution = 0
zoom = 3.0
cx, cy = 0, 0

mouse_pos = np.array([0, 0], dtype=int)
map_image = get_map()

cv.namedWindow("labeltool", cv.WINDOW_GUI_NORMAL)
cv.setWindowProperty("labeltool", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
cv.setMouseCallback("labeltool", capture_movement)

orig = map_image.copy()

while True:

    original_height, original_width = map_image.shape[:2]

    aspect_ratio = original_width / original_height
    new_width = int(VIEWPORT_SIZE * aspect_ratio)

    viewimage =cv.resize(map_image, (VIEWPORT_SIZE, new_width)) 

    cv.imshow("labeltool", viewimage)
    key = cv.waitKey(1)
    if key != -1:
        key_char = chr(key)
        if key == ord("q"):
            break
        if key == ord("="):
            zoom *= ZOOM_RESIZE_STRENGHT
        if key == ord("-"):
            zoom /= ZOOM_RESIZE_STRENGHT

        if key == ord("h"):
            map_image, (cx, cy) = zoom_at(orig.copy(), zoom*2**resolution, mouse_pos + np.array([cx, cy]) )
        print(mouse_pos , np.array([cx, cy]) )


    # newimage = get_map()
    # size = np.array(newimage.shape[:2][::-1]) // zoom
    # print(mouse_pos, mouse_pos/size.shape[0]) # * newimage.shape[0])
    # map_image = crop_image(newimage, mouse_pos, size.astype(int))
    # time.sleep(0.1)