from UPISAS.strategy import Strategy
import gym
from gym import spaces
import numpy as np
import requests

class EmptyStrategy(Strategy):
    STEP_THRESHOLD = 0.3
    INITIAL_VALUE = 0.1

    # Initializing the strategy
    def __init__(self, exemplar):
        super().__init__(exemplar)
        # self.Planner = Planner
        self.data = self.knowledge.monitored_data
        self.adaptation_options = self.knowledge.adaptation_options
        self.itial_step = 0
        self.counter = 0
        
    # analyze method
    def analyze(self):
        self.counter += 1
        car_stats = self.data['car_stats'][-1]
        configs = self.data['configs'][-1]
        self.knowledge.analysis_data["exploration_percentage"] = configs["exploration_percentage"]
        print(self.data['car_stats'],'eeeee')
        print(car_stats['step'],'step')
        #  total_trip_average = self.data['total_trip_average']
        # total_trips = self.data['total_trips']
        # total_complaints = self.data['total_complaints']
        step = car_stats['step']
        self.knowledge.analysis_data["step"] = step
        
        if self.counter > 50000:
            self.sufficient  = True
            return True
        self.sufficient  = False

        return False
        
    # Planner method 
    def plan(self):
        # step = self.knowledge.analysis_data["step"] 
        # print(step, 'step')
        # if step > 50000 :
        #     self.knowledge.plan_data["exploration_percentage"]  = self.knowledge.analysis_data["exploration_percentage"] + 0.1
        #     print(self.knowledge.plan_data["exploration_percentage"],'exploration')
        #     return True

        # return False

        pass
    
   
