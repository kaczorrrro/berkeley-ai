# powerChoosingAgents.py
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


# powerAgents.py
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

from powerAgents import *

class ReflexPowerChoosingAgent(ReflexPowerAgent):
    """
    The function getAction() is already defined in ReflexPowerAgent.
    Students just have to define the power choosing function here and the game 
    then plays automatically.
    """
    def getPowerChoice(self,inferredGhostPowers):
        """
        Question 5: Power Prediction

        inferredGhostPowers is a dictionary with keys 'laser',
        'speed' and 'blast'.  These powers were inferred using
        your bayesNet inference code.
        inferredGhostPowers is guaranteed to have exactly 
        one power set to 1 and the others set to 0.

        Below, you can choose your own agent's powers based on
        the inference.  Keep in mind that if your agent
        chooses powers that are the same as the ghost, they will be less
        effective and that some powers are better counterparts
        to others.  You should figure out the best powers to choose in
        response to the ghosts' powers.

        You can choose at most one of these three powers!
        Your powers dictionary should contain exactly one 
        entry with a value of 1 and two entries with values of 0.
        """
        powers = {}
        "*** YOUR CODE HERE ***"
        powers['blast'] = 0
        powers['laser'] = 0
        powers['speed'] = 0

        if inferredGhostPowers['speed'] == 1:
            powers['blast'] = 1
        elif inferredGhostPowers['blast'] == 1:
            powers['laser'] = 1
        elif inferredGhostPowers['laser'] == 1:
            powers['speed'] = 1

        return powers
