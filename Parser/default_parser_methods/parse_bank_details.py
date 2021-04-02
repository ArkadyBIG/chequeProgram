# %%
from cv2 import cv2
import pytesseract
import matplotlib.pyplot as plt
import os
import numpy as np
from pprint import pprint


def digits_score(text):
    return 2 * sum(c.isdigit() for c in text)  # - len(text)


def draw_and_show_boxes(img, config='--psm 7'):
    boxes = pytesseract.image_to_boxes(img, lang='eng+heb', config=config)
    _img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h = img.shape[0]
    for b in boxes.splitlines():
        b = b.split(' ')
        color = (255, 0, 0) if b[0].isdigit() and b[5] == '0' else (0, 0, 255)
        _img = cv2.rectangle(
            _img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), color, 1)
    cv2.imshow(' ', _img)


def draw_and_show_rectangle(img, left, top, right, bottom):
    ract = cv2.rectangle(img.copy(),
                         (left, top),
                         (right, bottom),
                         (255, 0, 255), 1)
    plt.imshow(ract)
    plt.show()


def print_img_data(data):
    for c, t in zip(data['conf'], data['text']):
        if t:
            print(repr(t), c)


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
    if len(lines) > 1:
        scores = []
        for line in lines:
            texts = (data['text'][i] for i in line)
            # print([data['text'][i] for i in line])
            score = sum(digits_score(t) for t in texts)
            # print(score)
            scores.append(score)
        number_indxs = lines[scores.index(max(scores))]
    else:
        number_indxs = lines[0]

    return number_indxs

def preprocessed(image):
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    bg = cv2.morphologyEx(image, cv2.MORPH_DILATE, se)
    out_gray = cv2.divide(image, bg, scale=255)

    return out_gray

def get_line_of_numbers(img, show_steps, _threshholded=False):
    # plt.imshow(img)
    # plt.show()
    # cv2.waitKey()
    data = pytesseract.image_to_data(preprocessed(img), output_type='dict', lang='eng')
    # draw_and_show_boxes(preprocessed(img))
    # cv2.waitKey()

    # preprocessed_data = pytesseract.image_to_data(preprocessed(img), output_type='dict', lang='eng')

    # data_eng = pytesseract.image_to_data(img, output_type='dict', lang='eng', config='-c tessedit_char_whitelist="0123456789 " --psm 7')
    # todo
    if show_steps:
        print_img_data(data)
    number_indxs = _find_line_of_numbers(data)
    if number_indxs is None:
        if _threshholded:
            return None, None
        _, _th = cv2.threshold(img, img.mean() * 0.9, 255,
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
        _th = 255 - _th

        return get_line_of_numbers(_th, show_steps, True)
    return number_indxs, data


def get_rectangle(data, word_indxs):
    left = min(10, data['left'][word_indxs[0]])
    right = max(230, data['left'][word_indxs[-1]] +
                data['width'][word_indxs[-1]])
    # top_lines = sorted(data['top'])
    # top = top_lines[len(top_lines) // 2]
    top = sum(data['top'][i] for i in word_indxs) // len(word_indxs)
    bottom = sum(data['height'][i]
                 for i in word_indxs) // len(word_indxs) + top

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


def crop_numbers(cheque_details, show_steps=False):
    if show_steps:
        draw_and_show_boxes(cheque_details)

    # data = pytesseract.image_to_data(cheque_details, output_type='dict', lang='eng')
    # if show_steps: print_img_data(data)


    number_indxs, data = get_line_of_numbers(cheque_details, show_steps)

    if not number_indxs:
        return None

    rect = get_rectangle(data, number_indxs)
    left, top, right, bottom = expand_rectangle(
        *rect, max_shape=cheque_details.shape, max_width=25)

    if show_steps:
        draw_and_show_rectangle(cheque_details, left, top, right, bottom)
    return cheque_details[top:bottom, left:right].copy()


def get_middle_slice(img, width):
    top = img.shape[0] // 2 - width // 2
    bottom = img.shape[0] // 2 + width // 2
    return img[top: bottom, ...].copy()


def get_blank_positions(img):
    _, th = cv2.threshold(img, img.mean(), 255, cv2.THRESH_BINARY_INV)
    hist = cv2.reduce(th, 0, cv2.REDUCE_AVG)[0]
    return [y for y in range(1, hist.shape[0]-1) if hist[y] <= 10]


def get_gaps_positions(blank_positions):
    max_step = 2
    gaps = [[blank_positions[0]]]
    for i in range(1, len(blank_positions)):
        if abs(blank_positions[i - 1] - blank_positions[i]) <= max_step:
            gaps[-1].append(blank_positions[i])
        else:
            gaps.append([blank_positions[i]])

    gaps = [(g[0], g[-1]) for g in gaps if len(g) > 1]
    gaps = sorted(gaps, key=lambda x: x[-1] - x[0], reverse=1)
    return gaps


def reduce_extra_gaps_on_image(img, gaps, min_gap_width):
    gaps = [g for g in gaps
            if g[-1] - g[0] >= min_gap_width]

    to_delete = []
    for gap in gaps:
        if gap[-1] > 160:
            if gap[-1] - gap[0] >= 6:
                to_delete.append(gap)

    if to_delete:
        most_left = min(to_delete, key=lambda x: x[0])
        img = img[:, :most_left[0] + 5]

    to_delete = []
    for gap in gaps:
        if gap[0] < 25:
            if gap[-1] - gap[0] >= 6:
                to_delete.append(gap)
            else:
                gaps.remove(gap)
    if to_delete:
        most_right = max(to_delete, key=lambda x: x[0])[-1] - 5
        img = img[:, most_right:]
        for gap in to_delete:
            gaps.remove(gap)
        gaps = [(g[0] - most_right, g[-1] - most_right) for g in gaps]

    gaps = [g for g in gaps if g[0] > 25 and g[1] < 160]
    return img, gaps


def show_blank_positions(img, pos):
    _img = img.copy()
    for y in pos:
        cv2.line(_img, (y, 0), (y, 100), (255, 0, 0), 1)
    plt.imshow(_img)
    plt.show()


def show_gaps(img, gaps):
    gaps_img = img.copy()
    for gap in gaps:
        for y in gap:
            cv2.line(gaps_img, (y, 0), (y, 100), (255, 0, 0), 1)
    plt.imshow(gaps_img)
    plt.show()


def get_right_split(gaps):
    pretendents = (g for g in gaps if 110 <=
                   g[0] <= 170 and 110 <= g[1] <= 170)
    split = max(pretendents, key=lambda x: x[-1] - x[0])
    return split


def show_vertical_lines(img, positions):
    _img = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)
    for pos in positions:
        cv2.line(_img, (pos, 0), (pos, img.shape[0]), (255, 0, 0), 1)
    plt.imshow(_img)
    plt.show()


def numbers_split(gaps):
    right_split = get_right_split(gaps)
    widest_two = gaps[:2]
    splits = set(widest_two + [right_split])
    splits = [sum(i) // 2 for i in splits]
    return sorted(splits)


def parse_cheque_details_on_numbers(numbers, lang='heb'):
    data = pytesseract.image_to_data(preprocessed(numbers),
                                     lang=lang,
                                     config='-c tessedit_char_whitelist="0123456789 " --psm 7',
                                     output_type='dict')

    text = data['text']
    conf = data['conf']
    text = [''.join(i for i in t if i.isdigit()) for t in text]
    conf = [c for t, c in zip(text, data['conf']) if t]
    text = [t for t in text if t]
    if len(text) == 3:
        cheque_num, cheque_conf = text[0], conf[0]
        branch_num, branch_conf = text[1][2:][:3], conf[1]
        account_num, account_conf = text[2], conf[2]
    elif len(text) == 4:
        if len(text[0]) >= 7:
            cheque_num, cheque_conf = text[0], conf[0]
        else:
            cheque_num = text[0] + text[1]
            cheque_conf = (conf[0] + conf[1]) / 2
        branch_num, branch_conf = text[2][:3], conf[2]
        account_num, account_conf = text[3], conf[3]
    else:
        branch_num, branch_conf = None, -1
        account_num, account_conf = None, -1
        cheque_num, cheque_conf = None, -1
    return {
        'cheque_num': cheque_num,
        'branch_num': branch_num,
        'account_num': account_num,
        'cheque_conf': cheque_conf,
        'branch_conf': branch_conf,
        'account_conf': account_conf
    }



def get_best_data(data1, data2):

    def best(par): return data1[par + '_num'] if data1[par + '_conf'] > data2[par + '_conf'] else data2[par + '_num']

    cheque_num = best('cheque')
    if data1['cheque_num'] and data2['cheque_num'] \
            and abs(len(data1['cheque_num']) - len(data2['cheque_num'])) > 2:
        if len(data1['cheque_num']) == 8:
            cheque_num = data1['cheque_num']
        if len(data2['cheque_num']) == 8:
            cheque_num = data2['cheque_num']

    account_num = best('account')
    if data1['account_num'] and data2['account_num'] \
            and abs(len(data1['account_num']) - len(data2['account_num'])) >= 4:
        data1_abs = abs(10 - len(data1['account_num']))
        data2_abs = abs(10 - len(data2['account_num']))
        if data1_abs < data2_abs:
            account_num = data1['account_num']
        else:
            account_num = data2['account_num']
        
    return {
        'cheque_num': cheque_num,
        'branch_num': best('branch'),
        'account_num': account_num,
    }


def parse_bank_details(img, show_steps=0, area_to_search=[110, 160, 20, 265]):
    # draw_and_show_boxes(img, config='-c tessedit_char_whiteliimst="0123456789 " --psm 7')
    img = cv2.resize(img, (900, 400))
    # cheque_details = img[110:160, 20:265]
    y1, y2, x1, x2 = area_to_search
    cheque_details = img[y1:y2, x1:x2]

    # cv2.imshow(' ', cheque_details)
    # cv2.waitKey()

    numbers = crop_numbers(cheque_details, show_steps)
    # cv2.imshow(' ', numbers)
    # cv2.waitKey()
    if numbers is None:
        return {
            'cheque_num': None,
            'account_num': None,
            'branch_num': None,
        }

    numbers = cv2.fastNlMeansDenoising(numbers, h=15, templateWindowSize=3, searchWindowSize=12)
    

    middle_slice = get_middle_slice(numbers, 6)
    blank_positions = get_blank_positions(middle_slice)

    if show_steps:
        show_blan2k_positions(numbers, blank_positions)

    W = numbers.shape[1]
    gaps = get_gaps_positions(blank_positions)
    # numbers, gaps = reduce_extra_gaps_on_image(numbers, gaps, W // 80)
    
    numbers = cv2.fastNlMeansDenoising(numbers, h=6)
    # plt.imshow(numbers)
    # plt.show()
    # cv2.waitKey()
    # cv2.imshow('numbers', numbers)
    # cv2.waitKey()
    data_Hebrew = parse_cheque_details_on_numbers(numbers, 'Hebrew')


    data_eng = parse_cheque_details_on_numbers(numbers, 'eng')
    data = get_best_data(data_eng, data_Hebrew)
    # data = data_Hebrew2
    return data
