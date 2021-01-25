import sys
try:
    from .crop_cheques import Cropper
    from .parse_bank_details import parse_bank_details
    from .parse_telephone_number import parse_telephone_numbers
    from .cheque_persone import parse_person_info
    from .classificator import Classificator
except ImportError:
    from crop_cheques import Cropper
    from parse_bank_details import parse_bank_details
    from parse_telephone_number import parse_telephone_numbers
    from cheque_persone import parse_person_info
    from classificator import Classificator

from cv2 import cv2

# if len(sys.argv) < 2:
#     raise NotADirectoryError

#
# if img is None:
#     raise NotADirectoryError


def parse(cheque_image):
    # cropped = Cropper(cheque_image).crop()
    cropped = cheque_image
    gray_cropped = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)

    bank_data = parse_bank_details(gray_cropped)
    numbers = parse_telephone_numbers(gray_cropped)
    person_data = parse_person_info(gray_cropped)

    cf = Classificator()
    # cf = Classificator(icons_path='cheque_parser/program/icons/')
    return {
        'persons': person_data,
        **numbers,
        **bank_data,
        'type': cf.match(gray_cropped),
    }


# cheque_path = '/home/dima/Documents/Git/cv2/check3.png' # sys.argv[1]
# img = cv2.imread(cheque_path)
# print(parse(img))
