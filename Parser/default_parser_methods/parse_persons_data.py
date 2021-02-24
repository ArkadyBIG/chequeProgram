
from cv2 import cv2 
import matplotlib.pyplot as plt
import pytesseract
import os
import numpy as np
from pprint import pprint
from typing import List
import itertools

def _find_line_of_numbers(data):
    lines = []
    for i, text in enumerate(data['text']):
        if text:
            if i and data['text'][i - 1]:
                lines[-1].append(i)
            else:
                lines.append([i])

    if not lines:
        return []
    return lines

def get_line_of_numbers(img):
    data = pytesseract.image_to_data(img, output_type='dict', config='--psm 6', lang='heb')
    number_indxs = _find_line_of_numbers(data)
    
    right_block = []
    left_block = []
    
    for line in number_indxs:
        max_gap = 0
        right_block.append([])
        left_block.append([])
        if len(line) == 1:
            right_block[-1].append(line[0])
            continue
        # for _next, prev in zip(line, line[1:]):
        prev_x = data['left'][line[0]] + data['width'][line[0]]
        for i, index in enumerate(line):
            pos_x = data['left'][index] + data['width'][index]
            gap = prev_x - pos_x
            if gap > 200:
                # print('gap is too big', gap)
                break
            right_block[-1].append(index)
            prev_x = data['left'][index]
        
        left_block[-1].extend(line[i:])
        
        
    
    return right_block, left_block, data

def get_rectangle(data, word_indxs, max_right=230):
    most_left = min(data['left'][w] for w in word_indxs)
    left = min(data['left'][w] for w in word_indxs)
    right = max(max_right, data['left'][word_indxs[-1]] + data['width'][word_indxs[-1]])
    top = sum(data['top'][i] for i in word_indxs) // len(word_indxs)
    bottom = sum(data['height'][i] for i in word_indxs) // len(word_indxs) + top

    return left, top, right, bottom

def expand_rectangle(left, top, right, bottom, max_shape, increase=1.5, max_width=None, max_left=0):
    delta_width = int((bottom - top) * (increase - 1))
    top = max(0, top - delta_width)
    left = int(max(0, min(max_left, left - (max_shape[1] - left) * 0.3)))
    right = min(max_shape[1], right + 5)
    bottom = min(max_shape[0], bottom + delta_width)
    if max_width is not None:
        med = (top + bottom) / 2
        top = int(max(top, med - max_width / 2))
        bottom = int(min(bottom, med + max_width / 2))
        
    return left, top, right, bottom

def get_text_lines(text_img):
    right_block, left_block, data = get_line_of_numbers(text_img)
    if not right_block:
        return []
    
    right_img_slices = []
    for number_indxs in  right_block:
        rect = get_rectangle(data, number_indxs)
        left, top, right, bottom = expand_rectangle(*rect, max_shape=text_img.shape, max_width=25, max_left=350)
        right_img_slices.append(text_img[top :bottom, left:])
    
    left_img_slices = []
    for number_indxs in  left_block:
        if not number_indxs:
            continue
        rect = get_rectangle(data, number_indxs, max_right=0)
        left, top, right, bottom = expand_rectangle(*rect, max_shape=text_img.shape, max_width=25)
        # draw_and_show_boxes(text_img[top :bottom, left:right])
        left_img_slices.append(text_img[top :bottom, left:right])
        
    return right_img_slices#, left_img_slices
    

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

def remove_junks(data, max_char_width=15, min_conf=1):
    clear_data = {
        'text' : [],
        'width': [],
        'conf' : [],
        'left' : []
    }
    data = [data['text'], data['width'], data['conf'], data['left']]
    for text, width, conf, left in zip(*data):
        if not text \
            or (width / len(text) > max_char_width and len(text) < 5 and text != '1' and text != 'תז')\
            or (conf < min_conf and len(text) < 5):
                continue
        clear_data['text' ].append(text)
        clear_data['width'].append(width)
        clear_data['conf' ].append(conf)
        clear_data['left' ].append(left)
    return clear_data
            
            
            
def split_lines_to_data(persons_area, add_black_line=False, config=''):
    if add_black_line:
        persons_area = cv2.vconcat([persons_area, np.zeros((5, persons_area.shape[1]), 'uint8')])

    # draw_and_show_boxes(persons_area)
    
    lines = []
    
    for img in get_text_lines(persons_area):
        data = pytesseract.image_to_data(img, lang='heb', config='--psm 7', output_type='dict')
        
        # draw_and_show_boxes(img)
        
        cdata = remove_junks(data)
        # print(data['text'], cdata['text'])
        lines.append(cdata)
        
    return lines

def strip_not_digits(word):
    if not word:
        return ''

    for i, c in enumerate(word):
        if c.isdigit():
           break 
    word = word[i:]
    for i, c in enumerate(word[::-1]):
        if c.isdigit():
           break 
    return word[:(-i or None)]

    

def find_id_in_word(word):
    numbers = strip_not_digits(word)
    if not all(i.isdigit() for i in numbers):
        return None
        
    if 10 >= len(numbers) >= 8:
        return numbers[:9]
    return None 

def find_ids_left_from_TZ(textlines):
    ids = []
    for line in textlines:
        line = line['text']
        for i, word in enumerate(line):
            if not set(word).isdisjoint('ז1תה'):
                if 1 <= len(word) < 5:
                    if i + 1 < len(line):
                        _id = find_id_in_word(line[i + 1])
                        ids.append(_id)
                    if i + 2 < len(line):
                        ids.append(find_id_in_word(line[i + 2]))
                    if i - 1 >= 0:
                        ids.append(find_id_in_word(line[i - 1]))
                elif '1' not in word[:3] and 'ש' not in word:
                    right = ''
                    if 'ת' in word:
                        left, right = word.split('ת')[:2]
                    elif 'ז' in word:
                        left, right = word.split('ז')[:2]
                    elif 'ה' in word:
                        left, right = word.split('ה')[:2]
                    ids.append(find_id_in_word(right))
                    
    return [i for i in set(ids) if i][:2]
                        
                    
def find_ids_alone_on_line(textlines):
    ids = []
    for line in textlines[:3]:
        for word in line['text']:
            ids.append(find_id_in_word(word))
    return list(filter(None, ids))[:2]
    
    

def find_ids_in_textlines(textlines: List[List[str]]):
    ids = find_ids_left_from_TZ(textlines)
    if not ids:
        ids = find_ids_alone_on_line(textlines)
    return ids

def remove_not_letters(_str):
    return _str.replace('=', '').replace('/', '').replace('|', '').replace(',', '').replace('ת.ז.', '').replace('.', '')
    

def find_names_right_from_TZ(textlines):
    names = []
    for line_index, line in enumerate(textlines):
        line = line['text']
        names_on_line = []
        for i, word in enumerate(line):
            if not set(word).isdisjoint('ז1תה'):
                if 1 <= sum(not i.isdigit() for i in set(word)) < 5:
                    name = ' '.join(line[:i])
                    
                    numbers = ''.join(i for i in ''.join(line[i:]) if i.isdigit())
                    
                    if not any(i.isdigit() for i in name) and \
                        (len(numbers) > 7 or sum(i.isdigit() for i in word) > 7):
                        names_on_line.append(name)
        if line_index > 0 and names[-1] and not names_on_line:
            break 
        names.append(max(names_on_line, default=[], key=len))
    return list({remove_not_letters(i) for i in names if i})[:2]

def find_names_alone_on_line(textlines):
    names = []
    for line in textlines[:-2]:
        text = ' '.join(line['text'])
        if not any(i.isdigit() for i in text):
            names.append(text)
    return [remove_not_letters(n) for n in names[:2]]

def find_names_in_textlines(textlines):
    text = ''.join(sum((i['text'] for i in textlines), []))
    
    look_for_TZ_first = \
        ('ת.ז.' in text or '.ז.' in text or 'תז.' in text or 'ת.ז' in text or 'תז ' in text or ' תז' in text or 'ת.1' in text or 'ת"ז' in text)
    
    queue = [find_names_alone_on_line, find_names_right_from_TZ]
    
    names = queue[look_for_TZ_first](textlines)
    if not names:
        names = queue[not look_for_TZ_first](textlines)
    # print('names:', names)
    return names
    

def parse_persons_data(cropped_gray, lang='Hebrew'):
    img = cv2.resize(cropped_gray, (900, 400))
    
    persons_area = img[10:100, 400:-10]
    
    # persons_area = cv2.fastNlMeansDenoising(persons_area, h=10)#, templateWindowSize=5, searchWindowSize=15)    
    
    
    textlines = split_lines_to_data(persons_area, add_black_line=True)
    persons_id = find_ids_in_textlines(textlines)
    persons_names = find_names_in_textlines(textlines)
    
    if not persons_id:
        textlines = split_lines_to_data(persons_area, add_black_line=False)
        persons_id = find_ids_in_textlines(textlines)
        persons_names = max(find_names_in_textlines(textlines), persons_names, key=lambda x: len(''.join(x)))
    
    if not persons_id:
        textlines = split_lines_to_data(persons_area[:60, :250], add_black_line=True, config='')
        persons_id = find_ids_in_textlines(textlines)
    
    data = []
    for _id, name in itertools.zip_longest(persons_id, persons_names):
        data.append({
            'id'   : _id,
            'name' : name
        })
    
    return data
