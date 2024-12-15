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

    # Define the "arms" (configurations)
    arms = [
        {"exploration_percentage": 0.1, "re_route_every_ticks": 50, "freshness_cut_off_value": 10},  # Low Traffic
        {"exploration_percentage": 0.2, "re_route_every_ticks": 25, "freshness_cut_off_value": 5},   # Medium Traffic
        {"exploration_percentage": 0.3, "re_route_every_ticks": 10, "freshness_cut_off_value": 2}   # High Traffic
    ]    

    #The number of arms (configurations)        
    num_arms = len(arms)

    # Initialize variables
    rewards = [0] * num_arms  # Total reward for each arm
    counts = [0] * num_arms   # Number of times each arm is selected
    t = 1                     # Current timestep

    # Feedback control
    reward_threshold = 0.6  # Threshold for acceptable performance
    decline_count = 0
    decline_limit = 5  # Number of iterations with low reward before updating parameters

        # Reward calculation function
    def calculate_reward(trip_overhead, trip_average):
            """Calculate reward based on system performance."""
            return 1 - (trip_overhead / trip_average)

        # analyze method
    def analyze(self, reward_threshold, decline_count, decline_limit):
        # Increment the analysis counter
        self.counter += 1

        # Retrieve the latest car stats and configuration data
        car_stats = self.data['trip_overhead'][-1]
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
        trip_average = configs.get('trip_average', 0)

        # Store the performance metrics in the knowledge base for later analysis
        self.knowledge.analysis_data["trip_overhead"] = trip_overhead
        self.knowledge.analysis_data["trip_average"] = trip_average

        # Calculate the reward based on the performance metrics
        reward = calculate_reward(trip_overhead, trip_average)

        if reward < reward_threshold:
            decline_count += 1
        else:
            decline_count = 0

        adjust_parameters = decline_count >= decline_limit
        return adjust_parameters, decline_count, reward, trip_overhead, trip_average

        # # Check if conditions for sufficiency are met
        # # Here, the condition is example logic, refine it as necessary
        # if self.counter > 50000:
        #     # Example threshold for metrics
        #     if trip_overhead < 1.5 and complaints_rate < 0.05:
        #         self.sufficient = True
        #         return True

        # # If not sufficient, continue adaptation
        # self.sufficient = False
        # return False
            


    # UCB calculation
    def calculate_ucb(rewards, counts, t):
        """Calculate UCB scores for each arm."""
        ucb_scores = []
        for i in range(num_arms):
            if counts[i] == 0:
                ucb_scores.append(float('inf'))  # Ensure each arm is tried at least once
            else:
                average_reward = rewards[i] / counts[i]
                confidence_bound = np.sqrt((2 * np.log(t)) / counts[i])
                ucb_scores.append(average_reward + confidence_bound)
        return ucb_scores

        # Planner method 
    def plan(self, ucb_scores, arms, decline_count, decline_limit):
        """Select the best configuration and update parameters if needed."""
        selected_arm = np.argmax(ucb_scores)
        current_config = arms[selected_arm]

        # Adjust parameters dynamically if performance declines
        if decline_count >= decline_limit:
            current_config["exploration_percentage"] = min(current_config["exploration_percentage"] + 0.05, 0.5)
            current_config["re_route_every_ticks"] = max(current_config["re_route_every_ticks"] - 5, 10)
            current_config["freshness_cut_off_value"] = max(current_config["freshness_cut_off_value"] - 1, 2)

        # Prepare the action schema outside the EXECUTE phase
        action_schema = {
            "exploration_percentage": current_config["exploration_percentage"],
            "re_route_every_ticks": current_config["re_route_every_ticks"],
            "freshness_cut_off_value": current_config["freshness_cut_off_value"],
        }

        return selected_arm, current_config, action_schema
    
    

        # EXECUTE function with external action schema
    def execute(self, action_schema, selected_arm, rewards, counts, reward, strategy):
        """Execute the action schema by calling the strategy's execute method."""
        print(f"Executing: {action_schema}")
        strategy.execute(action_schema, with_validation=False)

        # Update rewards and counts for the selected arm
        counts[selected_arm] += 1
        rewards[selected_arm] += reward


            # step = self.knowledge.analysis_data["step"] 
            # print(step, 'step')
            # if step > 50000 :
            #     self.knowledge.plan_data["exploration_percentage"]  = self.knowledge.analysis_data["exploration_percentage"] + 0.1
            #     print(self.knowledge.plan_data["exploration_percentage"],'exploration')
            #     return True

            # return False

        
    
   
