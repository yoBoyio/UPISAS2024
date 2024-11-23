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
    # Increment the analysis counter
    self.counter += 1

    # Retrieve the latest car stats and configuration data
    car_stats = self.data['car_stats'][-1]
    configs = self.data['configs'][-1]

    # Store the current exploration percentage and step in knowledge
    self.knowledge.analysis_data["exploration_percentage"] = configs["exploration_percentage"]
    step = car_stats['step']
    self.knowledge.analysis_data["step"] = step

    # Log or debug the input data
    print(f"Current car stats: {car_stats}")
    print(f"Current step: {step}")

    # Retrieve performance metrics for analysis
    trip_overhead = car_stats.get('trip_overhead', 0)
    complaints_rate = car_stats.get('complaints_rate', 0)

    # Store the performance metrics in the knowledge base for later analysis
    self.knowledge.analysis_data["trip_overhead"] = trip_overhead
    self.knowledge.analysis_data["complaints_rate"] = complaints_rate

    # Check if conditions for sufficiency are met
    # Here, the condition is example logic, refine it as necessary
    if self.counter > 50000:
        # Example threshold for metrics
        if trip_overhead < 1.5 and complaints_rate < 0.05:
            self.sufficient = True
            return True

    # If not sufficient, continue adaptation
    self.sufficient = False
    return False
        
    # Planner method 
    def plan(self):
        pass
        # step = self.knowledge.analysis_data["step"] 
        # print(step, 'step')
        # if step > 50000 :
        #     self.knowledge.plan_data["exploration_percentage"]  = self.knowledge.analysis_data["exploration_percentage"] + 0.1
        #     print(self.knowledge.plan_data["exploration_percentage"],'exploration')
        #     return True

        # return False

        
    
   
