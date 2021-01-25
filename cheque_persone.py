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


def _parse_info_by_lines(lines) -> list:
    result = []

    for line in lines:
        separator = ' ת'
        *name, person_id = line.split(separator)
        if not name:
            continue

        name = separator.join(name).split()
        f_name = name.pop()
        l_name = ' '.join(name)
        person_id = re.split(r'[ \.:]+', person_id[2:])[-1] or None

        info = {
            'id': person_id,
            'firstname': f_name,
            'lastname': l_name,
        }
        result.append(info)

    return result


def parse_person_info(image, lang=None, crop_func=None, filter_func=None):
    img = crop_func(image) if crop_func else default_crop_person_info(image)
    img = filter_func(img) if filter_func else default_filter(img)

    if not lang:
        lang = 'Hebrew'

    data = pytesseract.image_to_string(img, lang)
    if data is None:
        # return {}?
        raise Exception('Error while finding string data')

    lines = data.splitlines()
    return _parse_info_by_lines(lines)


def main():
    for i in range(47):
        img = cv2.imread(f'/home/dima/Documents/Git/cv2/cheque_parser/cropped/{i}.jpg')
        img = default_crop_person_info(img)
        data = pytesseract.image_to_string(img, lang='Hebrew')
        data2 = pytesseract.image_to_data(img, lang='Hebrew', output_type='dict')
        print(str(i)*5, '\n', data)

if __name__ == '__main__':
    main()
