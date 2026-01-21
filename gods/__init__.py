from .brahma import Brahma
from .shiva import Shiva
from .vishnu import Vishnu

def get_all_gods(logger=print):
    return {
        "brahma": Brahma(logger=logger),
        "shiva": Shiva(logger=logger),
        "vishnu": Vishnu(logger=logger)
    }