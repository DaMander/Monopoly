import random
from board import Board
from player import Player


def dice_roll():
    dice1 = random.randint(1,6)
    dice2 = random.randint(1,6)
    n = True if dice1 == dice2 else False
    return 1,n

def jail():
    pass


def past_go():
    pass