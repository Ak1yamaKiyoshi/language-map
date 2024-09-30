import numpy as np 
import cv2

import scipy.interpolate as spi

expansionxy = 100



def random_polygon(num_corners, center_x=150, center_y=150, min_radius=5, max_radius=150):
    angles = np.linspace(0, 2*np.pi, num_corners, endpoint=False)
    radii = np.random.uniform(min_radius, max_radius, num_corners)
    
    x = center_x + radii * np.cos(angles)
    y = center_y + radii * np.sin(angles)
    
    return np.column_stack([x, y]).astype(int)


def interpolate_points(p1, p2, num_interpolations):
    interpolated_points = []
    for t in np.linspace(0, 1, num_interpolations, endpoint=False):
        interp_point = (1 - t) * p1 + t * p2
        interpolated_points.append(interp_point)
    return interpolated_points


def spline_interpolate(points, num_interpolations=100):
    """Interpolate a smooth spline through the given points."""
    points = np.vstack([points, points[0]])
    
    t = np.arange(len(points))
    tck_x = spi.splrep(t, points[:, 0], s=0)  # Fit spline for x
    tck_y = spi.splrep(t, points[:, 1], s=0)  # Fit spline for y
    t_new = np.linspace(0, len(points) - 1, num_interpolations)
    x_spline = spi.splev(t_new, tck_x)
    y_spline = spi.splev(t_new, tck_y)
    
    return np.column_stack([x_spline, y_spline])

def random_oval(num_corners, center_x=150, center_y=150, min_radius_x=50, max_radius_x=150, min_radius_y=30, max_radius_y=100, distortion_factor=0.2, num_interpolations=100):
    angles = np.linspace(0, 2 * np.pi, num_corners, endpoint=False)
    
    radii_x = np.random.uniform(min_radius_x, max_radius_x, num_corners)
    radii_y = np.random.uniform(min_radius_y, max_radius_y, num_corners)
    
    distortion_x = np.random.uniform(-distortion_factor, distortion_factor, num_corners) * radii_x
    distortion_y = np.random.uniform(-distortion_factor, distortion_factor, num_corners) * radii_y
    
    x = center_x + (radii_x + distortion_x) * np.cos(angles)
    y = center_y + (radii_y + distortion_y) * np.sin(angles)
    
    points = np.column_stack([x, y]).astype(float)
    
    smooth_points = spline_interpolate(points, num_interpolations)
    return smooth_points 

def draw_points(img, points, color=255, thickness=1, ):
    prev_pt = points[-1]
    for pt in points:
        cv2.line(img, tuple(prev_pt), tuple(pt), color,  thickness)
        prev_pt = pt
    return img

def block_outer(img, points): 
    mask = np.zeros(img.shape[:2], dtype=np.uint8) 
    mask = cv2.drawContours(mask, [points], -1, 1, -1)
    result = cv2.bitwise_and(img, img, mask=mask)
    return result


def cubic_ease(t):
    return t ** 3

def apply_cubic_ease(base_colors):
    positions = np.linspace(0, 1, len(base_colors))
    eased_colors = [cubic_ease(pos) for pos in positions]
    min_color, max_color = min(base_colors), max(base_colors)
    scaled_colors = [min_color + (max_color - min_color) * eased for eased in eased_colors]
    return scaled_colors

def gradient(img, points, steps=110):
    thikness = range(steps, 1, -1)
    color =    (np.array(list(range(steps, 1, -1)))/steps)

    color = apply_cubic_ease(color)

    for th, cl in zip(thikness, color):
        img = draw_points(img, points, color= cl, thickness=th )
    img = block_outer(img, points)
    return img

def gradient_reverse(img, points, amplifier=0.7):
    normalized_points = points.copy() / np.max(points, axis=0)
    steps = int(np.max(points)*amplifier)
    thikness = range(1, int(steps))[::-1]
    color =    (np.array(list(range(steps, 1, -1)))/steps)
    for th, cl in zip(thikness, color):
        img = draw_points(img, points, color= cl, thickness=th )
        img = block_outer(img, points)
    return img

def border(img, points, thikness=5, color=255):
    img = draw_points(img, points, color= color, thickness=thikness )
    return img



def create_mask(shape, points):
    mask = np.zeros(shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], 1)
    return mask

def gradient_from_border(shape, points, max_distance=None):
    mask = create_mask(shape, points)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    if max_distance is None:
        max_distance = np.max(dist)
    return np.clip(dist / max_distance, 0, 1)

def gradient_from_center(shape, points):
    mask = create_mask(shape, points)
    center = np.mean(points, axis=0).astype(int)
    y, x = np.ogrid[:shape[0], :shape[1]]
    dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    max_distance = np.max(dist * mask)
    return (1 - np.clip(dist / max_distance, 0, 1)) * mask

def apply_gradient(img, gradient, color_func):
    colored_gradient = color_func(gradient)
    return (img * colored_gradient).astype(np.uint8)

def combined_gradient(shape, points, border_weight=0.5):
    border_grad = gradient_from_border(shape, points)
    center_grad = gradient_from_center(shape, points)
    return border_weight * border_grad + (1 - border_weight) * center_grad

def cubic_ease(t):
    return t ** 3

def create_gradient_image(shape, points, color_func, border_weight=0.5):
    gradient = combined_gradient(shape, points, border_weight)
    eased_gradient = cubic_ease(gradient)
    return apply_gradient(np.ones(shape, dtype=np.uint8) * 255, eased_gradient, color_func)

def grayscale_color(t):
    return np.expand_dims(t * 255, axis=2)

def rgb_color(t):
    return np.stack([t * 255, t * 128, t * 64], axis=2)


if __name__ == "__main__":
    points =random_oval(35, center_x=150, center_y=150, min_radius_x=50, max_radius_x=150, min_radius_y=30, max_radius_y=150, num_interpolations=10).astype(int)

    frames = 0
    while True:
        try:
            
            frames += 1
            img = np.zeros((np.max(points)+expansionxy, np.max(points)+expansionxy))

            img_grad = gradient(img, points, steps=40)
            img_revgrad = gradient_reverse(img, points, )
            img = cv2.addWeighted(img_grad, 0.5, img_revgrad, 0.5, 0)
            img = cv2.GaussianBlur(img, (23, 23), 0)
            img = border(img, points, thikness=3)

            random_movement = np.random.randint(-1, 2, size=points.shape) * 10
            points += random_movement

            cv2.imshow("1", img.astype(np.float32))
            cv2.waitKey(1)
            print(f"\r frames: {frames}", end="", flush=True)

        except KeyboardInterrupt:
            break

    cv2.destroyAllWindows()

