# capsule.py
# ----------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from events import Event
import pacman
import util

class Capsule:
    """
    An abstract class for a power pellet.
    NOTE:  Any instance information can only be added in the __init__
    method and can never be mutated afterwards.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getPosition(self):
        return self.x, self.y

    def deepCopy(self):
        util.raiseNotDefined()

    def __eq__(self, other):
        util.raiseNotDefined()

    def __hash__(self):
        util.raiseNotDefined()


    def performAction(self, state):
        """
        Called when an agent eats the capsule.  The capsule has
        already been removed from the state.
        """
        util.raiseNotDefined()

class ScareCapsule(Capsule):

    def performAction(self, state):
        # Start at 1 to skip Pacman
        for i in range(1, len(state.data.agentStates)):
            ghost = state.data.agentStates[i]
            ghost.scaredTimer = pacman.SCARED_TIME

    def deepCopy(self):
        return ScareCapsule(self.x, self.y)

    def __hash__(self):
        return hash( (self.x, self.y) )

    def __eq__(self, other):
        return isinstance(other, ScareCapsule) and \
            self.x == other.x and self.y == other.y


class WallCapsule(Capsule):
    def __init__(self, x, y, wallPositions, time):
        Capsule.__init__(self, x, y)
        self.wallPositions = tuple(wallPositions)
        self.timeForWalls = time

    def performAction(self, state):
        agentPositions = [s.getPosition() for s in state.data.agentStates]
        for x, y in self.wallPositions:
            if (x, y) not in agentPositions:
                state.data.walls[x][y] = True
                state.data.timedWalls[(x, y)] = self.timeForWalls
                state.data._wallsChanged.append((x, y))

    def deepCopy(self):
        return WallCapsule(self.x, self.y, self.wallPositions, self.timeForWalls)

    def __hash__(self):
        return hash( (self.x, self.y, self.wallPositions, self.timeForWalls) )

    def __eq__(self, other):
        return isinstance(other, WallCapsule) and \
            self.x == other.x and self.y == other.y and \
            self.wallPositions == other.wallPositions and \
            self.timeForWalls == other.timeForWalls

DefaultCapsule = ScareCapsule
