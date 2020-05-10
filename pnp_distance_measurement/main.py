import json, cv2
import numpy as np
from matplotlib import pyplot as plt
from quadrilateral import Point, Quadrilateral

# JSON_INPUT = 'json/quadrilateral-raw-1807.json'
# JSON_OUTPUT = 'json/quadrilateral-results-1787.json'

JSON_INPUT = 'json/street-raw-4032x3024.json'
JSON_OUTPUT = 'json/street-results-4032x3024.json'

# JSON_INPUT = 'json/street-raw-1008x756.json'
# JSON_OUTPUT = 'json/street-results-1008x756.json'

class Processing(object):
  def create_quadrilateral_arr(self, data):
    """
    Create an array of quadrilateral objects from the input data json object
    """
    quadrilateral_arr = []
    for i in range(len(data)):
      id = data[i]['External ID']
      url = data[i]['Labeled Data']
      try:
        # pts = data[i]['Label']['EXIT_sign'][0]['geometry']
        pts = data[i]['Label']['rectangle'][0]['geometry']
        p1 = Point(float(pts[0]['x']), float(pts[0]['y']))
        p2 = Point(float(pts[1]['x']), float(pts[1]['y']))
        p3 = Point(float(pts[2]['x']), float(pts[2]['y']))
        p4 = Point(float(pts[3]['x']), float(pts[3]['y']))
        pts = self.rearrange_pts(p1, p2, p3, p4)     # Rearrange the point in A B C D order
        quadrilateral_arr.append(Quadrilateral(id, url, pts))
      except:
        continue
    quadrilateral_arr.sort(key=lambda x : x.id, reverse = False)
    return quadrilateral_arr

  def rearrange_pts(self, p1, p2, p3, p4):
    """
    From 4 corner points, put them in A B C D order of a quadrilateral
    """
    arr = [p1, p2, p3, p4]
    arr.sort(key=lambda p: (p.x, p.y))
    # A and D will have smaller x, B and C will have larger x
    (A, D) = (arr[0], arr[1]) if arr[0].y < arr[1].y else (arr[1], arr[0])
    (B, C) = (arr[2], arr[3]) if arr[2].y < arr[3].y else (arr[3], arr[2])
    return (A, B, C, D)

  def find_ave_proj_error(self, quadrilateral_arr):
    """
    Calulate the average pixel differences in x and y directions between
    the labels and the projected images
    """
    err_x, err_y = 0, 0
    for quadrilateral in quadrilateral_arr:
      err_x += quadrilateral.x_err
      err_y += quadrilateral.y_err
    return (err_x/len(quadrilateral_arr), err_y/len(quadrilateral_arr))

  def analyze_distance_stats(self, quadrilateral_arr, distance_arr):
    """
    Find the image with maximum / minimum distance among the dataset for analysis
    """
    min_distance, max_distance = min(distance_arr), max(distance_arr)
    for obj in quadrilateral_arr:
      if obj.distance == min_distance:
        print('Min distance: ' + str(obj.distance))
        print(obj.id)
        print(obj.url)
        print('-----------------------------------')
      if obj.distance == max_distance:
        print('Max distance: ' + str(obj.distance))
        print('Image name: ' + obj.id)
        print('URL: ' + obj.url)

  def plot_histogram(self, arr):
    plt.hist(arr, rwidth=0.8, bins=50) 
    plt.xlabel('Distance (in meter)')
    plt.title('Histogram of distances')
    plt.show()

  def print_an_example(self, quadrilateral):
    """
    Printing the processing results for quadrilateral index i
    """
    print("2D coordinates of the testing point: ")
    print(quadrilateral.vertices_2D)

    print("2D projected coordinates of the testing point: ")
    print(quadrilateral.projected_vertices_2D)

    print("x-axis projection error: " + str(quadrilateral.x_err) + ' pixel')
    print("y-axis projection error: " + str(quadrilateral.y_err) + ' pixel')

    print('R_vec: '); 
    print(quadrilateral.R_vec)

    print('T_vec: '); 
    print(quadrilateral.T_vec)

    print('Calculated distance from T_vector: '); 
    print(str(quadrilateral.distance) + ' (meters)')

  def write_to_json(self, arr, json_file_name):
    """
    Write the quadrilateral array to a json output file
    """
    with open(json_file_name, "w") as outfile: 
      json_obj = json.dumps(arr, default=lambda x: x.__dict__, indent=4, sort_keys=True)
      outfile.write(json_obj)

def main():
  with open(JSON_INPUT) as f:
    data = json.load(f)
  P = Processing()
  quadrilateral_arr = P.create_quadrilateral_arr(data)
  P.write_to_json(quadrilateral_arr, JSON_OUTPUT)

  print('***********************************************************************')
  ave_x_err, ave_y_err = P.find_ave_proj_error(quadrilateral_arr)
  print('Average x-axis projection error: ' + str(ave_x_err))
  print('Average y-axis projection error: ' + str(ave_y_err))

  print('***********************************************************************')
  distance_arr = [obj.distance for obj in quadrilateral_arr]
  P.analyze_distance_stats(quadrilateral_arr, distance_arr)
  # P.plot_histogram(distance_arr)

  # print('***********************************************************************')
  # P.print_an_example(quadrilateral_arr[1])

  print('***********************************************************************')
  for quadrilateral in quadrilateral_arr:
    print(quadrilateral.id + ' ' + str(quadrilateral.distance))
  print('***********************************************************************')

if __name__== "__main__":
  main()