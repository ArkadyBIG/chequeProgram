from cv2 import cv2
import matplotlib.pyplot as plt
import pytesseract
import os
import numpy as np

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
    
    return lines[::-1]


def get_line_of_numbers(img, _threshholded=False):
    # draw_and_show_boxes(img)
    data = pytesseract.image_to_data(img, output_type='dict', config='--psm 6', lang='heb')
    number_indxs = _find_line_of_numbers(data)
    # if number_indxs is None:
    #     if _threshholded:
    #         return None, None
    #     _, _th = cv2.threshold(img, img.mean() * 0.9, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
    #     _th = 255 - _th
    #     return get_line_of_numbers(_th, True)
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


def crop_telephon_numbers(telephon_area):
    list_number_indxs, data = get_line_of_numbers(telephon_area)
    if not list_number_indxs:
        return [None]
    for number_indxs in  list_number_indxs:
        rect = get_rectangle(data, number_indxs)
        left, top, right, bottom = expand_rectangle(*rect, max_shape=telephon_area.shape, max_width=25)

        yield telephon_area[top:bottom, left:right].copy()


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
    num = None
    if 7 < len(text) < 11:
        if len(text) == 8:
            text = '0' + text
        elif text[0] != '0':
            if text[0] == '5':
                text = '0' + text
            else:
                text = '0' + text[1:]
        num = text
    elif len(text) >= 11:
        i = text.find('05')
        if i > 0:
            num = correct_if_number(text[i:])
    if num and num[1] != '0':
        return num
    return None


def find_phone_numbers_from_data(data):#054-9400045
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
    if not num:
        num = correct_if_number(text.split(':')[0])
    if not num:
        num = correct_if_number(text.split('.')[0])

    text = ''.join(data['text']).replace(' ', '').strip('-')
    if '-' in text:
        parts = text.split('-')
        if len(parts[0]) == 3 and len(parts) > 1:
            num = correct_if_number(parts[0] + parts[1])
            if num:
                return [num]
    text = [t for t, c in zip(data['text'], data['conf']) if int(c) > 0]
    for part in combine_in_order(text, max_step=2):
        if len(''.join(text[:text.index(part[0])])) > 3:
            break
        num = correct_if_number(''.join(part))
        if num:
            return [num]
    
    return [num] if num else []


def find_phone_numbers(number_image, _threshholded=False):
    # draw_and_show_boxes(number_image, lang='eng')#, config='--psm 7 -c tessedit_char_whitelist="0123456789 -:."')
    config = '--psm 7 -c tessedit_char_whitelist="0123456789 -:."'
    data = pytesseract.image_to_data(number_image, lang='eng',
                                     config=config, output_type='dict')

    _numbers_list = find_phone_numbers_from_data(data)
    
    if not _threshholded and not _numbers_list:
        _, number_image = cv2.threshold(number_image, 120, 255, cv2.THRESH_BINARY)
        return find_phone_numbers(number_image,_threshholded=True)

    text = ''.join(data['text'])
    # index = text.find('-')
    # if index > 0 and index != len(text) - 1:
    _dash = ('-' in text)
    return _numbers_list or None, _dash

def _parse_telephon_area(number_area):
    # draw_and_show_boxes(number_area, config='--psm 6')
    number_images = crop_telephon_numbers(number_area)
    
    numbers = []
    dash_in_phone_number = False
    found_numbers_on_previous = False
    for number_image in number_images:
        if number_image is None:
            continue
        black_line = np.ones([number_image.shape[0] // 10, number_image.shape[1]], 'uint8')
        number_image = cv2.vconcat([number_image, black_line])
        
        # draw_and_show_boxes(number_image, config='--psm 7')
        
        nums, _dash = find_phone_numbers(number_image)
        if nums:
            if len(numbers) == 1 and dash_in_phone_number == _dash:
                numbers += nums
            elif not numbers:
                numbers += nums
                dash_in_phone_number = _dash
            if len(numbers) == 2:
                break
            found_numbers_on_previous = True
        elif found_numbers_on_previous:
            break
        else:
            found_numbers_on_previous = False
    return numbers

def parse_telephone_numbers(cropped_gray):
    img = cv2.resize(cropped_gray, (900, 400))
    number_area = img[50:130, 650:-10]
    
    number_area_denoised = cv2.fastNlMeansDenoising(number_area, h=13)
    number_area_denoised = cv2.vconcat([number_area_denoised, np.ones([5, number_area.shape[1]], 'uint8')])
    numbers = _parse_telephon_area(number_area)
    
    if not numbers:
        number_area = cv2.vconcat([number_area, np.ones([5, number_area.shape[1]], 'uint8')])
        numbers = _parse_telephon_area(number_area)
    return {
        'first_telephone_number': numbers.pop(0) if numbers else None,
        'second_telephone_number': numbers.pop(0) if numbers else None,
    }
