import random
from board import Board
from player import Player


def dice_roll():
    dice1 = random.randint(1,6)
    dice2 = random.randint(1,6)
    n = True if dice1 == dice2 else False
    return dice1 +dice2,n

def jail():
    pass


