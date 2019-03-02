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

    exitReward = 1000
    monsterReward = -1000
    explosionReward = -1100
    bombTimer = None

    def do(self, wrld):
        # print("My Location: ", self.x, ", ", self.y)

        # Initialize Policy Matrices
        policy1 = [[(0, 0, 0) for i in range(wrld.width())] for j in range(wrld.height())]
        policy2 = [[(0, 0, 0) for i in range(wrld.width())] for j in range(wrld.height())]
        policies = [policy1, policy2]
        policyIndex = 1

        if self.getBombLocation(wrld) is None:
            self.bombTimer = None

        nextToWall = False

        # Good ol' Value Iteration?
        checkForMons = False
        for a in range (-3, 4):
            for b in range (-3, 4):
                if self.checkForNearbyMonster(wrld, self.x, self.y, a, b) is not None:
                    checkForMons = True

        monsterGrid = None


        if checkForMons:
            monsterGrid = [[(False, 0, 0) for i in range(wrld.width())] for j in range(wrld.height())]
            for i in range(wrld.width()):
                for j in range(wrld.height()):
                    monsterFound = False
                    xDir = None
                    yDir = None
                    for c in range(-2, 3):
                        for d in range(-2, 3):
                            if self.checkInWorldBounds(i+c, j+d, wrld):
                                if wrld.monsters_at(i + c, j + d):
                                    monsterFound = True
                                    if c < 0:
                                        xDir = 1
                                    else:
                                        xDir = -1
                                    if d < 0:
                                        yDir = 1
                                    else:
                                        yDir = -1
                    monsterGrid[j][i] = (monsterFound, xDir, yDir)

        #print("Monster Grid:")
        #print(DataFrame(monsterGrid))

        # Iterate 50 times
        for k in range(0, 21):
            # print("\nLevel", k)

            # For each cell in the world
            for i in range(0, wrld.width()):
                for j in range(0, wrld.height()):
                    max = None
                    bestA = None
                    bestB = None
                    nextToExit = False
                    deathFound = False

                    shouldprint = False
                    #if i==7 and j==6:
                    #    shouldprint = True

                    # Look at adjacent cells
                    for a in range(-1, 2):
                        for b in range(-1, 2):

                            # Ignore the current cell, the exit cell, and cells that are walls
                            # if not (a == 0 and b == 0) and not wrld.exit_at(i, j) and not wrld.wall_at(i, j):
                            if not wrld.exit_at(i, j) and not wrld.wall_at(i, j):
                                if self.checkInWorldBounds(i+a, j+b, wrld):
                                    if not wrld.wall_at(i+a, j+b):
                                        if shouldprint:
                                            print("Checking", i+a, j+b)

                                        # If we are next to the exit, go to the exit
                                        if wrld.exit_at(i+a, j+b):
                                            bestA = a
                                            bestB = b
                                            max = self.exitReward - 1
                                            nextToExit = True

                                        # If the bomb will explode soon check if we are near it
                                        if self.bombTimer is not None and self.bombTimer < 2:
                                            if self.isInExplodeRange(i, j, wrld):
                                                max = self.explosionReward
                                                deathFound = True

                                        # Check for explosion cells
                                        if wrld.explosion_at(i, j):
                                            max = self.explosionReward
                                            deathFound = True

                                        # Check for nearby monsters
                                        if checkForMons:
                                            mons = monsterGrid[j+b][i+a]
                                            if mons[0]:
                                                deathFound = True
                                                max = self.monsterReward
                                                if bestA is None:
                                                    bestA = mons[1]
                                                if bestB is None:
                                                    bestB = mons[2]
                                                if wrld.explosion_at(i+bestA, j+bestB):
                                                    bestA = 0
                                                    bestB = 0

                                        # If we are not next to the exit, find the best cell to go to
                                        if not nextToExit:
                                            reward = -(wrld.height() - j)
                                            p = policies[self.getPreviousPolicyIndex(policyIndex)][j + b][i + a]
                                            v = p[2] + reward

                                            if max is None:
                                                max = v
                                                bestA = a
                                                bestB = b
                                            else:
                                                if v > max + reward:
                                                    if not deathFound:
                                                        max = v
                                                    bestA = a
                                                    bestB = b

                                            if shouldprint:
                                                print(max, bestA, bestB)

                                    # If there is a wall at this spot (from else) and we are at this i, j, then we are next to a wall
                                    elif i == self.x and j == self.y and a == 0:
                                        nextToWall = True

                            # If this is the exit cell, set the reward appropriately
                            elif wrld.exit_at(i, j):
                                bestA = 0
                                bestB = 0
                                max = self.exitReward


                    # Update the policy matrix
                    policies[policyIndex][j][i] = (bestA, bestB, max)

            # Switch to other policy matrix
            policyIndex = self.getPreviousPolicyIndex(policyIndex)

        # Print the final policy matrix after 50 iterations
        #print("\nPrev")
        #print(DataFrame(policies[self.getPreviousPolicyIndex(policyIndex)]))
        print("\nCurrent")
        print(DataFrame(policies[policyIndex]))

        # If we are near a monster or next to a wall place a bomb
        if policies[policyIndex][self.y][self.x][2] < self.monsterReward - 1 or nextToWall:
            if self.getBombLocation(wrld) is None:
                self.place_bomb()
                self.bombTimer = wrld.bomb_time

        # If there is a bomb, decrease the timer by 1
        if self.bombTimer is not None:
            self.bombTimer = self.bombTimer - 1

        print("Bomb Time = ", self.bombTimer)
        print("Explode Range = ", wrld.expl_range)
        print("Explode at? = ", wrld.explosion_at(2, 2))

        # Choose best move
        # print("Im at", self.x, self.y)
        p = policies[policyIndex][self.y][self.x]
        cantMoveX = False
        cantMoveY = False
        print("Move: ", p[0], p[1])
        if self.checkInWorldBounds(p[0] + self.x, p[1]+self.y, wrld) and not wrld.wall_at(self.x + p[0], self.y + p[1]):
            print("In Bounds")
            self.move(p[0], p[1])
        else:
            if (self.x + p[0]) >= wrld.width() or (p[0] + self.x) < 0 or wrld.wall_at(p[0] + self.x, self.y):
                print("Can't move X")
                cantMoveX = True
            if (self.y + p[1]) >= wrld.height() or (self.y + p[1]) < 0 or wrld.wall_at(self.x, p[1] + self.y):
                print("Cant move Y")
                cantMoveY = True

            if cantMoveX and not cantMoveY:
                print("Move: ", 0, p[1])
                self.move(0, p[1])
            elif cantMoveY and not cantMoveX:
                print("Move: ", p[0], 0)
                self.move(p[0], 0)
            elif cantMoveX and cantMoveY:
                #monsterat = self.getMonsterLocations(wrld)
                #if monsterat is not None and abs(self.x-monsterat[0] > (self.y - monsterat[1])): #TODO CHANGED getMonsterLocations
                #    print("Move: ", 0, -p[1])
                #    self.move(0, -p[1])
                #elif monsterat is not None and abs(self.y - monsterat[1]) > (self.x - monsterat[0]):
                #    print("Move: ", -p[0], 0)
                #    self.move(-p[0], 0)
                self.move(0, 0)



        # print("My direction is", p[0], p[1])
        #self.move(p[0], p[1])

    def checkForMonster(self, wrld, i, j, a, b):
        for c in range(-3, 4):
            for d in range(-3, 4):
                if self.checkInWorldBounds(i + a + c, j + b + d, wrld) and not wrld.wall_at(i + a + c, j + b + d):
                    if wrld.monsters_at(i + a + c, j + b + d):
                        if a+c < 0:
                            xDir = -1
                        else:
                            xDir = 1

                        if b+d < 0:
                            yDir = -1
                        else:
                            yDir = 1
                        return xDir,yDir
        return None

    def checkForNearbyMonster(self, wrld, i, j, a, b):
        for c in range(-2, 3):
            for d in range(-2, 3):
                if self.checkInWorldBounds(i + a + c, j + b + d, wrld) and not wrld.wall_at(i + a + c, j + b + d):
                    if wrld.monsters_at(i + a + c, j + b + d):
                        if a+c < 0:
                            xDir = 1
                        else:
                            xDir = -1

                        if b+d < 0:
                            yDir = 1
                        else:
                            yDir = -1
                        return xDir,yDir
        return None



    def getBombLocation(self, wrld):
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                if wrld.bomb_at(i, j):
                    return i, j
        return None

    def getMonsterLocations(self, wrld):
        monsters = []
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                if wrld.monsters_at(i, j):
                    monsters.append((i, j))
        return monsters

    def isInExplodeRange(self, x, y, wrld):
        bombLoc = self.getBombLocation(wrld)
        if bombLoc is None:
            return False

        if x < (bombLoc[0] + wrld.expl_range) and x > (bombLoc[0] - wrld.expl_range) and y == bombLoc[1]:
            return True

        if y < (bombLoc[1] + wrld.expl_range + 1) and y > (bombLoc[1] - wrld.expl_range - 1) and x == bombLoc[0]:
            return True

        return False

    def checkInWorldBounds(self, x, y, wrld):
        if x >= 0 and x < wrld.width() and y >=0 and y < wrld.height():
            return True
        return False

    def getPreviousPolicyIndex(self, idx):
        if idx == 0:
            return 1
        else:
            return 0
