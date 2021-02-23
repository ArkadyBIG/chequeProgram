import sys
import json
from pprint import pprint

from parser import parse
import cv2


path_to_image, path_to_json = sys.argv[1:3]
# path_to_image, path_to_json = '../ch_photos/40.jpg', '../ch_photos/40.json'
image = cv2.imread(path_to_image, 0)
if image is None:
    raise FileNotFoundError
with open(path_to_json, 'rb') as file:
    data = json.load(file)['corners']
    points = {i['type']: (i['x'], i['y']) for i in data}
    info = parse(image, [points['tl'], points['tr'], points['bl'], points['br']],
                 need_sort=False)
    pprint(info)

