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

    # min_mercator = np.array((-20037508.34, -20037508.34))
    # max_mercator = np.array((20037508.34, 20037508.34))

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


def draw_text_with_background(
    img, text, mouse_pos, font=cv.FONT_HERSHEY_COMPLEX, font_scale=0.4, thickness=2
):
    (text_width, text_height), baseline = cv.getTextSize(
        text, font, font_scale, thickness
    )
    rect_top_left = (mouse_pos[0], mouse_pos[1] - text_height - baseline)
    rect_bottom_right = (mouse_pos[0] + text_width, mouse_pos[1] + baseline)

    cv.rectangle(
        img, rect_top_left, rect_bottom_right, (0, 0, 0), thickness=2
    )  # Border
    cv.rectangle(
        img, rect_top_left, rect_bottom_right, (255, 255, 255), cv.FILLED
    )  # Background
    cv.putText(img, text, mouse_pos, font, font_scale, (0, 0, 0), thickness)  # Text



img = init_map_img(5000, 5000)


points = []
mouse_pos = 0, 0
image_scaling_factor = 1

year = 2024
language = ""
intensity = 0.5


def capture_movement(event, x, y, flags, param):
    global mouse_pos
    mouse_pos = x, y


def year_slider_callback(val):
    global year
    year = val + 1924
    print(f"Year selected: {year}")


def intensity_slider_callback(val):
    global intensity
    intensity = val / 100.0
    print(f"Intensity selected: {intensity:.2f}")


def input_language(event, x, y, flags, param):
    global language
    if event == cv.EVENT_KEYDOWN:
        if flags == cv.EVENT_FLAG_LBUTTON:  # Only process when the mouse is clicked
            language = ""


cv.namedWindow("labeltool", cv.WINDOW_GUI_NORMAL)
cv.setWindowProperty("labeltool", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)

cv.setMouseCallback("labeltool", input_language)
cv.setMouseCallback("labeltool", capture_movement)
cv.createTrackbar(
    "Year", "labeltool", 100, 100, year_slider_callback
)  # 0-100 corresponds to 1924-2024
cv.createTrackbar(
    "Intensity", "labeltool", 50, 100, intensity_slider_callback
)  # 0-100 for intensity

# save


font_scale = 0.4
font = cv.FONT_HERSHEY_COMPLEX
thickness = 1

derrivative_image = img.copy()
latest_points = None

while True:
    img_copy = derrivative_image.copy()
    key = cv.waitKey(1) & 0xFF

    ckiyv_latlon = np.array((50.4504, 30.5245))
    ckiyv = np.array(MapUtils.latlon_to_mercator(*ckiyv_latlon))
    ckiyv = lerp(ckiyv, min_mercator, max_mercator, np.array([0, 0]),  np.min(img_copy.shape[:2])).astype(np.int32)
    cv.circle(img_copy, ckiyv.astype(np.int32), 15, (0, 0, 255), 5)
    cv.putText(img_copy, f"{ckiyv_latlon[0]} {ckiyv_latlon[1]}", ckiyv, cv.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)



    if len(points) > 3 and not np.array_equal(
        np.array(points), np.array(latest_points)
    ):
        latest_points = points.copy()
        drawpts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        mask = MapVis.create_polygon_mask(*img.shape[:2], drawpts.reshape(-1, 2))
        derrivative_image = MapVis.draw_hatched_pattern(
            img.copy(), 10, 49, (255, 255, 0), 3, mask
        )
        print("t", time.time())

    if len(points) > 3:
        drawpts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv.polylines(img_copy, [drawpts], True, (0, 0, 0), 3)
        cv.polylines(img_copy, [drawpts], True, (100, 255, 100), 1)

    for point in points:
        cv.circle(img_copy, point, 3, (0, 0, 0), 2)
        cv.circle(img_copy, point, 3, (255, 150, 40), 1)

    if key == ord("q"):
        break

    if key == ord("u"):
        newshape = (np.array(img.shape[:2]) / 1.2).astype(int)
        points = (np.array(points) / 1.2).astype(np.int32).tolist()
        img = init_map_img(*newshape)
        derrivative_image = img.copy()

    if key == ord("i"):
        newshape = (np.array(img.shape[:2]) * 1.2).astype(int)
        points = (np.array(points) * 1.2).astype(np.int32).tolist()

        img = init_map_img(*newshape)
        derrivative_image = img.copy()

    if key == ord("p"):
        points.append(mouse_pos)

    elif key == ord("x") and points:
        nearest = min(
            points,
            key=lambda dot: np.linalg.norm(np.array(dot) - np.array((mouse_pos))),
        )
        points.remove(nearest)

    elif key == ord("m") and points:
        nearest = min(
            points,
            key=lambda dot: np.linalg.norm(np.array(dot) - np.array((mouse_pos))),
        )
        points[points.index(nearest)] = mouse_pos

    elif key == ord("s") and points:
        savepts = np.array(points)
        # points to mercator
        # mercator to latlng
        # save

        lang = input("Enter language")
        data = {"coords": savepts, "lang": lang, "year": year, "intensity": intensity}
        with open("world_map_topology.cool_file_format", "a+") as f:
            f.write(f"\n{data}")


    #
      
    # mouse pos
    mercator = lerp(
        np.array(mouse_pos) ,
        np.array([0, 0]),
        np.array(img.shape[:2][::-1]),
        np.array(min_mercator),
        np.array(max_mercator),
    )
    latlon = MapUtils.web_mercator_to_latlon(*mercator)


    text = f"{latlon[0]:3.5f}, {latlon[1]:3.5f}"
    draw_text_with_background(
        img_copy, text, (mouse_pos[0] + 20, mouse_pos[1]), font, font_scale, thickness
    )
    draw_text_with_background(
        img_copy,
        f"year:{year}",
        (mouse_pos[0] + 20, mouse_pos[1] + 20),
        font,
        font_scale,
        thickness,
    )
    draw_text_with_background(
        img_copy,
        f"int:{intensity}",
        (mouse_pos[0] + 20, mouse_pos[1] + 40),
        font,
        font_scale,
        thickness,
    )

    cv.imshow("labeltool", img_copy)
cv.destroyAllWindows()
