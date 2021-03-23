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
    #
    # {'first_person_id': first_person_id,
    #  'first_person_name': first_person_name,
    #  'second_person_id': second_person_id,
    #  'second_person_name': second_person_name,
    #  'persons_count': persons_count}
    # def def parse_cheque_details_on_numbers(numbers, lang='heb'):
    @classmethod
    def parse_person_info(cls, img):
        person_data = super().parse_person_info(img)
        #
        # first_person_name_list = person_data['first_person_name'] and list(person_data['first_person_name'][::-1].split(" "))
        # seen = set(first_person_name_list)
        # print(first_person_name_list)
        # print(seen)
        # fpnc = first_person_name_list.copy()
        # for elem in seen:
        #     fpnc.remove(elem)
        # print(fpnc)
        #
        # if fpnc and person_data['second_person_name'] is None:
        #     index = first_person_name_list.index(fpnc[0])
        #     print(index)
        #     tmp = first_person_name_list[:index]
        #     person_data['second_person_name'] = first_person_name_list[index+1:]
        #     person_data['first_person_name'] = tmp
        #
        # first_person_name_list = person_data['first_person_name']
        # if first_person_name_list:
        #     person_data['first_person_name'] = ' '.join(first_person_name_list[:-1])
        #     person_data['first_person_lastname'] = first_person_name_list[-1]
        #
        # else:
        #     person_data['first_person_name'] = None
        #     person_data['first_person_lastname'] = None
        # second_person_name_list = person_data['second_person_name']
        # if second_person_name_list:
        #     person_data['second_person_name'] = ' '.join(second_person_name_list[:-1])
        # person_data['second_person_lastname'] = second_person_name_list[-1]

        return person_data
