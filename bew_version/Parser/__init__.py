from .aibank_parser import AiBank
from .masad_parser import MasadParser
from .beliomi_parser import BeliomiParser
from .leumi_parser import LeumiParser
from .yiahav_parser import YiahavParser
from .discount_parser import Discount
from .otsearahayal_parser import OtsearahayalParser
from .mizrahi_parser import MizrahiParser
from .merkantil_parser import MerkantilParser
from .doar_parser import Doar
from .hapoalim_parser import HapoalimParser
from .igut_parser import IgutParser

from .base_cheque_class import BaseCheque

cheque_parsers = {cls.TYPE_NAME: cls for cls in BaseCheque.__subclasses__()}
