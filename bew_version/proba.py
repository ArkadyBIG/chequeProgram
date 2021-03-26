import matplotlib.pyplot as plt
from PIL import Image

import cv2
from scipy import stats
import numpy as np
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
from PIL import Image
import json

def draw_and_show_boxes(img, lang='heb', config='--psm 6'):
    boxes = pytesseract.image_to_boxes(img, lang=lang, config=config)
    _img = img.copy()#cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h = img.shape[0]
    for b in boxes.splitlines():
        b = b.split(' ')
        color = (255, 0, 0) if b[0].isdigit() and b[5] == '0' else (0, 0, 255)
        _img = cv2.rectangle(_img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), color, 1)
    plt.imshow(_img)
    plt.show()

def preprocessing(image):
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # denosied = cv2.fastNlMeansDenoising(gray, h=10)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    bg = cv2.morphologyEx(image, cv2.MORPH_DILATE, se)
    out_gray = cv2.divide(image, bg, scale=255)
    #     adaptive_treshold = cv2.adaptiveThreshold(denosied, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 21)

    return out_gray  # adaptive_treshold

def draw_boxes(img):
    d = pytesseract.image_to_data(img, lang = 'eng+heb', output_type='dict')
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return img
img = cv2.imread('/home/anastasja/PycharmProjects/chequeProgram/test_img.jpeg')
config = '--psm 6 -c tesseract_white_list=אבבּגדהוזחטיךךּככּלםמןנסעףפפּץצקרשׁשׂתתּ1234567890-'

proc_img = preprocessing(img)
d = pytesseract.image_to_data(proc_img, lang = 'eng+heb', config = config , output_type='dict')
print(d['text'])
draw_and_show_boxes(proc_img, 'eng+heb', config = config )
cv2.imshow('processed img', proc_img)
# cv2.imshow('box img', box_img)
cv2.waitKey()
cv2.destroyAllWindows()