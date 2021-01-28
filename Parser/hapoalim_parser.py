from .base_cheque_class import BaseCheque


class HapoalimParser(BaseCheque):
    TYPE_NUMBER = 12
    TYPE_NAME = 'hapoalim'

    @classmethod
    def parse(cls, gray_img):
        return cls._parse(
            gray_img,
            match_telephones_with_persons=False
        )
