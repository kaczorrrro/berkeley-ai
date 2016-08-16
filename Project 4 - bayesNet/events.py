# events.py
# ---------
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


import bisect

class EventQueue:
    """
      Implements the event queue for Pacman games.
      Currently uses a slow list implementation (not a heap) so that
      equality checking is easy.
    """
    def  __init__(self):
        self.sortedEvents = []

    def registerEventAtTime(self, event, time):
        assert isinstance(event, Event)
        entry = (time, event)
        index = bisect.bisect_right(self.sortedEvents, entry)
        self.sortedEvents.insert(index, entry)

    def peek(self):
        assert self.sortedEvents, "Error: Peek on an empty EventQueue"
        return self.sortedEvents[0]

    def pop(self):
        assert self.sortedEvents, "Error: Pop on an empty EventQueue"
        return self.sortedEvents.pop(0)

    def isEmpty(self):
        return len(self.sortedEvents) == 0

    def getSortedTimesAndEvents(self):
        return self.sortedEvents

    def deepCopy(self):
        result = EventQueue()
        result.sortedEvents = [(t, e.deepCopy()) for t, e in self.sortedEvents]
        return result

    def __hash__(self):
        return hash(tuple(self.sortedEvents))

    def __eq__(self, other):
        return hasattr(other, 'sortedEvents') and \
            self.sortedEvents == other.sortedEvents

    def __str__(self):
        ansStr = "["
        for (t,e) in self.sortedEvents:
            if(e.isAgentMove):
                ansStr+= "(t = " + str(t) + ", " + str(e) + ")"
        return ansStr+"]"


class Event:
    """
    An abstract class for an Event.  All Events must have a trigger
    method which performs the actions of the Event.
    """
    nextId = 0
    def __init__(self, prevId=None):
        if prevId is None:
            self.eventId = Event.nextId
            Event.nextId += 1
        else:
            self.eventId = prevId

    def trigger(self, state):
        util.raiseNotDefined()

    def isAgentMove(self):
        return False

    def deepCopy(self):
        util.raiseNotDefined()

    def __eq__( self, other ):
        util.raiseNotDefined()

    def __hash__( self ):
        util.raiseNotDefined()

    def __lt__(self, other):
        return self.eventId < other.eventId
