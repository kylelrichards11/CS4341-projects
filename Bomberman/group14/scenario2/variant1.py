# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../group14')
from scenario2_testcharacter import TestCharacter

# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character
g.add_character(TestCharacter("group14", # name
                              "C",  # avatar
                              0, 0  # position
))

# Run!
g.go()
