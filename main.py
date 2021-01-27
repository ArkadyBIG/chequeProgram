from parser import parse

from cv2 import cv2


cheque_path = 'cropped/44.jpg' # sys.argv[1]
img = cv2.imread(cheque_path, 0)
print(parse(img))
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

    # cf = Classificator()
    cf = Classificator(icons_path='/home/dima/Documents/Git/cv2/cheque_parser/program/icons')
    return {
        'persons': person_data,
        **numbers,
        **bank_data,
        'type': cf.match(gray_cropped),
    }


# cheque_path = '/home/dima/Documents/Git/cv2/check3.png' # sys.argv[1]
# img = cv2.imread(cheque_path)
# print(parse(img))
