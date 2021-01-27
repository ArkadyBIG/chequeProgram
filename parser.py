# from crop_cheques import Cropper
# from parse_bank_details import parse_bank_details
# from parse_telephone_number import parse_telephone_numbers
# from cheque_persone import parse_person_info
# from classificator import Classificator
from Crop import crop_cheques
from classificator import Classificator
from Parser.hapoalim_parser import HapoalimParser

icons_path = '/home/arkady_big/Repositories/ReciveTextDetector/icons'
cl = Classificator(icons_path)
def parse(img):
    cheque_type = cl.match(img)
    return HapoalimParser.parse(img)




