#%%
from cv2 import cv2 
import matplotlib.pyplot as plt
import pytesseract
import os
import numpy as np
from pprint import pprint
#%%
def combine_in_order(items, max_step=3):
    for i in range(len(items)):
        slice_ = []
        for _i in range(i, min(len(items), i + max_step), 1):
            slice_.append(items[_i])
            yield slice_

def _find_line_of_numbers(data):
    lines = []
    for i, text in enumerate(data['text']):
        if text:
            if i and data['text'][i - 1]:
                lines[-1].append(i)
            else:
                lines.append([i])

    if not lines:
        return None
    return lines

def get_line_of_numbers(img, _threshholded=False):
    data = pytesseract.image_to_data(img, output_type='dict', config='--psm 6', lang='heb')
    number_indxs = _find_line_of_numbers(data)
    return number_indxs, data

def get_rectangle(data, word_indxs):
    most_left = min(data['left'][w] for w in word_indxs)
    left = min(data['left'][w] for w in word_indxs)
    right = max(230, data['left'][word_indxs[-1]] + data['width'][word_indxs[-1]])
    top = sum(data['top'][i] for i in word_indxs) // len(word_indxs)
    bottom = sum(data['height'][i] for i in word_indxs) // len(word_indxs) + top

    return left, top, right, bottom

def expand_rectangle(left, top, right, bottom, max_shape, increase=1.5, max_width=None):
    delta_width = int((bottom - top) * (increase - 1))
    top = max(0, top - delta_width)
    left = int(max(0, left - (max_shape[1] - left) * 0.3))
    right = min(max_shape[1], right + 5)
    bottom = min(max_shape[0], bottom + delta_width)
    if max_width is not None:
        med = (top + bottom) / 2
        top = int(max(top, med - max_width / 2))
        bottom = int(min(bottom, med + max_width / 2))
        
    return left, top, right, bottom

def crop_into_lines(text_img):
    list_number_indxs, data = get_line_of_numbers(text_img)
    if not list_number_indxs:
        return []
    for number_indxs in  list_number_indxs:
        rect = get_rectangle(data, number_indxs)
        left, top, right, bottom = expand_rectangle(*rect, max_shape=text_img.shape, max_width=25)
        yield text_img[top :bottom, left:].copy()

def draw_and_show_boxes(img, lang='heb', config='--psm 6'):
    boxes = pytesseract.image_to_boxes(img, lang=lang, config=config)
    _img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h = img.shape[0]
    for b in boxes.splitlines():
        b = b.split(' ')
        color = (255, 0, 0) if b[0].isdigit() and b[5] == '0' else (0, 0, 255)
        _img = cv2.rectangle(_img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), color, 1)
    plt.imshow(_img)
    plt.show()

def correct_if_number(text):
    text = ''.join(t for t in text if t.isdigit())
    if 7 < len(text) < 11:
        if len(text) == 8:
            text = '0' + text
        elif text[0] != '0':
            if text[0] == '5':
                text = '0' + text
            else:
                text = '0' + text[1:]
        return text
    elif len(text) >= 11:
        i = text.find('05')
        if (i) > 0:
            return correct_if_number(text[i:])
    
    
    return None

def find_phone_numbers_from_data(data):
    list_numbers = [''.join(i for i in t if i.isdigit()) for t in data['text']]
    _numbers_list = []
    for num in list_numbers:
        corrected_num = correct_if_number(num)
        if corrected_num:
            _numbers_list.append(corrected_num)

    if _numbers_list:
        return _numbers_list
    
    for i, num_part in enumerate(data['text']):
        if len(num_part) == 3 and num_part[0] == '0' and i < len(data['text']) - 1:
            num = correct_if_number(num_part + data['text'][i + 1])
            if num:
                return [num]
    text = ''.join(t for t, c in zip(data['text'], data['conf']) if int(c) > 0)
    numbers = ''.join(t for t in text if t.isdigit())
    num = correct_if_number(numbers)
    if num:
        return [num]
    
    num = correct_if_number(text.split(':')[0])
    if num:
        return [num]
    num = correct_if_number(text.split('.')[0])
    if num:
        return [num]
    return []

def find_phone_numbers(number_image, _threshholded=False):
    # draw_and_show_boxes(number_image, lang='eng')#, config='--psm 7 -c tessedit_char_whitelist="0123456789 -:."')
    data = pytesseract.image_to_data(number_image, lang='eng', config='--psm 7 -c tessedit_char_whitelist="0123456789 -:."', output_type='dict')

    _numbers_list = find_phone_numbers_from_data(data)
    
    if not _threshholded and not _numbers_list:
        _, number_image = cv2.threshold(number_image, 120, 255, cv2.THRESH_BINARY)
        return find_phone_numbers(number_image,_threshholded=True)

    return _numbers_list or None, '-' in ''.join(data['text'])

def parse_persons_data(cropped_gray, lang='Hebrew'):#, crop_func=None, filter_func=None):
    img = cv2.resize(cropped_gray, (900, 400))
    
    persons_area = img[10:100, 550:-10]
    
    # persons_area = cv2.fastNlMeansDenoising(persons_area, h=15)#, templateWindowSize=5, searchWindowSize=15)    
    # img = cv2.fastNlMeansDenoising(img, h=7, templateWindowSize=5, searchWindowSize=15)    
    # img = cv2.fastNlMeansDenoising(img, h=7, templateWindowSize=5, searchWindowSize=15)    
    # img = cv2.fastNlMeansDenoising(img, h=7, templateWindowSize=5, searchWindowSize=15)    
    
    # data  = pytesseract.image_to_data(img, lang='heb', config='--psm 6', output_type='dict')
    persons_area = cv2.vconcat([persons_area, np.zeros((5, 340), 'uint8')])
    # persons_area = cv2.hconcat([persons_area, np.ones((90, 5), 'uint8')])
    # persons_area[30:65, 40:60] = 0
    # draw_and_show_boxes(persons_area)
    _all = [persons_area]
    list_lines = []
    for img in crop_into_lines(persons_area):
        line = np.zeros((img.shape[0] // 10, img.shape[1]), 'uint8')
        img = cv2.vconcat([line, img, line])
        data = pytesseract.image_to_data(img, lang='heb', config='--psm 7', output_type='dict')
        list_lines.append(data['text'])
        # img = cv2.hconcat([img, np.ones((img.shape[0], 340 - img.shape[1]), 'uint8')])
        # _all += [np.ones((10, 340), 'uint8')]
        # _all += [img]
        # draw_and_show_boxes(img, config='--psm 7')
        
        
    print(list_lines)
    # _all = cv2.vconcat(_all)
    # plt.imshow(persons_area)
    # plt.show()
    
    
    return {}
    # img = filter_func(img) if filter_func else default_filter(img)

    data = pytesseract.image_to_string(img, lang)
    # full_data = pytesseract.image_to_data(img, lang or 'Hebrew', output_type='dict')

    lines = data.splitlines()
    result = _parse_info_by_lines(lines)
    # if not result:
    #     img = crop_top_center(image)
    #     filter_func(img)
    return result

        








