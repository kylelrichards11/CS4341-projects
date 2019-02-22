# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from pandas import *
pandas.set_option('display.max_rows', 19)
pandas.set_option('display.max_columns', 8)
pandas.set_option('display.width', 1000)

class TestCharacter(CharacterEntity):

    exitReward = 100
    monsterReward = -100

    def do(self, wrld):
        # print("My Location: ", self.x, ", ", self.y)

        policy1 = [[(0, 0, 0) for i in range(wrld.width())] for j in range(wrld.height())]
        policy2 = [[(0, 0, 0) for i in range(wrld.width())] for j in range(wrld.height())]

        # Value Iteration?
        policies = [policy1, policy2]
        policyIndex = 1
        for k in range(0, 50):
            # print("Level", k)
            for i in range(0, wrld.width()):
                for j in range(0, wrld.height()):
                    max = None
                    bestA = None
                    bestB = None
                    for a in range(-1, 2):
                        for b in range(-1, 2):
                            if not (a == 0 and b == 0) and not wrld.exit_at(i, j) and not wrld.wall_at(i, j):
                                if i + a < wrld.width() and i + a >= 0 and j + b < wrld.height() and j + b >= 0 and not wrld.wall_at(i+a, j+b):
                                    #print("Found move at", i+a, j+b)
                                    if wrld.exit_at(i+a, j+b):
                                        bestA = a
                                        bestB = b
                                        max = self.exitReward - 1
                                    elif wrld.monsters_at(i + a, j + b):
                                        # print("Monster At", i+a,j+b)
                                        bestA = 0
                                        bestB = 0
                                        max = self.monsterReward
                                    else:
                                        reward = -1

                                        if policyIndex == 0:
                                            prevPolicyIndex = 1
                                        else:
                                            prevPolicyIndex = 0

                                        p = policies[prevPolicyIndex][j + b][i + a]
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
                            elif wrld.exit_at(i, j):
                                    bestA = 0
                                    bestB = 0
                                    max = self.exitReward

                    policies[policyIndex][j][i] = (bestA, bestB, max)

            if policyIndex == 0:
                policyIndex = 1
            else:
                policyIndex = 0

        print(DataFrame(policies[policyIndex]))

        # Choose best move
        # print("Im at", self.x, self.y)
        p = policies[policyIndex][self.y][self.x]
        # print("My direction is", p[0], p[1])
        self.move(p[0], p[1])
