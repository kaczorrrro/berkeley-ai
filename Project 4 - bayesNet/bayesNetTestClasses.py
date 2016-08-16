# bayesNetTestClasses.py
# ----------------------
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


import testClasses
import bayesNet
import random
from copy import deepcopy
from hashlib import sha1
from tempfile import mkstemp
import time
from shutil import move
from os import remove, close
import util

class FactorEqualityTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(FactorEqualityTest, self).__init__(question, testDict)
        self.seed = self.testDict['seed']
        random.seed(self.seed)
        self.alg = self.testDict['alg']
        self.max_points = int(self.testDict['max_points'])
        self.testPath = testDict['path']
        self.constructRandomly = testDict['constructRandomly']

    def execute(self, grades, moduleDict, solutionDict):
        # load student code and staff code solutions
        studentFactor = self.solveProblem(moduleDict)
        goldenFactor = parseFactorFromFileDict(solutionDict)

        # compare computed factor to stored factor
        self.addMessage('Executed FactorEqualityTest')
        if studentFactor == goldenFactor:
            # extra condition for test passing for this test type:
            if self.alg == 'inferenceByVariableElimination':
                goldenCallTrackingList = eval(solutionDict['callTrackingList'])
                if self.callTrackingList != goldenCallTrackingList:
                    self.addMessage('Order of joining by variables and elimination by variables is incorrect for variable elimination')
                    self.addMessage('Student performed the following operations in order: ' + str(self.callTrackingList) + '\n')
                    self.addMessage('Correct order of operations: ' + str(goldenCallTrackingList) + '\n')
                    return self.testFail(grades)

            return self.testPass(grades)
        else:
            self.addMessage('Factors are not equal.\n')
            self.addMessage('Student generated factor:\n\n' + str(studentFactor) + '\n\n')
            self.addMessage('Correct factor:\n\n' + str(goldenFactor) + '\n')

            studentProbabilityTotal = sum([studentFactor.getProbability(assignmentDict) for assignmentDict in studentFactor.getAllPossibleAssignmentDicts()])
            correctProbabilityTotal = sum([goldenFactor.getProbability(assignmentDict) for assignmentDict in goldenFactor.getAllPossibleAssignmentDicts()])
            if abs(studentProbabilityTotal - correctProbabilityTotal) > 10e-12:
                self.addMessage('Sum of probability in student generated factor is not the same as in correct factor')
                self.addMessage('Student sum of probability: ' + str(studentProbabilityTotal))
                self.addMessage('Correct sum of probability: ' + str(correctProbabilityTotal))

            return self.testFail(grades)


    def writeSolution(self, moduleDict, filePath):

        if self.constructRandomly:
            if self.alg == 'joinFactors' or self.alg == 'eliminate' or \
                    self.alg == 'normalize':
                replaceTestFile(self.testPath, "Factors", self.factorsDict)
            elif self.alg == 'inferenceByVariableElimination' or \
                    self.alg == 'inferenceByLikelihoodWeightingSampling':
                replaceTestFile(self.testPath, "BayesNet", self.problemBayesNet)

        factor = self.solveProblem(moduleDict)
        with open(filePath, 'w') as handle:
            handle.write('# This is the solution file for %s.\n' % self.path)
            printString = factor.easierToParseString()
            handle.write('%s\n' % (printString))

            if self.alg == 'inferenceByVariableElimination':
                handle.write('callTrackingList: "' + repr(self.callTrackingList) + '"\n')
        return True


class FactorInputFactorEqualityTest(FactorEqualityTest):
    def __init__(self, question, testDict):
        super(FactorInputFactorEqualityTest, self).__init__(question, testDict)
        self.factorArgs = self.testDict['factorArgs']
        eliminateToPerform = (self.alg == 'eliminate')
        evidenceAssignmentToPerform = (self.alg == 'normalize')

        parseDict =  parseFactorInputProblem(testDict, goingToEliminate=eliminateToPerform,
                                             goingToEvidenceAssign=evidenceAssignmentToPerform)
        self.variableDomainsDict = parseDict['variableDomainsDict']
        self.factorsDict = parseDict['factorsDict']
        if eliminateToPerform:
            self.eliminateVariable = parseDict['eliminateVariable']
        if evidenceAssignmentToPerform:
            self.evidenceDict = parseDict['evidenceDict']
        self.max_points = int(self.testDict['max_points'])

    def solveProblem(self, moduleDict):
        factorOperationsModule =  moduleDict['factorOperations']
        studentComputation = getattr(factorOperationsModule, self.alg)
        if self.alg == 'joinFactors':
            solvedFactor = studentComputation(self.factorsDict.values())
            #for factor in self.factorsDict.values():
                #print factor.easierToParseString(printVariableDomainsDict=False)
        elif self.alg == 'eliminate':
            solvedFactor = studentComputation(self.factorsDict.values()[0],
                                              self.eliminateVariable)
        elif self.alg == 'normalize':
            newVariableDomainsDict = deepcopy(self.variableDomainsDict)
            for variable, value in self.evidenceDict.items():
                newVariableDomainsDict[variable] = [value]
            origFactor = self.factorsDict.values()[0]
            specializedFactor = origFactor.specializeVariableDomains(newVariableDomainsDict)
            solvedFactor = studentComputation(specializedFactor)
        
        return solvedFactor


class BayesNetInputFactorEqualityTest(FactorEqualityTest):

    def __init__(self, question, testDict):
        super(BayesNetInputFactorEqualityTest, self).__init__(question, testDict)

        parseDict = parseBayesNetProblem(testDict)

        self.queryVariables = parseDict['queryVariables']
        self.evidenceDict = parseDict['evidenceDict']

        if self.alg == 'inferenceByVariableElimination':
            self.callTrackingList = []
            self.variableEliminationOrder = parseDict['variableEliminationOrder']
        elif self.alg == 'inferenceByLikelihoodWeightingSampling':
            self.numSamples = parseDict['numSamples']

        self.problemBayesNet = parseDict['problemBayesNet']
        self.max_points = int(self.testDict['max_points'])

    def solveProblem(self, moduleDict):
        inferenceModule = moduleDict['inference']
        if self.alg == 'inferenceByVariableElimination':
            studentComputationWithCallTracking = getattr(inferenceModule, self.alg + 'WithCallTracking')
            studentComputation = studentComputationWithCallTracking(self.callTrackingList)
            solvedFactor = studentComputation(self.problemBayesNet, self.queryVariables, self.evidenceDict, self.variableEliminationOrder)
        elif self.alg == 'inferenceByLikelihoodWeightingSampling':
            randomSource = util.FixedRandom().random
            studentComputationRandomSource = getattr(inferenceModule, self.alg + 'RandomSource')
            studentComputation = studentComputationRandomSource(randomSource)
            #random.seed(self.seed) # reset seed so that if we had to compute the bayes net we still have the initial seed
            solvedFactor = studentComputation(self.problemBayesNet, self.queryVariables, self.evidenceDict, self.numSamples)
        
        return solvedFactor

def parseFactorInputProblem(testDict, goingToEliminate=False, goingToEvidenceAssign=False):
    parseDict = {}
    variableDomainsDict = {}
    for line in testDict['variableDomainsDict'].split('\n'):
        variable, domain = line.split(' : ')
        variableDomainsDict[variable] = domain.split(' ')

    parseDict['variableDomainsDict'] = variableDomainsDict


    factorsDict = {} # assume args is a list of factor names and maybe a variable name at the end
    if goingToEliminate:
        eliminateVariable = testDict["eliminateVariable"]
        parseDict['eliminateVariable'] = eliminateVariable

    # for normalize need evidence so that normalize is nontrivial
    if goingToEvidenceAssign:
        evidenceAssignmentString = testDict["evidenceDict"]
        evidenceDict = {}
        for line in evidenceAssignmentString.split('\n'):
            if(line.count(' : ')): #so we can pass empty dicts for unnormalized variables
                evidenceVariable, evidenceAssignment = line.split(' : ')
                evidenceDict[evidenceVariable] = evidenceAssignment
        parseDict['evidenceDict'] = evidenceDict

    for factorName in testDict["factorArgs"].split(' '):
        # construct a dict from names to factors and 
        # load a factor from the test file for each

        currentFactor = parseFactorFromFileDict(testDict, variableDomainsDict=variableDomainsDict,
                                                prefix=factorName)
        factorsDict[factorName] = currentFactor

    parseDict['factorsDict'] = factorsDict

    return parseDict

def replaceTestFile(file_path, typeOfTest, inputToTest):
    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            # Assumes that variableDomainsDict is the last 
            # entry in the test file before the factors start to 
            # get enumerated
            for line in old_file:
                new_file.write(line)
                if 'endOfNonFactors' in line:
                    break
        if typeOfTest == 'BayesNet':
            new_file.write("\n" + inputToTest.easierToParseString())
        elif typeOfTest == 'Factors':
            new_file.write("\n" + "\n".join([factor.easierToParseString(prefix=name, 
                                      printVariableDomainsDict=False) for 
                                      name, factor in inputToTest.items()]))


    close(fh)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)

def parseFactorFromFileDict(fileDict, variableDomainsDict=None, prefix=None):
    if prefix is None:
        prefix = ''
    if variableDomainsDict is None:
        variableDomainsDict = {}
        for line in fileDict['variableDomainsDict'].split('\n'):
            variable, domain = line.split(' : ')
            variableDomainsDict[variable] = domain.split(' ')
    # construct a dict from names to factors and 
    # load a factor from the test file for each


    unconditionedVariables = []
    for variable in fileDict[prefix + "unconditionedVariables"].split(' '):
        unconditionedVariable = variable.strip()
        unconditionedVariables.append(unconditionedVariable)

    conditionedVariables = []
    for variable in fileDict[prefix + "conditionedVariables"].split(' '):
        conditionedVariable = variable.strip()
        if variable != '':
            conditionedVariables.append(conditionedVariable)

    if 'constructRandomly' not in fileDict or fileDict['constructRandomly'] == 'False':
        currentFactor = bayesNet.Factor(unconditionedVariables, conditionedVariables,
                                        variableDomainsDict)
        for line in fileDict[prefix + 'FactorTable'].split('\n'):
            assignments, probability = line.split(" = ")
            assignmentList = [assignment for assignment in assignments.split(', ')]

            assignmentsDict = {}
            for assignment in assignmentList:
                var, value = assignment.split(' : ')
                assignmentsDict[var] = value
            
            currentFactor.setProbability(assignmentsDict, float(probability))
    elif fileDict['constructRandomly'] == 'True':
        currentFactor = bayesNet.constructAndFillFactorRandomly(unconditionedVariables, conditionedVariables, variableDomainsDict)
    return currentFactor



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
        problemBayesNet = bayesNet.constructEmptyBayesNet(variables, edges, variableDomainsDict)
        for variable in variables:
            currentFactor = bayesNet.Factor([variable], problemBayesNet.inEdges()[variable], variableDomainsDict)
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
        problemBayesNet = bayesNet.constructRandomlyFilledBayesNet(variables, edges, variableDomainsDict)

    parseDict['problemBayesNet'] = problemBayesNet

    if testDict['alg'] == 'inferenceByVariableElimination':
        variableEliminationOrder = testDict['variableEliminationOrder'].split(' ')
        parseDict['variableEliminationOrder'] = variableEliminationOrder
    elif testDict['alg'] == 'inferenceByLikelihoodWeightingSampling':
        numSamples = int(testDict['numSamples'])
        parseDict['numSamples'] = numSamples

    return parseDict

##############################################
###### TetsClasses for Pacman Game ###########
import testClasses
import json, time

from collections import defaultdict
from pprint import PrettyPrinter
pp = PrettyPrinter()

from game import Agent
from pacman import GameState
from ghostAgents import RandomGhost, DirectionalGhost, DirectionalPowerGhost
import random, math, traceback, sys, os
import layout, pacman
import autograder
import graphicsDisplay

VERBOSE = False

def run(lay, layName, pac, ghosts, ghostPowers, disp, nGames=1, name='games'):
    """
    Runs a few games and outputs their statistics.
    """
    starttime = time.time()
    print '*** Running %s on' % name, layName, '%d time(s).' % nGames
    #runGames( layout, pacman, pacmanPowers, ghosts, ghostPowers, powerLimit, display, numGames, record, numTraining = 0, catchExceptions=False, timeout=30)
    games = pacman.runGames( lay, pac, {}, ghosts, [ghostPowers], 4, disp, nGames, False, numTraining = 0, catchExceptions=False, timeout=10000)
    print '*** Finished running %s on' % name, layName, 'after %d seconds.' % (time.time() - starttime)
    stats = {'time': time.time() - starttime, 'wins': [g.state.isWin() for g in games].count(True), 'games': games, 'scores': [g.state.getScore() for g in games],
             'timeouts': [g.agentTimeout for g in games].count(True), 'crashes': [g.agentCrashed for g in games].count(True)}
    print '*** Won %d out of %d games. Average score: %f ***' % (stats['wins'], len(games), sum(stats['scores']) * 1.0 / len(games))
    return stats

class EvalAgentTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(EvalAgentTest, self).__init__(question, testDict)
        self.layoutName = testDict['layoutName']
        self.agentName = testDict['agentName']
        self.ghosts = eval(testDict['ghosts'])
        self.maxTime = int(testDict['maxTime'])
        self.seed = int(testDict['randomSeed'])
        self.numGames = int(testDict['numGames'])
        self.ghostPowers = {}
        self.ghostPowers[testDict['power']] = '2'
        self.frameTime = 0.05

        self.scoreMinimum = int(testDict['scoreMinimum']) if 'scoreMinimum' in testDict else None
        self.nonTimeoutMinimum = int(testDict['nonTimeoutMinimum']) if 'nonTimeoutMinimum' in testDict else None
        self.winsMinimum = int(testDict['winsMinimum']) if 'winsMinimum' in testDict else None

        self.scoreThresholds = [int(s) for s in testDict.get('scoreThresholds','').split()]
        self.nonTimeoutThresholds = [int(s) for s in testDict.get('nonTimeoutThresholds','').split()]
        self.winsThresholds = [int(s) for s in testDict.get('winsThresholds','').split()]

        self.maxPoints = sum([len(t) for t in [self.scoreThresholds, self.nonTimeoutThresholds, self.winsThresholds]])
        self.agentArgs = testDict.get('agentArgs', '')

    def execute(self, grades, moduleDict, solutionDict):

        #print moduleDict
        agentType = getattr(moduleDict['powerChoosingAgents'], self.agentName)
        agentOpts = pacman.parseAgentArgs(self.agentArgs) if self.agentArgs != '' else {}
        agent = agentType(**agentOpts)

        lay = layout.getLayout(self.layoutName, 3)

        #disp = self.question.getDisplay()
        import textDisplay
        disp = textDisplay.NullGraphics()
        #disp = graphicsDisplay.PacmanGraphics(1, frameTime = self.frameTime)
        #print disp

        random.seed(self.seed)
        stats = run(lay, self.layoutName, agent, self.ghosts, self.ghostPowers, disp, self.numGames)

        #games = pacman.runGames(lay, agent, self.ghosts, disp, self.numGames, False, catchExceptions=True, timeout=self.maxTime)
        #totalTime = time.time() - startTime

        #stats = {'time': totalTime, 'wins': [g.state.isWin() for g in games].count(True),
        #         'games': games, 'scores': [g.state.getScore() for g in games],
        #         'timeouts': [g.agentTimeout for g in games].count(True), 'crashes': [g.agentCrashed for g in games].count(True)}

        averageScore = sum(stats['scores']) / float(len(stats['scores']))
        nonTimeouts = self.numGames - stats['timeouts']
        wins = stats['wins']
        print "Number of wins : " + str(wins)
        print "Minimum number of required wins : "  +str(self.winsMinimum)
        if(wins >= self.winsMinimum):
            return self.testPass(grades)
        else:
            return self.testFail(grades)

    def writeSolution(self, moduleDict, filePath):
        handle = open(filePath, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# File intentionally blank.\n')
        handle.close()
        return True



class IndependenceQuestionTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(IndependenceQuestionTest, self).__init__(question, testDict)
        self.question = testDict['question']
        parseDict = parseBayesNetProblem(testDict)

        self.max_points = int(self.testDict['max_points'])
        self.seed = self.testDict['seed']
        random.seed(self.seed)

        self.queryVariables = parseDict['queryVariables']
        self.evidenceDict = parseDict['evidenceDict']

        self.callTrackingList = []
        self.variableEliminationOrder = parseDict['variableEliminationOrder']

        self.testPath = testDict['path']

        self.fullVarElimTime = testDict['fullVarElimTime']
        self.reducedVarElimTime = testDict['reducedVarElimTime']
        self.fullEnumerationTime = testDict['fullEnumerationTime']
        self.reducedEnumerationTime = testDict['reducedEnumerationTime']

        self.problemBayesNet = parseDict['problemBayesNet']

    def solveProblem(self, moduleDict, analysisSolution, computeFullEnum=False):
        # try variable elimination first, then with enumeration if that doesn't work
        inferenceModule = moduleDict['inference']
        reducedBayesNet = bayesNet.reduceBayesNetVariablesWithEvidence(self.problemBayesNet, \
                                                                       analysisSolution,
                                                                       self.evidenceDict)

        # var elim time
        try:
            studentComputationWithCallTracking = getattr(inferenceModule, 'inferenceByVariableEliminationWithCallTracking')
            studentComputation = studentComputationWithCallTracking(self.callTrackingList)
            startTime = time.clock()
            solvedFactorReducedVarElim = studentComputation(reducedBayesNet, self.queryVariables, self.evidenceDict, None)
            endTime = time.clock()
            reducedVarElimTime = endTime - startTime
        except:
            reducedVarElimTime = None

        # enumeration time
        studentComputation = getattr(inferenceModule, 'inferenceByEnumeration')
        startTime = time.clock()
        solvedFactorReducedEnum = studentComputation(reducedBayesNet, self.queryVariables, self.evidenceDict)
        endTime = time.clock()
        reducedEnumerationTime = endTime - startTime

        # full bayes net comparison
        # var elim time
        try:
            studentComputationWithCallTracking = getattr(inferenceModule, 'inferenceByVariableEliminationWithCallTracking')
            studentComputation = studentComputationWithCallTracking(self.callTrackingList)
            startTime = time.clock()
            solvedFactorFullVarElim = studentComputation(self.problemBayesNet, self.queryVariables, self.evidenceDict, None)
            endTime = time.clock()
            fullVarElimTime = endTime - startTime
            #print 'equal full vs reduced: ', str(solvedFactorFullVarElim == solvedFactorReducedVarElim)
        except:
            fullVarElimTime = None


        # enumeration time
        if self.question != 'c' or computeFullEnum:
            studentComputation = getattr(inferenceModule, 'inferenceByEnumeration')
            startTime = time.clock()
            solvedFactorFullEnum = studentComputation(self.problemBayesNet, self.queryVariables, self.evidenceDict)
            endTime = time.clock()
            fullEnumerationTime = endTime - startTime
            #print 'equal full vs reduced: ', str(solvedFactorFullEnum == solvedFactorReducedEnum)
        else:
            fullEnumerationTime = None
        
        return reducedVarElimTime, reducedEnumerationTime, fullVarElimTime, fullEnumerationTime

    def execute(self, grades, moduleDict, solutionDict):
        studentSolutions = moduleDict['analysis']
        studentSolution = getattr(studentSolutions, 'question5' + str(self.question))()
        studentSolutionSortedString = " ".join(sorted(studentSolution)).upper()
        hashedSolution = sha1(studentSolutionSortedString).hexdigest()

        goldenHashedSolution = solutionDict['hashedSolution']
        if hashedSolution == goldenHashedSolution:
            try:
                reducedVarElimTime, reducedEnumerationTime, fullVarElimTime, fullEnumerationTime = self.solveProblem(moduleDict, analysisSolution=studentSolution)
                if reducedVarElimTime is not None:
                    self.addMessage("Student performed the inference query using variable elimination \n" + \
                                    "(and an arbitrary variable elimination order) in the reduced Bayes' net\n" + \
                                    "in time: " + str(reducedVarElimTime) + " seconds.")
                    self.addMessage("Student performed the inference query using variable elimination\n" + \
                                    "(and an arbitrary variable elimination order) in the full Bayes' net\n" + \
                                    "in time: " + str(fullVarElimTime) + " seconds.")
                    self.addMessage("Variable elimination Speedup Ratio: " + str(fullVarElimTime / reducedVarElimTime) + "\n")
                else: 
                    self.addMessage("\n" + \
                                    "To decouple this question from previous questions, for the \n" + \
                                    "purposes of this question, feel free to ignore: 'Method not implemented:\n" + \
                                    "inferenceByVariableElimination at line 120 of inference.py'\n")

                self.addMessage("Student performed the inference query using enumeration \n" + \
                                "in the reduced Bayes' net in time: " + str(reducedEnumerationTime) + " seconds.")
                if self.question != 'c':
                    self.addMessage("Student performed the inference query using enumeration \n" + \
                                    "in the full Bayes' net in time: " + str(fullEnumerationTime) + " seconds.")
                    self.addMessage("Enumeration Speedup Ratio: " + str(fullEnumerationTime / reducedEnumerationTime) + "\n")
                else:
                    reducedEnumerationTime = float(self.reducedEnumerationTime)
                    self.addMessage("On the instructor's computer, the inference query was performed using \n" + \
                                    "enumeration in the reduced Bayes' net in time: " + str(reducedEnumerationTime) + " seconds.")
                    fullEnumerationTime = float(self.fullEnumerationTime)
                    self.addMessage("On the instructor's computer, the inference query was performed using \n" + \
                                    "enumeration in the full Bayes' net in time: " + str(fullEnumerationTime) + " seconds.")
                    self.addMessage("Enumeration Speedup Ratio on the instructor's computer: " + str(fullEnumerationTime / reducedEnumerationTime))
            except:
                self.addMessage("Functions needed for inference are not implemented.\n"
                                "This question's points are not dependent on previous questions.")

            grades.addPoints(self.max_points)
            return self.testPass(grades)
        else:
            #self.addMessage(str(self.solveProblem(moduleDict, analysisSolution=studentSolution)))
            self.addMessage("Solution is not correct.")
            self.addMessage("   Student solution: %s" % (studentSolution,))
            self.testFail(grades)
            return True # Return true so that other tests do not fail

    def writeSolution(self, moduleDict, filePath):
        studentSolutions = moduleDict['analysis']
        studentSolution = getattr(studentSolutions, 'question5' + str(self.question))()
        studentSolutionSortedString = " ".join(sorted(studentSolution)).upper()
        hashedSolution = sha1(studentSolutionSortedString).hexdigest()

        # UNCOMMENT THIS TO GET NEW SPEED REPORTS
        #reducedVarElimTime, reducedEnumerationTime, fullVarElimTime, fullEnumerationTime = self.solveProblem(moduleDict, analysisSolution=studentSolution, computeFullEnum=True)
        #if self.alg == 'joinFactors' or self.alg == 'eliminate' or \
                #self.alg == 'normalize':

        with open(filePath, 'w') as handle:
            handle.write('# This is the solution file for %s.\n' % self.path)
            handle.write('hashedSolution: "' + hashedSolution + '"\n')

            # UNCOMMENT THIS TO GET NEW SPEED REPORTS
            #handle.write('reducedVarElimTime: "' + str(reducedVarElimTime) + '"\n')
            #handle.write('fullVarElimTime: "' + str(fullVarElimTime) + '"\n')
            #handle.write('reducedEnumerationTime: "' + str(reducedEnumerationTime) + '"\n')
            #handle.write('fullEnumerationTime: "' + str(fullEnumerationTime) + '"\n')

        return True

