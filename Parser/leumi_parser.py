from .base_cheque_class import BaseCheque


class LeumiParser(BaseCheque):
    TYPE_NUMBER = 10
    TYPE_NAME = 'leumi'

    @classmethod
    def parse(cls, gray_img):
        return super()._parse(
            gray_img,
            match_telephones_with_persons=False
        )
