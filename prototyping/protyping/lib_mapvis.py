import numpy as np 
import cv2 as cv
import cv2


class MapVis: 
  @staticmethod
  def create_polygon_mask(width, height, vertices):
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(vertices, dtype=np.int32)], 255)
    return mask

  @staticmethod
  def create_hatched_pattern(base_img, spacing=10, angle=45, color=(255, 255, 255), thickness=1, alpha=0.5, mask=None):
    height, width = base_img.shape[:2]
    overlay = np.zeros_like(base_img)
    num_lines = int(np.ceil(np.sqrt(width**2 + height**2) / spacing))
    center_x, center_y = width // 2, height // 2
    M = cv2.getRotationMatrix2D((center_x, center_y), angle, 1)
    for i in range(-num_lines, num_lines):
      start_point = (0, i * spacing + center_y)
      end_point = (width, i * spacing + center_y)
      start_rotated = np.dot(M, [start_point[0], start_point[1], 1]).astype(int)
      end_rotated = np.dot(M, [end_point[0], end_point[1], 1]).astype(int)        
      cv2.line(overlay, tuple(start_rotated), tuple(end_rotated), color, max(1, thickness))

    if mask is not None:
      overlay = cv2.bitwise_and(overlay, overlay, mask=mask)
    result = cv2.addWeighted(base_img, 1, overlay, alpha, 0)
    return result



  @staticmethod
  def draw_hatched_pattern(base_img, spacing=10, angle=45, color=(255, 255, 255), thickness=1, mask=None):
      height, width = base_img.shape[:2]
      overlay = np.zeros_like(base_img)

      num_lines = int(np.ceil(np.sqrt(width**2 + height**2) / spacing))
      center_x, center_y = width // 2, height // 2
      M = cv.getRotationMatrix2D((center_x, center_y), angle, 1)

      for i in range(-num_lines, num_lines):
          start_point = (0, i * spacing + center_y)
          end_point = (width, i * spacing + center_y)
          start_rotated = np.dot(M, [start_point[0], start_point[1], 1]).astype(int)
          end_rotated = np.dot(M, [end_point[0], end_point[1], 1]).astype(int)
          cv.line(overlay, tuple(start_rotated), tuple(end_rotated), color, max(1, thickness))

      if mask is not None:
          if len(mask.shape) == 3:
              mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
          overlay_masked = cv.bitwise_and(overlay, overlay, mask=mask)
          result = cv.bitwise_or(base_img, overlay_masked)
      else:
          result = base_img 

      return result