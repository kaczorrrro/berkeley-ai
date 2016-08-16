# analysis.py
# -----------
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



######################
# ANALYSIS QUESTIONS #
######################

# For the Bayes' Nets, query variables, and evidence given in the
# website, return the set of variables that can be ignored when
# performing inference.
# Do not include evidence variables.

def question5a():
    ignoredVariables = ['w','g']
    # Example solution : ignoredVariables = ['E', 'G'] (order does not matter so ['G','E'] is also the same)
    return ignoredVariables

def question5b():
    ignoredVariables = ['a','h','i']
    return ignoredVariables

def question5c():
    ignoredVariables = ["x1",'x2','x3','x4','x5','x6','y1','y2','y3','y4','y5','y6','y7','y8','y12','y13','y14']
    return ignoredVariables


