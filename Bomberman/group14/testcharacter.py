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
    manhattanGrid = None
    bombPlaces = None


    def do(self, wrld):
        # print("My Location: ", self.x, ", ", self.y)

        if self.manhattanGrid is None:
            self.manhattanGrid = self.generateManhattan(wrld)

        if self.bombPlaces is None:
            self.bombPlaces = self.getBombPlaces(wrld)

        if self.bombPlaces is not None:
            for b in self.bombPlaces:
                if b[0] == self.x and b[1] == self.y:
                    self.place_bomb()

        monsterLocations = self.findAllMonsters(wrld)

        gridCopy = [[0 for i in range(wrld.width())] for j in range(wrld.height())]
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                gridCopy[j][i] = self.manhattanGrid[j][i]


        for m in monsterLocations:
            for k in range(1, 4):
                for a in range(-1*k, k + 1):
                    for b in range(-1*k, k + 1):
                        if self.checkInWorldBounds(m[0] + a, m[1] + b, wrld):
                            gridCopy[m[1] + b][m[0] + a] = gridCopy[m[1] + b][m[0] + a] + 4


        print(DataFrame(gridCopy))
        print(DataFrame(self.manhattanGrid))

        min = None
        for a in range(-1, 2):
            for b in range(-1, 2):
                if self.checkInWorldBounds(self.x + a, self.y + b, wrld) and not (a == 0 and b == 0):
                    v = gridCopy[self.y + b][self.x + a]
                    if min is None or v < min:
                        min = v
                        bestA = a
                        bestB = b

        self.move(bestA, bestB)


    def monsterHeuristic(self, wrld, x, y):
        return

    def makeMonsterGrid(self, wrld, x, y):
        d = [[0 for i in range(wrld.width())] for j in range(wrld.height())]

        d[y][x] = 3

        for k in range(0, 3):
            for a in range(-1, 2):
                for b in range(-1, 2):
                    if self.checkInWorldBounds(x + a, y + b, wrld) and not (a == 0 and b == 0):
                        if not wrld.wall_at(x + a, y + b):
                            v = d[x + b][y + a]
                            if v == 0 or v > d[j][i] + 1:
                                d[j + b][i + a] = d[j][i] + 1




        print("Monster Grid")
        print(DataFrame(d))

        return d


    def checkForNearbyMonster(self, wrld, x, y):
        for a in range(-2, 3):
            for b in range(-2, 3):
                if self.checkInWorldBounds(x + a, y + b, wrld) and not wrld.wall_at(x + a, y + b):
                    if wrld.monsters_at(x + a, y + b):
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

    def generateManhattan(self, wrld):

        d = [[1000 for i in range(wrld.width())] for j in range(wrld.height())]

        e = self.getExitLoc(wrld)
        exitX = e[0]
        exitY = e[1]

        d[exitY][exitX] = 0

        if self.bombPlaces is not None:
            for b in self.bombPlaces:
                d[b[1]][b[0]] = 5

        for k in range(0, 20):
            for i in range(wrld.width()):
                for j in range(wrld.height()):
                    for a in range (-1, 2):
                        for b in range (-1, 2):
                            if self.checkInWorldBounds(i + a, j + b, wrld) and not (a == 0 and b == 0):
                                if not wrld.wall_at(i + a, j + b):
                                    v = d[j + b][i + a]
                                    if v > 999 or v > d[j][i] + 1:
                                        d[j + b][i + a] = d[j][i] + 1


        print(DataFrame(d))

        return d

    def getOtherIndex(self, idx):
        if idx == 0:
            return 1
        else:
            return 0


    def findAllMonsters(self, wrld):
        m = []
        for i in range (wrld.width()):
            for j in range (wrld.height()):
                if wrld.monsters_at(i, j):
                    m.append((i, j))
        return m

    def getBombPlaces(self, wrld):
        bombLocs = []
        for j in range(wrld.height()):
            x = wrld.width() - 1
            if wrld.wall_at(x, j):
                bombLocs.append((x, j-1))
        return bombLocs

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
