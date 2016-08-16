# powersBayesNet.py
# -----------------
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


# powersBayesNet.py
# --------------
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

from bayesNet import *
from inference import *
import testParser
import os

class PowersBayesNet(object):
    def __init__(self):
        """
        Constructor for a predefined BayesNet that dictates ghost powers.
        Main utilities are to :
        a) run inference and
        b) give samples of variables (size,belt,temperature,time,powers) to the game in accordance with desired powers
        """
        self.bayesNet = self.readPowerBayesNet()
        #print self.bayesNet

    def instantiateObservableVars(self,ghostPower):
        if(ghostPower == 'laser'):
            return self.LaserPowerObservarionDict()
        if(ghostPower == 'blast'):
            return self.BlastPowerObservarionDict()
        if(ghostPower == 'speed'):
            return self.SpeedPowerObservarionDict()
        return self.NullPowerObservarionDict()

    def readPowerBayesNet(self):
        netFile = os.path.join('.', 'powersBayesNet.txt')
        testDict = testParser.TestParser(netFile).parse()
        parseDict = parseBayesNetProblem(testDict)
        return parseDict['problemBayesNet']

    def constructPowerBayesNet(self):
        variableList = ['Time', 'Temp', 'L', 'E', 'S','Belt','Size']
        edgeTuplesList = ( [('Time', 'L'), ('Time', 'E'),
        ('Temp', 'L'),('Temp', 'E'),('Temp', 'S'),
        ('L', 'Belt'),('E','Belt'),
            ('E','Size'),('S','Size')] )
        variableDomainsDict = {}
        variableDomainsDict['Time'] = ['day','night']
        variableDomainsDict['Temp'] = ['hot','cold']
        variableDomainsDict['L'] = ['0','1']
        variableDomainsDict['E'] = ['0','1']
        variableDomainsDict['S'] = ['0','1']
        variableDomainsDict['Belt'] = ['0','1']
        variableDomainsDict['Size'] = ['small','normal']
        bayesNet = constructRandomlyFilledBayesNet(variableList, edgeTuplesList, variableDomainsDict)
        return bayesNet

    def inferGhostPowers(self,evidenceDict):
        queryVars = ['L','E','S']
        eliminationOrder = []
        inferenceByVariableElimination=inferenceByVariableEliminationWithCallTracking([])
        powersFactor = inferenceByVariableElimination(self.bayesNet, queryVars, evidenceDict, eliminationOrder)
        assignments = powersFactor.getAllPossibleAssignmentDicts()
        bestProb = 0
        inferredAssignment = {}
        for assignment in assignments:
            prob = powersFactor.getProbability(assignment)
            if(prob > bestProb):
                bestProb = prob
                inferredAssignment = assignment
        powers = {}
        powers['laser'] = int(inferredAssignment['L'])
        powers['speed'] = int(inferredAssignment['S'])
        powers['blast'] = int(inferredAssignment['E'])
        return powers


    def LaserPowerObservarionDict(self):
        evidenceDict = {}
        evidenceDict['Time'] = 'night'
        evidenceDict['Temp'] = 'hot'
        evidenceDict['Belt'] = '1'
        evidenceDict['Size'] = 'normal'
        return evidenceDict

    def BlastPowerObservarionDict(self):
        evidenceDict = {}
        evidenceDict['Time'] = 'day'
        evidenceDict['Temp'] = 'hot'
        evidenceDict['Belt'] = '1'
        evidenceDict['Size'] = 'normal'
        return evidenceDict

    def SpeedPowerObservarionDict(self):
        evidenceDict = {}
        evidenceDict['Time'] = 'day'
        evidenceDict['Temp'] = 'cold'
        evidenceDict['Belt'] = '0'
        evidenceDict['Size'] = 'small'
        return evidenceDict

    def NullPowerObservarionDict(self):
        evidenceDict = {}
        evidenceDict['Time'] = 'day'
        evidenceDict['Temp'] = 'cold'
        evidenceDict['Belt'] = '0'
        evidenceDict['Size'] = 'normal'
        return evidenceDict

def parseBayesNetProblem(testDict):
    # needs to be able to parse in a bayes net,
    # and figure out what type of operation to perform and on what
    parseDict = {}

    variableDomainsDict = {}
    for line in testDict['variableDomainsDict'].split('\n'):
        variable, domain = line.split(' : ')
        variableDomainsDict[variable] = domain.split(' ')

    parseDict['variableDomainsDict'] = variableDomainsDict


    
    variables = []
    for line in testDict["variables"].split('\n'):
        
        variable = line.strip()
        variables.append(variable)

    edges = []
    for line in testDict["edges"].split('\n'):
        
        tokens = line.strip().split()
        if len(tokens) == 2:
            edges.append((tokens[0], tokens[1]))

        else:
            raise Exception, "[parseBayesNetProblem] Bad evaluation line: |%s|" % (line,)

    # inference query args

    queryVariables = testDict['queryVariables'].split(' ')

    parseDict['queryVariables'] = queryVariables

    evidenceDict = {}
    for line in testDict['evidenceDict'].split('\n'):
        if(line.count(' : ')): #so we can pass empty dicts for unnormalized variables        
            (evidenceVariable, evidenceValue) = line.split(' : ')
            evidenceDict[evidenceVariable] = evidenceValue

    parseDict['evidenceDict'] = evidenceDict

    if testDict['constructRandomly'] == 'False':
        # load from test file
        problemBayesNet = constructEmptyBayesNet(variables, edges, variableDomainsDict)
        for variable in variables:
            currentFactor = Factor([variable], problemBayesNet.inEdges()[variable], variableDomainsDict)
            for line in testDict[variable + 'FactorTable'].split('\n'):
                assignments, probability = line.split(" = ")
                assignmentList = [assignment for assignment in assignments.split(', ')]

                assignmentsDict = {}
                for assignment in assignmentList:
                    var, value = assignment.split(' : ')
                    assignmentsDict[var] = value
                
                currentFactor.setProbability(assignmentsDict, float(probability))
            problemBayesNet.setCPT(variable, currentFactor)
            #print currentFactor
    elif testDict['constructRandomly'] == 'True':
        problemBayesNet = constructRandomlyFilledBayesNet(variables, edges, variableDomainsDict)

    parseDict['problemBayesNet'] = problemBayesNet

    if testDict['alg'] == 'inferenceByVariableElimination':
        variableEliminationOrder = testDict['variableEliminationOrder'].split(' ')
        parseDict['variableEliminationOrder'] = variableEliminationOrder
    elif testDict['alg'] == 'inferenceByLikelihoodWeightingSampling':
        numSamples = int(testDict['numSamples'])
        parseDict['numSamples'] = numSamples

    return parseDict

if __name__ == "__main__":
    #from powersBayesNet import *
    pbNet = PowersBayesNet()
    l = pbNet.inferGhostPowers(pbNet.LaserPowerObservarionDict())
    e = pbNet.inferGhostPowers(pbNet.BlastPowerObservarionDict())
    s = pbNet.inferGhostPowers(pbNet.SpeedPowerObservarionDict())
    n = pbNet.inferGhostPowers(pbNet.NullPowerObservarionDict())
    print l
    print e
    print s
    print n
    #factorsString = "\n ======================= \n\n".join([factor.easierToParseString() for factor in g.getAllConditionalProbabilityTablesInstantiatedWithEvidence()])
    #print factorsString
