import random 

from config import *


def random_count(lst: list | int) -> list:
    if type(lst) == type([0, 1]):
        return random.randint(lst[0], lst[1])
    else:
        return lst 

def random_pattern() -> list:
    lst = []
    
    lst.extend(['dmail'] * random_count(USE_DMAIL)) 
    lst.extend(['aave'] * random_count(USE_AAVE))
    lst.extend(['mintfun'] * random_count(USE_MINTFUN))
    lst.extend(['zkstars'] * random_count(USE_ZKSTARS))
    lst.extend(['aero'] * random_count(USE_AERODROME))
    lst.extend(['baseswap'] * random_count(USE_BASESWAP))
    lst.extend(['maverick'] * random_count(USE_MAVERICK))
    lst.extend(['odos'] * random_count(USE_ODOS))
    lst.extend(['inch'] * random_count(USE_INCH))
    lst.extend(['pancake'] * random_count(USE_PANCAKE))
    lst.extend(['uniswap'] * random_count(USE_UNISWAP))
    lst.extend(['woofi'] * random_count(USE_WOOFI))
    lst.extend(['self_trans'] * random_count(SELF_TRANSACTIONS))
    
    random.shuffle(lst)
    
    return lst