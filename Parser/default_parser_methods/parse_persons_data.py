#%%
from cv2 import cv2 
import matplotlib.pyplot as plt
import pytesseract
import os
import numpy as np

#%%
def combine_in_order(items, max_step=3):
    for i in range(len(items)):
        slice_ = []
        for _i in range(i, min(len(items), i + max_step), 1):
            slice_.append(items[_i])
            yield slice_

def is_phone_number(text):
    score = 0
    delta = abs(sum(i.isdigit() for i in text) - 10)
    score += 0.6 / (delta / 3 + 1)
    score += 0.4 * ('-' in text)
    return score

def phone_score(text_line):
    score = 80 * max((is_phone_number(''.join(line)) for line in combine_in_order(text_line)), default=0)
    num_of_digits = sum(i.isdigit() for i in ''.join(text_line)) 
    if num_of_digits > 6:
        score += 20 * ('ל' in ''.join(text_line))
        
        score += 20 * ('ט' in ''.join(text_line))

    score += 40 * (text_line[-1][0] == '0')
    return score

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
    # if len(lines) > 1:
    #     scores = []
    #     for i, line in enumerate(lines):
    #         text_line = [data['text'][i] for i in line]
    #         score = phone_score(text_line)
    #         scores.append(score + 20 * i)
    #     # scores[-1] += 30
    #     # if max(scores) < 0:
    #     #     return None
    #     # lines_score = zip(lines, scores)
    #     # lines_score = sorted(lines_score, key=lambda x: x[1], reverse=True)
    #     return [i[0] for i in lines_score]
    # else:
    #     number_indxs = [lines[0]]
    
    return lines[]

def get_line_of_numbers(img, _threshholded=False):
    data = pytesseract.image_to_data(img, output_type='dict', config='--psm 6', lang='heb')
    number_indxs = _find_line_of_numbers(data)
    return number_indxs, data

def get_rectangle(data, word_indxs):
    left = min(10, data['left'][word_indxs[0]])
    right = max(230, data['left'][word_indxs[-1]] + data['width'][word_indxs[-1]])
    top = sum(data['top'][i] for i in word_indxs) // len(word_indxs)
    bottom = sum(data['height'][i] for i in word_indxs) // len(word_indxs) + top

    return left, top, right, bottom

def expand_rectangle(left, top, right, bottom, max_shape, increase=1.5, max_width=None):
    delta_width = int((bottom - top) * (increase - 1))
    top = max(0, top - delta_width)
    left = max(0, left - 5)
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
        yield text_img[top :bottom , left :right].copy()

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
        if (i := text.find('05')) > 0:
            return correct_if_number(text[i:])
    
    
    return None

def find_phone_numbers_from_data(data):
    list_numbers = [''.join(i for i in t if i.isdigit()) for t in data['text']]
    _numbers_list = []
    for num in list_numbers:
        if corrected_num := correct_if_number(num):
            _numbers_list.append(corrected_num)

    if _numbers_list:
        return _numbers_list
    
    for i, num_part in enumerate(data['text']):
        if len(num_part) == 3 and num_part[0] == '0' and i < len(data['text']) - 1:
            if num := correct_if_number(num_part + data['text'][i + 1]):
                return [num]
    text = ''.join(t for t, c in zip(data['text'], data['conf']) if int(c) > 0)
    numbers = ''.join(t for t in text if t.isdigit())
    if num := correct_if_number(numbers):
        return [num]
    
    if num := correct_if_number(text.split(':')[0]):
        return [num]
    if num := correct_if_number(text.split('.')[0]):
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
    _all = [persons_area]
    for img in crop_into_lines(persons_area):
        _all += [np.ones((10, 340), 'uint8')]
        print(img.shape)
        _r = np.ones([img.shape[0], 340 - img.shape[1]], 'uint8')
        _all += [cv2.hconcat([img, _r])]
    draw_and_show_boxes(cv2.vconcat(_all))
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

        








