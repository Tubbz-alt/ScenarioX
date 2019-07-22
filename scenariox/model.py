#!/usr/bin/env python3
import uuid

class Agent:
    agentid = None
    state = {}
    actions = {}
    
    def __init__(self):
        self.agentid = str(uuid.uuid4())
        self.addDefaultActions()

    def addDefaultActions():
        self.actions["idle"] = None
        self.actions["communicate"] = None
        
class Leadership(Agent):
    def __init__(self):
        super().__init__()
        self.addLeadershipActions()
        
    def addLeadershipActions():
        self.actions["direct"] = None

class DeliveryExpert(Agent):
    def __init__(self):
        super().__init__()
        self.addDeliveryExpertActions()

    def addDeliverExpertActions():
        None

class TechnicalExpert(Agent):
    def __init__(self):
        super().__init__
        self.addTechnicalExpertActions()

    def addTechnicalExpertActions():
        None
