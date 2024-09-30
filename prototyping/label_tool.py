import cv2 as cv
import numpy as np

points = []
mouse_pos = 0, 0
image_scaling_factor = 1
mappng = "world_map_topology.png"

img = cv.imread(mappng)
shape = (np.array(img.shape)/image_scaling_factor).astype(int)
img = cv.resize(img, tuple(shape.tolist()[:2][::-1]))
print(img.shape)


def capture_movement(event, x, y, flags, param):
    global mouse_pos
    mouse_pos = x, y

cv.namedWindow("labeltool", cv.WINDOW_GUI_NORMAL)
cv.setMouseCallback("labeltool", capture_movement)


while True:
    img_copy = img.copy()
    
    key = cv.waitKey(1) & 0xFF

    for point in points:
        cv.circle(img_copy, point, 3, (0, 0, 0), 2)
        cv.circle(img_copy, point, 3, (255, 150, 40), 1)
    
    if len(points) > 3:
        drawpts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv.polylines(img_copy, [drawpts], True, (0, 0, 0), 3)
        cv.polylines(img_copy, [drawpts], True, (100, 255, 100), 1)

    if key == ord('p'):
        points.append(mouse_pos)
        print(points)

    elif key == ord('x') and points:
        nearest = min(points, key=lambda dot: np.linalg.norm(np.array(dot) - np.array((mouse_pos))))
        points.remove(nearest)

    elif key == ord('m') and points: 
        nearest = min(points, key=lambda dot: np.linalg.norm(np.array(dot) - np.array((mouse_pos))))
        points[points.index(nearest)] = mouse_pos

    elif key == ord('s') and points: 
        savepts = np.array(points) * image_scaling_factor

        lang = input("lang: ")
        intensity = float(input("intensity: "))
        year = int(input("year: "))
        data = {"coords": savepts,"lang": lang, "year": year,"intensity": intensity}

        with open("world_map_topology.cool_file_format", "a+") as f:
            f.write(f"\n{data}")

    print(mouse_pos)    
    cv.imshow("labeltool", img_copy)
cv.destroyAllWindows()
