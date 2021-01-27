from parser import parse

from cv2 import cv2


cheque_path = 'cropped/44.jpg' # sys.argv[1]
img = cv2.imread(cheque_path, 0)
print(parse(img))
