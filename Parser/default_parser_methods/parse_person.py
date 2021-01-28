from cv2 import cv2
import pytesseract
import re
import matplotlib.pyplot as plt
from pprint import pprint

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

def default_filter(image):
    return image


def resize_by_width(image, new_width=900):
    height, width = image.shape[:2]
    scale = new_width / width

    img = cv2.resize(image, None, fx=scale, fy=scale)
    return img


def default_crop_person_info(image):
    height, width = image.shape[:2]

    crop_width, crop_height = int(width * 0.45), int(height * 0.25)
    img = image[:crop_height, -crop_width:]

    return img


def crop_top_center(image):
    height, width = image.shape[:2]

    crop_height = int(height * 0.25)
    crop_x1 = int(width * 0.44)
    crop_x2 = int(width * 0.66)
    img = image[:crop_height, crop_x1:crop_x2]

    return img


def _name_split(name):
    name = name.replace('\u200f', '')

    # name = name.split()
    # f_name = name.pop()
    # l_name = ' '.join(name)
    #
    # return {
    #     'firstname': f_name,
    #     'lastname': l_name,
    # }
    return {'name': name}


def _filter(string, whitelist):
    return ''.join(c for c in string if c in whitelist)


def _is_correct_id(_id):
    _id = _filter(_id, '0123456789')
    if 8 <= len(_id) <= 9:
        return _id

    return None


def _return_if_2_type(line):
    for c in filter(lambda x: x in line, '\'"'):
        index = line.index(c)
        _id = _is_correct_id(line[:index])
        if not _id:
            _id = _is_correct_id(line[index:])
        if _id:
            return _id

    return None


def _parse_info_by_lines(lines) -> list:
    result = []
    lines = list(filter(lambda x: x not in ('', ' '), lines))
    for i, line in enumerate(lines):
        separators = [' ת', ' ח']

        for sep in separators:
            *name, person_id = line.split(sep)
            name = sep.join(name)

            _id = _return_if_2_type(person_id)
            if _id:
                name = lines[i-1]
            else:
                _id = _is_correct_id(person_id[2:])
                if not _id:
                    _id = _is_correct_id(name.split(' ', 1)[0])
                    if _id:
                        name = name.split(' ', 1)[-1]
                    else:
                        continue
            person_id = _id

            # if _id := _return_if_2_type(person_id):
            #     name = lines[i-1]
            # elif _id := _is_correct_id(person_id[2:]):
            #     pass
            # elif _id := _is_correct_id(name.split(' ', 1)[0]):
            #     name = name.split(' ', 1)[-1]
            # else:
            #     continue
            # person_id = _id

            if not name:
                # todo:  and person_id: look up
                continue

            info = {
                'id': person_id,
                **_name_split(name)
            }
            result.append(info)
            break

    return result


def parse_person_info(image, lang='Hebrew', crop_func=None, filter_func=None):
    if crop_func:
        img = crop_func(image)
    else:
        img = resize_by_width(image)
        img = default_crop_person_info(img)
    
    
    # data  = pytesseract.image_to_data(img, lang='heb', config='--psm 6', output_type='dict')
    
    # img = filter_func(img) if filter_func else default_filter(img)

    data = pytesseract.image_to_string(img, lang)
    # full_data = pytesseract.image_to_data(img, lang or 'Hebrew', output_type='dict')

    lines = data.splitlines()
    result = _parse_info_by_lines(lines)
    # if not result:
    #     img = crop_top_center(image)
    #     filter_func(img)
    return result


def main():
    for i in range(47):
        img = cv2.imread(f'/home/dima/Documents/Git/cv2/cheque_parser/cropped/{i}.jpg')
        img = default_crop_person_info(img)

        data = pytesseract.image_to_string(img, lang='Hebrew')
        # data2 = pytesseract.image_to_data(img, lang='Hebrew', output_type='dict')
        print(str(i) * 5, '\n', data)


if __name__ == '__main__':
    main()
