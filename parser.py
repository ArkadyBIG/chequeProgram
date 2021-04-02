import sys
from cv2 import cv2

# from Crop.crop_cheques import crop
from Crop.crop_by_points import crop
from Parser import cheque_parsers
from classificator import Classificator
import os

DESCRIPTORS_PATH = os.path.join(*os.path.split(__file__)[:-1], 'Descriptors')
cl = Classificator(DESCRIPTORS_PATH)


def parse(img, points=None, need_sort=False, return_cropped=False):
    if points:
        img = crop(img, points, need_sort)
        # cv2.imshow('', img)
        # cv2.waitKey()
    _type = cl.match(img)
    data = cheque_parsers[_type].parse(img)
    if not (data['cheque_num'] or data['account_num'] or data['branch_num'] \
            or data['first_person_id'] or data['first_person_name'] or data['first_person_surname']):
        rotated_img = cv2.rotate(img, cv2.ROTATE_180)
        _type = cl.match(rotated_img)
        data = cheque_parsers[_type].parse(rotated_img)


    if return_cropped:
        return data, img
    return data
