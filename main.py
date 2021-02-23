import sys
import json
from pprint import pprint

from parser import parse
import cv2

def parse_cheque_by_imgpath(imgpath, jsonpath=None, return_cropped=False):
    if jsonpath is None:
        jsonpath = imgpath + '.json'
    image = cv2.imread(imgpath, 0)
    if image is None:
        raise FileNotFoundError
    # path_to_image, path_to_json = '../ch_photos/40.jpg', '../ch_photos/40.json'
    try:
        with open(jsonpath, 'rb') as file:
            data = json.load(file)['corners']
            points = {i['type']: (i['x'], i['y']) for i in data}
            points = [points['tl'], points['tr'], points['bl'], points['br']]
    except FileNotFoundError:
        points = None
        
    return parse(image, points,
                need_sort=False, 
                return_cropped=return_cropped)


if __name__ == '__main__':    
    path_to_image, path_to_json = sys.argv[1:3]


    parse_cheque_by_imgpath(path_to_image, path_to_json)
