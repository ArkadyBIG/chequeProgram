import sys
from cv2 import cv2

from Crop.crop_cheques import crop
from Parser import cheque_parsers
from classificator import Classificator

DESCRIPTORS_PATH = '/home/arkady_big/Repositories/ReciveTextDetector/chequeProgram/Descriptors'
cl = Classificator(DESCRIPTORS_PATH)


def parse(cropped):
    # cropped = crop(img)
    _type = cl.match(cropped)
    return cheque_parsers[_type].parse(cropped)


if __name__ == '__main__':
    img_path = sys.argv[1]

    img = cv2.imread(img_path, 0)


    print(parse(cropped))
