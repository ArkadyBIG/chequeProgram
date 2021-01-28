from cv2 import cv2
import pytesseract
import re


def default_filter(image):
    return image


def default_crop_person_info(image):
    height, width = image.shape[:2]
    new_width = 900
    scale = new_width / width

    img = cv2.resize(image, None, fx=scale, fy=scale)
    height, width = img.shape[:2]

    crop_width, crop_height = int(width * 0.45), int(height * 0.25)
    img = img[:crop_height, -crop_width:]

    return img


def _name_split(name):
    name = name.split()
    f_name = name.pop()
    l_name = ' '.join(name)

    return {
        'firstname': f_name,
        'lastname': l_name,
    }


def _filter(string, whitelist):
    # person_id = re.split(r'[ \.:]+', person_id[2:])[-1] or None

    return ''.join(c for c in string if c in whitelist)


def _is_correct_id(_id):
    _id = _filter(_id, '0123456789')
    if 8 <= len(_id) <= 9:
        return _id

    return None


def _return_if_2_type(line):
    for c in filter(lambda x: x in line, '\'"'):
        index = line.index(c)

        if _id := _is_correct_id(line[:index]):
            return _id
        if _id := _is_correct_id(line[index:]):
            return _id

    return None


def _parse_info_by_lines(lines) -> list:
    result = []
    lines = list(filter(lambda x: x not in ('', ' '), lines))
    for i, line in enumerate(lines):
        separators = [' ת', ' ח']
        
        for sep in separators:
            *name, person_id = line.split(sep)
            if _id := _return_if_2_type(person_id):
                name = lines[i-1]
                person_id = _id
            elif person_id := _is_correct_id(person_id[2:]):
                name = sep.join(name)
            else:
                continue

            if not name:
                # todo:  and person_id: look up
                continue

            info = {
                'id': person_id,
                'name': name
            }
            result.append(info)
            break

    return result


def parse_person_info(image, lang=None, crop_func=None, filter_func=None):
    img = crop_func(image) if crop_func else default_crop_person_info(image)
    # img = filter_func(img) if filter_func else default_filter(img)

    if not lang:
        lang = 'Hebrew'

    data = pytesseract.image_to_string(img, lang)
    if data is None:
        # return {}?
        raise Exception('Error while finding string data')

    lines = data.splitlines()
    result = _parse_info_by_lines(lines)

    return result


def main():
    for i in range(47):
        img = cv2.imread(f'/home/dima/Documents/Git/cv2/cheque_parser/cropped/{i}.jpg')
        img = default_crop_person_info(img)
        data = pytesseract.image_to_string(img, lang='Hebrew')
        data2 = pytesseract.image_to_data(img, lang='Hebrew', output_type='dict')
        print(str(i)*5, '\n', data)

if __name__ == '__main__':
    main()
