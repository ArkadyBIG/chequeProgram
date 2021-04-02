try:
    from .default_parser_methods.parse_persons_data import parse_persons_data
    from .default_parser_methods.parse_person import parse_person_info
    from .default_parser_methods.parse_bank_details import parse_bank_details
    from .default_parser_methods.parse_telephone_number import parse_telephone_numbers
except ImportError:
    from default_parser_methods.parse_persons_data import parse_persons_data
    from default_parser_methods.parse_bank_details import parse_bank_details
    from default_parser_methods.parse_telephone_number import parse_telephone_numbers

from abc import ABC
from cv2 import cv2


class BaseCheque(ABC):
    TYPE_NUMBER = None
    TYPE_NAME = None

    @classmethod
    def type_number(cls):
        return cls.TYPE_NUMBER

    @classmethod
    def type_name(cls):
        return cls.TYPE_NAME

    @staticmethod
    def parse_bank_details(image):
        return parse_bank_details(image)

    @staticmethod
    def parse_telephone_numbers(img):
        return parse_telephone_numbers(img)

    @staticmethod
    def parse_person_info(img):
        # person_data = parse_persons_data(img)
        # print(parse_persons_data(img))
        return parse_persons_data(img)

    @classmethod
    def _parse(cls, gray_img, match_telephones_with_persons):
        bank_data = cls.parse_bank_details(gray_img)
        telephones = cls.parse_telephone_numbers(gray_img)
        person_data = cls.parse_person_info(gray_img)
        # if not (bank_data['cheque_num'] or bank_data['account_num'] or bank_data['branch_num'] \
        #         or person_data['first_person_id'] or person_data['first_person_name'] or person_data['first_person_surname']):
        #     rotated_img = cv2.rotate(gray_img, cv2.ROTATE_180)
        #     parse(rotated_img)
            # cv2.imshow('rotated', rotated_img)
            # cv2.waitKey()
            #
            # bank_data = cls.parse_bank_details(rotated_img)
            # telephones = cls.parse_telephone_numbers(rotated_img)
            # person_data = cls.parse_person_info(rotated_img)



        # if match_telephones_with_persons \
        #     and len(person_data) == 1:
        #     telephones['second_telephone_number'] = None
        return {
            **telephones,
            **bank_data,
            **person_data,
            # 'first_person_id': first_person_id,
            # 'second_person_id': second_person_id,
            # 'first_person_name': first_person_name and first_person_name[::-1],
            # 'second_person_name': second_person_name and second_person_name[::-1],
            'type_number': cls.type_number(),
            'type_name': cls.type_name()
        }


        
    @classmethod
    def parse(cls, gray_img):
        return cls._parse(
            gray_img, 
            match_telephones_with_persons=True
        )
