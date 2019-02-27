# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from pandas import *
import numpy as np
pandas.set_option('display.max_rows', 19)
pandas.set_option('display.max_columns', 8)
pandas.set_option('display.width', 1000)

class TestCharacter(CharacterEntity):

    exitReward = 1000
    deathReward = -1000
    bombTimer = None

    def do(self, wrld):
        # print("My Location: ", self.x, ", ", self.y)

        self.getManhattanDist(self.x, self.y, wrld)
        self.move(0, 0)

    def checkForNearbyMonster(self, wrld, i, j, a, b):
        for c in range(-1, 2):
            for d in range(-1, 2):
                if self.checkInWorldBounds(i + a + c, j + b + d, wrld) and not wrld.wall_at(i + a + c, j + b + d):
                    if wrld.monsters_at(i + a + c, j + b + d):
                        return True
        return False

    def getBombLocation(self, wrld):
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                if wrld.bomb_at(i, j):
                    return i, j
        return None, None

    def isInExplodeRange(self, x, y, wrld):
        bombLoc = self.getBombLocation(wrld)
        if bombLoc[0] is None:
            return False

        if x < (bombLoc[0] + wrld.expl_range) and x > (bombLoc[0] - wrld.expl_range) and y == bombLoc[1]:
            return True

        if y < (bombLoc[1] + wrld.expl_range) and y > (bombLoc[1] - wrld.expl_range) and x == bombLoc[0]:
            return True

        return False

    def checkInWorldBounds(self, x, y, wrld):
        if x >= 0 and x < wrld.width() and y >=0 and y < wrld.height():
            return True
        return False


    def getExitLoc(self, wrld):
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                if wrld.exit_at(i, j):
                    return i, j

    def getEuclideanDist(self, x, y, wrld):
        exit_x, exit_y = self.getExitLoc(x, y, wrld)
        return np.sqrt(((x - exit_x) ^ 2) + ((y - exit_y) ^ 2))

    def getManhattanDist(self, x, y, wrld):

        h1 = [[1000 for i in range(wrld.width())] for j in range(wrld.height())]
        h2 = [[1000 for i in range(wrld.width())] for j in range(wrld.height())]

        exit_x, exit_y = self.getExitLoc(wrld)

        h1[exit_y][exit_x] = 0
        h2[exit_y][exit_x] = 0

        h = [h1, h2]

        h_index = 0

        for k in range(0, 1):
            for i in range(wrld.width()):
                for j in range(wrld.height()):
                    if not wrld.wall_at(i, j) and not wrld.exit_at(i, j):
                        min = None
                        for a in range(-1, 2):
                            for b in range(-1, 2):
                                if self.checkInWorldBounds(i + a, j + b, wrld):
                                    if not wrld.wall_at(i + a, j + b):
                                        v = h[h_index][j][i]
                                        if min is None:
                                            min = v
                                        else:
                                            if v < min:
                                                min = v

                        h[self.getOtherIndex(h_index)][j][i] = min + 1

            h_index = self.getOtherIndex(h_index)

        print(DataFrame(h[h_index]))

        return h[h_index][y][x]

    def getOtherIndex(self, idx):
        if idx == 0:
            return 1
        else:
            return 0


