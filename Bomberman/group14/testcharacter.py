# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from pandas import *

class TestCharacter(CharacterEntity):

    exitX = None
    exitY = None

    monsX = None
    monsY = None

    def do(self, wrld):
        if self.exitX is None:
            self.exitX, self.exitY = self.findExit(wrld)

        if self.monsX is None:
            self.monsX, self.monsY = self.findMonsters(wrld)

        print("My Location: ", self.x, ", ", self.y)
        print("Exit Location: ", self.exitX, ", ", self.exitY)
        print("Monsters Location: ", self.monsX, self.monsY)

        policy = [[(0, 0, 0) for i in range(wrld.width())] for j in range(wrld.height())]

        # Value Iteration?
        for k in range(0, 1):
            # print("Level", k)
            for i in range(0, wrld.width()):
                for j in range(0, wrld.height()):
                    max = None
                    bestA = None
                    bestB = None
                    for a in range(-1, 2):
                        for b in range(-1, 2):
                            if not (a == 0 and b == 0):
                                if i + a < wrld.width() and i + a >= 0 and j + b < wrld.height() and j + b >= 0 and (wrld.monsters_at(i + a, j + b) or wrld.characters_at(i + a, j + b) or wrld.exit_at(i + a, j + b) or wrld.empty_at(i + a, j + b)):
                                    #print("Found move at", i+a, j+b)
                                    if i+a == self.exitX and j+b == self.exitY:
                                        reward = 100
                                    elif wrld.monsters_at(i + a, j + b):
                                        print("Monster At", i+a,j+b)
                                        reward = -1000
                                    else:
                                        reward = -1

                                    p = policy[j + b][i + a]
                                    v = p[2] + reward

                                    if max is None:
                                        max = v
                                        bestA = a
                                        bestB = b
                                    else:
                                        if v > max + reward:
                                            max = v
                                            bestA = a
                                            bestB = b

                    policy[j][i] = (bestA, bestB, max)

        for i in policy:
            print(*i, sep="\t\t")

        # Choose best move
        # print("Im at", self.x, self.y)
        p = policy[self.y][self.x]
        # print("Im going to", p[0], p[1])
        self.move(p[0], p[1])

    def findExit(self, wrld):
        for i in range(0, wrld.width()):
            for j in range(0, wrld.height()):
                if wrld.exit_at(i, j):
                    return i, j

    def findMonsters(self, wrld):
        for i in range(0, wrld.width()):
            for j in range(0, wrld.height()):
                if wrld.monsters_at(i, j):
                    return i, j
