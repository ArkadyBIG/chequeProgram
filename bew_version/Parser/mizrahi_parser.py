from .base_cheque_class import BaseCheque
from .default_parser_methods.parse_bank_details import parse_bank_details


class MizrahiParser(BaseCheque):
    TYPE_NUMBER = 20
    TYPE_NAME = 'mizrahi'
    
    def parse_bank_details(image):
        return parse_bank_details(image, area_to_search=[50,120,20,265])
