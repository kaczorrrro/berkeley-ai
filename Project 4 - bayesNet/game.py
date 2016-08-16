# game.py
# -------
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


# game.py
# -------
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


# game.py
# -------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import *
import time, os
import traceback
import sys
import powersBayesNet

#######################
# Parts worth reading #
#######################

# TODO: A lot of this class should be refactored into a table of
# constants, so that it is more generic
class AgentPowers:
    def __init__(self, powerDict={}):
        laser = int(powerDict.get('laser', 0))
        assert laser >= 0 and laser <= 2
        speed = float(powerDict.get('speed', 1.0))
        assert speed > 0 and speed <= 4
        blast = int(powerDict.get('blast', 0))
        assert blast >= 0 and blast <= 2

        self.laser = laser
        self.timestepsBetweenMoves = (1.0 / speed)
        self.blast = blast

    def makePowersFromChoice(powerChoiceDict):
        laser = int(powerChoiceDict.get('laser', 0))
        speed = int(powerChoiceDict.get('speed', 0))
        blast = int(powerChoiceDict.get('blast',0))
        assert laser >= 0 and blast>=0 and speed>=0 and (laser+blast+speed)<=1
        if(laser):
            laser = 2 #default is full power
        if(blast):
            blast = 2
        speed = speed+1
        return AgentPowers({'laser':laser,'speed':speed,'blast':blast})
    makePowersFromChoice = staticmethod(makePowersFromChoice)

    def hasNoPowers(self):
        return self.laser == 0 and self.blast == 0 and \
            self.timestepsBetweenMoves == 1.0

    def copy(self):
        result = AgentPowers()
        result.laser = self.laser
        result.timestepsBetweenMoves = self.timestepsBetweenMoves
        result.blast = self.blast
        return result

class AgentObservedVariables:
    def __init__(self,size=1,backpack=0):
        self.size = size
        self.backpack = backpack

    def copy(self):
        return AgentObservedVariables(self.size,self.backpack)

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # Inspects the starting state
    def getPowers(self, state, limit): # Chooses powers (eg. laser, blast, speed)
    """
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        raiseNotDefined()

class Directions:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'
    LASER = 'Laser'
    BLAST = 'Blast'

    LEFT =       {NORTH: WEST,
                   SOUTH: EAST,
                   EAST:  NORTH,
                   WEST:  SOUTH,
                   LASER: LASER,
                   BLAST: BLAST,
                   STOP:  STOP}

    RIGHT =      dict([(y,x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               LASER: LASER,
               BLAST: BLAST,
               STOP: STOP}

    asVector = {NORTH: (0, 1),
                   SOUTH: (0, -1),
                   EAST:  (1, 0),
                   WEST:  (-1, 0),
                   LASER:  (0, 0),
                   BLAST: (0,0),
                   STOP:  (0, 0)}

class Configuration:
    """
    A Configuration holds the (x,y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, north is the direction of increasing y, or (0,1).
    """

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def getPosition(self):
        return (self.pos)

    def getDirection(self):
        return self.direction

    def isInteger(self):
        x,y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other):
        if other == None: return False
        return (self.pos == other.pos and self.direction == other.direction)

    def __hash__(self):
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        return "(x,y)="+str(self.pos)+", "+str(self.direction)

    def generateSuccessor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP or direction == Directions.LASER or direction == Directions.BLAST:
            direction = self.direction # There is no stop direction
        return Configuration((x + dx, y+dy), direction)

class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__( self, startConfiguration, isPacman, powers):
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isPacman = isPacman
        self.scaredTimer = 0
        self.numCarrying = 0
        self.numReturned = 0
        self.powers = AgentPowers(powers)
        self.observedVars = AgentObservedVariables()

    def __str__( self ):
        if self.isPacman:
            return "Pacman: " + str( self.configuration )
        else:
            return "Ghost: " + str( self.configuration )

    def __eq__( self, other ):
        if other == None:
            return False
        return self.configuration == other.configuration and self.scaredTimer == other.scaredTimer

    def __hash__(self):
        return hash(hash(self.configuration) + 13 * hash(self.scaredTimer))

    def copy( self ):
        state = AgentState( self.start, self.isPacman, {} )
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        state.powers = self.powers.copy()
        state.observedVars = self.observedVars.copy()

        return state

    def getPosition(self):
        if self.configuration == None: return None
        return self.configuration.getPosition()

    def getDirection(self):
        return self.configuration.getDirection()

    def getLaserPower(self):
        return self.powers.laser

    def getBlastPower(self):
        return self.powers.blast

    def getSpeed(self):
        return 1.0/self.powers.timestepsBetweenMoves

class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.  Data is accessed
    via grid[x][y] where (x,y) are positions on a Pacman map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented like a pacman board.
    """
    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other == None: return False
        return self.data == other.data

    def __hash__(self):
        # return hash(str(self))
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item =True ):
        return sum([x.count(item) for x in self.data])

    def asList(self, key = True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append( (x,y) )
        return list

    def packBits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index):
        x = index / self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed, size):
        bools = []
        if packed < 0: raise ValueError, "must be a positive integer"
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools

def reconstituteGrid(bitRep):
    if type(bitRep) is not type((1,2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation= bitRep[2:])

####################################
# Parts you shouldn't have to read #
####################################

class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST:  (1, 0),
                   Directions.WEST:  (-1, 0),
                   Directions.LASER:  (0, 0),
                   Directions.BLAST:  (0, 0),
                   Directions.STOP:  (0, 0)}

    _directionsAsList = _directions.items()

    TOLERANCE = .001

    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action
    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP
    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction, speed = 1.0):
        dx, dy =  Actions._directions[direction]
        return (dx * speed, dy * speed)
    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if (abs(x - x_int) + abs(y - y_int)  > Actions.TOLERANCE):
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position, walls):
        x,y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width: continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height: continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors
    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)
    getSuccessor = staticmethod(getSuccessor)

class GameStateData:
    """

    """
    def __init__( self, prevState = None ):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.food = prevState.food.shallowCopy()
            self.walls = prevState.walls.shallowCopy()
            self.timedWalls = prevState.timedWalls.copy()
            self.capsules = [cap.deepCopy() for cap in prevState.capsules]
            self.agentStates = self.copyAgentStates( prevState.agentStates )
            self.layout = prevState.layout
            self._eaten = prevState._eaten
            self.score = prevState.score
            self.time = prevState.time

        self._lose = False
        self._win = False
        self.resetChangeData()

    def resetChangeData( self ):
        self._foodEaten = None
        self._foodAdded = None
        self._capsuleEaten = None
        self._wallsChanged = []
        self._agentMoved = None
        self._timeTillAgentMovesAgain = None
        self._action = None
        self.scoreChange = 0

    def deepCopy( self ):
        state = GameStateData( self )
        state.food = self.food.deepCopy()
        state.walls = self.walls.deepCopy()
        # timedWalls, capsules have already been sufficiently copied
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._timeTillAgentMovesAgain = self._timeTillAgentMovesAgain
        state._action = self._action
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        state._wallsChanged = self._wallsChanged[:]
        return state


    def copyAgentStates( self, agentStates ):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append( agentState.copy() )
        return copiedStates

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        if other == None: return False
        # TODO Check for type of other
        if not self.agentStates == other.agentStates: return False
        if not self.food == other.food: return False
        if not self.walls == other.walls: return False
        if not self.timedWalls == other.timedWalls: return False
        if not self.capsules == other.capsules: return False
        if not self.score == other.score: return False
        if not self.time == other.time: return False
        return True

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate( self.agentStates ):
            try:
                int(hash(state))
            except TypeError, e:
                print e
                #hash(state)
        return int((hash(tuple(self.agentStates)) + 13*hash(self.food) + 13*hash(self.walls) + 17*hash(tuple(self.timedWalls.items())) + 113* hash(tuple(self.capsules)) + 7 * hash(self.score) + 11 * hash(self.time)) % 1048575 )

    def __str__( self ):
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if type(self.food) == type((1,2)):
            self.food = reconstituteGrid(self.food)
        for x in range(width):
            for y in range(height):
                food, walls = self.food, self.walls
                map[x][y] = self._foodWallStr(food[x][y], walls[x][y])

        for agentState in self.agentStates:
            if agentState == None: continue
            if agentState.configuration == None: continue
            x,y = [int( i ) for i in nearestPoint( agentState.configuration.pos )]
            agent_dir = agentState.configuration.direction
            if agentState.isPacman:
                map[x][y] = self._pacStr( agent_dir )
            else:
                map[x][y] = self._ghostStr( agent_dir )

        #for x, y in self.capsules:
        #    map[x][y] = 'o'

        return str(map) + ("\nScore: %d\n" % self.score)

    def _foodWallStr( self, hasFood, hasWall ):
        if hasFood:
            return '.'
        elif hasWall:
            return '%'
        else:
            return ' '

    def _pacStr( self, dir ):
        if dir == Directions.NORTH:
            return 'v'
        if dir == Directions.SOUTH:
            return '^'
        if dir == Directions.WEST:
            return '>'
        return '<'

    def _ghostStr( self, dir ):
        return 'G'
        if dir == Directions.NORTH:
            return 'M'
        if dir == Directions.SOUTH:
            return 'W'
        if dir == Directions.WEST:
            return '3'
        return 'E'

    def initialize( self, layout, pacmanPowers, ghostPowers, numGhostAgents ):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.food = layout.food.deepCopy()
        self.walls = layout.walls.deepCopy()
        self.timedWalls = {}
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0
        self.time = 0
        #print ghostPowers

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            powers = {}
            if isPacman:
                powers = pacmanPowers
            else:
                if numGhosts == numGhostAgents:
                    continue # Max ghosts reached already
                else:
                    if ghostPowers != []:
                        if(numGhosts >= len(ghostPowers)):
                            powers = ghostPowers[0] #for now, we assign same power to all ghosts
                        else:
                            powers = ghostPowers[numGhosts]
                    numGhosts += 1
            config = Configuration(pos, Directions.STOP)
            self.agentStates.append( AgentState(config, isPacman, powers) )
        self._eaten = [False for a in self.agentStates]

try:
    import boinc
    _BOINC_ENABLED = True
except:
    _BOINC_ENABLED = False

class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """

    def __init__( self, agents, powerLimit, display, rules, muteAgents=False, catchExceptions=False ):
        self.agentCrashed = False
        self.agents = agents
        self.powerLimit = powerLimit
        self.display = display
        self.rules = rules
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.actualGhostPowers = None
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        self.pbNet = powersBayesNet.PowersBayesNet()
        import cStringIO
        self.agentOutput = [cStringIO.StringIO() for agent in agents]

    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash( self, agentIndex, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet: traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash(self, agentIndex)

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        import cStringIO
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        if not self.muteAgents: return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def initializeGhostPowers(self):
        """
        Agent powers provided in the command line are already parsed
        and present in the state.  If no powers were provided, then
        the agent has a chance to choose them itself.
        """

        for i in range(len(self.agents)):
            agentState = self.state.data.agentStates[i]
            if not(agentState.isPacman):
                if not agentState.powers.hasNoPowers():
                    self.actualGhostPowers = agentState.powers
                    
        if(not self.actualGhostPowers):
            powerDict = Counter()
            powerDict['laser']=1
            powerDict['speed']=1
            powerDict['blast']=1
            powerChoiceDict = {}
            choice = chooseFromDistribution(powerDict)
            print "Ghosts chose : " + choice
            powerChoiceDict[choice]=1
            self.actualGhostPowers = AgentPowers.makePowersFromChoice(powerChoiceDict)

        power = None
        #print self.actualGhostPowers.timestepsBetweenMoves
        if(self.actualGhostPowers.laser):
            power = 'laser'
        elif(self.actualGhostPowers.blast):
            power = 'blast'
        elif (self.actualGhostPowers.timestepsBetweenMoves < 1) :
            power = 'speed'
        self.observedVarsAssignmentDict = self.pbNet.instantiateObservableVars(power)

        for i in range(len(self.agents)):
            agentState = self.state.data.agentStates[i]
            if not(agentState.isPacman):
                if agentState.powers.hasNoPowers():
                    agentState.powers = self.actualGhostPowers  

    def initializePacmanPowers(self):
        """
        Agent powers provided in the command line are already parsed
        and present in the state.  If no powers were provided, then
        the agent has a chance to choose them itself.
        """
        for i in range(len(self.agents)):
            agent = self.agents[i]
            agentState = self.state.data.agentStates[i]
            ghostPowers = self.actualGhostPowers
            if(agentState.isPacman):
                if 'getPowerChoice' in dir(agent) and agentState.powers.hasNoPowers():
                    inferredGhostPowers = self.pbNet.inferGhostPowers(self.observedVarsAssignmentDict)
                    powerChoiceDict = agent.getPowerChoice(inferredGhostPowers)
                    #print powerChoiceDict
                    powers = AgentPowers.makePowersFromChoice(powerChoiceDict)

                    ## penalize if power same as ghost
                    if(self.actualGhostPowers.laser and powers.laser==2):
                        powers.laser = 1
                    if(self.actualGhostPowers.blast and powers.blast==2):
                        powers.blast = 1
                    agentState.powers = powers

    def initializeAgentObservedVars(self):
        #print self.observedVarsAssignmentDict
        gSize = 1 - 0.2*(self.observedVarsAssignmentDict['Size']=='small')
        belt = (self.observedVarsAssignmentDict['Belt']=='1')
        #print(gSize,belt)
        for i in range(len(self.agents)):
            agent = self.agents[i]
            s = self.state.data.agentStates[i]
            if s.isPacman :
                agentStr = "Pacman"
            else :
                agentStr = "Ghost"
            #print "Enter (size,backpack) for " + agentStr + " at position " + str(s.getPosition())
            if s.isPacman:
                s.observedVars = AgentObservedVariables(1,0)
            else:
                s.observedVars = AgentObservedVariables(gSize,belt) #(size,backpack)

    def informAgentsOfGameStart(self):
        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                # this is a null agent, meaning it failed to load
                # the other team wins
                print >>sys.stderr, "Agent %d failed to load" % i
                self.unmute()
                self._agentCrash(i, quiet=True)
                return False
            if ("registerInitialState" in dir(agent)):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime(i)))
                        try:
                            start_time = time.time()
                            timed_func(self.state.deepCopy())
                            time_taken = time.time() - start_time
                            self.totalAgentTimes[i] += time_taken
                        except TimeoutFunctionException:
                            print >>sys.stderr, "Agent %d ran out of time on startup!" % i
                            self.unmute()
                            self.agentTimeout = True
                            self._agentCrash(i, quiet=True)
                            return False
                    except Exception,data:
                        self._agentCrash(i, quiet=False)
                        self.unmute()
                        return False
                else:
                    agent.registerInitialState(self.state.deepCopy())
                ## TODO: could this exceed the total time
                self.unmute()
        return True

    def getAgentAction(self, agentIndex):
        # Fetch the next agent
        agent = self.agents[agentIndex]
        move_time = 0
        skip_action = False
        # Generate an observation of the state
        if 'observationFunction' in dir( agent ):
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout(agentIndex)))
                    try:
                        start_time = time.time()
                        observation = timed_func(self.state.deepCopy())
                    except TimeoutFunctionException:
                        skip_action = True
                    move_time += time.time() - start_time
                    self.unmute()
                except Exception,data:
                    self._agentCrash(agentIndex, quiet=False)
                    self.unmute()
                    return False
            else:
                observation = agent.observationFunction(self.state.deepCopy())
            self.unmute()
        else:
            observation = self.state.deepCopy()

        # Solicit an action
        action = None
        self.mute(agentIndex)
        if self.catchExceptions:
            try:
                timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout(agentIndex)) - int(move_time))
                try:
                    start_time = time.time()
                    if skip_action:
                        raise TimeoutFunctionException()
                    action = timed_func( observation )
                except TimeoutFunctionException:
                    print >>sys.stderr, "Agent %d timed out on a single move!" % agentIndex
                    self.agentTimeout = True
                    self._agentCrash(agentIndex, quiet=True)
                    self.unmute()
                    return False

                move_time += time.time() - start_time

                if move_time > self.rules.getMoveWarningTime(agentIndex):
                    self.totalAgentTimeWarnings[agentIndex] += 1
                    print >>sys.stderr, "Agent %d took too long to make a move! This is warning %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex])
                    if self.totalAgentTimeWarnings[agentIndex] > self.rules.getMaxTimeWarnings(agentIndex):
                        print >>sys.stderr, "Agent %d exceeded the maximum number of warnings: %d" % (agentIndex, self.totalAgentTimeWarnings[agentIndex])
                        self.agentTimeout = True
                        self._agentCrash(agentIndex, quiet=True)
                        self.unmute()
                        return False

                self.totalAgentTimes[agentIndex] += move_time
                #print "Agent: %d, time: %f, total: %f" % (agentIndex, move_time, self.totalAgentTimes[agentIndex])
                if self.totalAgentTimes[agentIndex] > self.rules.getMaxTotalTime(agentIndex):
                    print >>sys.stderr, "Agent %d ran out of time! (time: %1.2f)" % (agentIndex, self.totalAgentTimes[agentIndex])
                    self.agentTimeout = True
                    self._agentCrash(agentIndex, quiet=True)
                    self.unmute()
                    return False
                self.unmute()
            except Exception,data:
                self._agentCrash(agentIndex)
                self.unmute()
                return False
        else:
            action = agent.getAction(observation)
        self.unmute()
        return True, action

    def getAndRunAgentAction(self, agentIndex):
        actionTuple = self.getAgentAction(agentIndex)
        if not actionTuple:
            return False
        _, action = actionTuple

        # Execute the action
        self.moveHistory.append( (agentIndex, action) )
        if self.catchExceptions:
            try:
                self.state = self.state.generateSuccessor( action )
            except Exception,data:
                self.mute(agentIndex)
                self._agentCrash(agentIndex)
                self.unmute()
                return False
        else:
            self.state = self.state.generateSuccessor( action )
        return True

    def informLearningAgents(self):
        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir( agent ) :
                try:
                    self.mute(agentIndex)
                    agent.final( self.state )
                    self.unmute()
                except Exception,data:
                    if not self.catchExceptions: raise
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return False
        return True

    def run( self ):
        """
        Main control loop for game play.
        """
        self.initializeGhostPowers()
        self.initializeAgentObservedVars()
        self.initializePacmanPowers()
        self.display.initialize(self.state.data)
        self.numMoves = 0

        ###self.display.initialize(self.state.makeObservation(1).data)
        if not self.informAgentsOfGameStart():
            return

        agentIndex = self.state.getNextAgentIndex()
        numAgents = len( self.agents )

        while not self.gameOver:
            event = self.state.getNextEvent()
            if event.isAgentMove():
                agentIndex = event.getAgentIndex()
                if not self.getAndRunAgentAction(agentIndex):
                    return
                self.numMoves += 1
            else:
                self.runEvent()

            # Change the display
            self.display.update(self.state.data)

            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)

            if _BOINC_ENABLED:
                boinc.set_fraction_done(self.getProgress())

        if not self.informLearningAgents():
            return
        self.display.finish()
