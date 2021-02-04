#%%
from cv2 import cv2
import numpy as np
import matplotlib.pyplot as plt
import json
import os

def proccess_image(img):
    width = 1200
    height = 600
    img = cv2.resize(img, (width, height))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (3, 3), 3)
    return img

orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher()

class Sample:
    def __init__(self, descriptor, icon_area, class_name):
        self.descriptor = descriptor
        self.icon_area = icon_area
        self.bank_name = class_name
    
    def crop_by_icon_area(self, img):
        area = self.icon_area
        return img[area[0]:area[1], area[2]:area[3]]
    
    def match(self, img):
        img = proccess_image(img)
        img = self.crop_by_icon_area(img)
        _, other_des = orb.detectAndCompute(img, None)
        if other_des is None:
            return -1
        
        matches = bf.knnMatch(self.descriptor, other_des, k=2)
        if matches and len(matches[0]) != 2:
            return -2
    
        score = 0
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                score += 1
        return score
    
    def show_icon_area(self, img):
        plt.imshow(self.crop_by_icon_area(img))
        plt.show()


# To add descriptors for new cheque:
  
# 1. In directory 'icons/' put cropped sample of new icon image
#   name it as follows: listOfCordinaties-bankName.jpg
#   listOfCordinaties - area position and size where to look for this icon in cheque
#       Example: [100, 120, 10, 50]-discount.jpg
# 2. Run this file(will create descriptors and save them in '/icons')
# 3. Move early created  descriptors(.json) to '/Descriptors' directory
# 4. Create file in '/Parser' where create Class as in template /Parser/mizrahi_parser.py(Inherit from BaseCheque)
# 5. Import just created file in 'Parser/__init__.py' as all other imported.

samples = []

for name in os.listdir('icons/'):
    if '.jpg' in name: 
        icon_area = json.loads(name.split('-')[0])
        bank_name = name.split('-')[1].split('.')[0]
        img = cv2.imread('icons/' + name, 0)
        kp, des = orb.detectAndCompute(img, None)
        sample = Sample(des, icon_area, bank_name)
        samples.append(sample)
    
for i, sample in enumerate(samples):
    file_name = f'{sample.bank_name}-{i}.json'
    data = {
        'bank_name': sample.bank_name,
        'descriptor': sample.descriptor.tolist(),
        'icon_area': sample.icon_area,
    }
    data = json.dumps(data)
    with open('icons/' + file_name, 'w') as f:
        f.write(data)


