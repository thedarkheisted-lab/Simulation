from .brahma import Brahma
from .shiva import Shiva
from .vishnu import Vishnu

def get_all_gods():
    return {
        "brahma": Brahma(),
        "shiva": Shiva(),
        "vishnu": Vishnu()
    }