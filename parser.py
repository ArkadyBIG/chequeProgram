import sys
from cv2 import cv2

# from Crop.crop_cheques import crop
from Crop.crop_by_points import crop
from Parser import cheque_parsers
from classificator import Classificator
import os

DESCRIPTORS_PATH = os.path.join(*os.path.split(__file__)[:-1], 'Descriptors')
cl = Classificator(DESCRIPTORS_PATH)


def parse(img, points=None, need_sort=False):
    if points:
        img = crop(img, points, need_sort)

    _type = cl.match(img)
    return cheque_parsers[_type].parse(img)
