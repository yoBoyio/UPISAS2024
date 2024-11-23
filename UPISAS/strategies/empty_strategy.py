from UPISAS.strategy import Strategy
import gym
from gym import spaces
import numpy as np
import requests

class EmptyStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.current_num_of_complaints = 0
        self.initial_num_of_complaints_was_changed = False
        self.exploration_perc = -1

    def analyze(self, exploration_perc):
        monitored_data = self.knowledge.monitored_data
        car_stats = monitored_data['car_stats'][-1]

        trip_overhead = car_stats['total_trip_overhead_average']
        new_total_complaints = car_stats['total_complaints']
        complaints_delta = new_total_complaints - self.current_num_of_complaints

        if self.exploration_perc != exploration_perc: #not self.initial_num_of_complaints_was_changed:
            # sets the initial complaints num to 0, because complaints are just stacked, 
            # they do not change based on the steps and iterations, 
            # therefore the first iteration would show like 4567 (random num) complaints 
            # even though we just started tracking
            # therefore it should be reset to 0, whenever new experiment is started (new exploration percentage)
            self.exploration_perc = exploration_perc
            self.current_num_of_complaints = complaints_delta
            complaints_delta = 0 
        else:
            self.current_num_of_complaints = new_total_complaints
            
        return trip_overhead, complaints_delta
            
    def plan(self):
        pass