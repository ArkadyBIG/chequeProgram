import sys
from pprint import pprint

from parser import parse
import cv2


path = sys.argv[-1]
image = cv2.imread(path, 0)
if image is None:
    raise FileNotFoundError

info = parse(image)
pprint(info)

