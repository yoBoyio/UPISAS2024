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
    def analyze(self):
        """
        Analyze system performance and track adjustments based on traffic data.

        Returns:
            tuple: (adjust_parameters, decline_count, reward, trip_overhead, trip_average)
        """
        # Increment the analysis counter
        self.counter += 1

        # Retrieve the latest car stats and configuration data
        car_stats = self.data.get('trip_overhead', [{}])[-1]
        configs = self.data.get('configs', [{}])[-1]

        # Extract metrics and update the knowledge base
        trip_overhead = car_stats.get('trip_overhead', 0)
        trip_average = configs.get('trip_average', 1)  # Avoid division by zero with a default value
        step = car_stats.get('step', 0)

        self.knowledge.analysis_data.update({
            "exploration_percentage": configs.get("exploration_percentage", 0),
            "step": step,
            "trip_overhead": trip_overhead,
            "trip_average": trip_average,
        })

        # Log debug information
        print(f"Car Stats: {car_stats}")
        print(f"Configuration: {configs}")
        print(f"Step: {step}, Trip Overhead: {trip_overhead}, Trip Average: {trip_average}")

        # Calculate the reward
        reward = self.calculate_reward(trip_overhead, trip_average)

        # Update decline count and determine if adjustments are needed
        self.decline_count = self.decline_count + 1 if reward < self.reward_threshold else 0
        adjust_parameters = self.decline_count >= self.decline_limit

        # Log analysis results
        print(f"Reward: {reward}, Decline Count: {self.decline_count}, Adjust Parameters: {adjust_parameters}")

        return adjust_parameters, self.decline_count, reward, trip_overhead, trip_average

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
            


    # # UCB calculation
    # def calculate_ucb(self, rewards, counts, t):
    #     """
    #     Calculate UCB scores for each arm.

    #     Args:
    #         rewards (list): Total rewards for each arm.
    #         counts (list): Number of times each arm has been selected.
    #         t (int): Current timestep.

    #     Returns:
    #         list: UCB scores for all arms.
    #     """
        
    #     return ucb_scores
    
        # Planner method
    def plan(self, arms, rewards, counts, t, decline_count, decline_limit):
        """
        Select the best configuration and prepare the action schema.

        Args:
            arms (list): Configurations for each arm.
            rewards (list): Total rewards for each arm.
            counts (list): Number of times each arm has been selected.
            t (int): Current timestep.
            decline_count (int): Current count of performance declines.
            decline_limit (int): Limit for triggering parameter adjustments.

        Returns:
            tuple: (selected_arm, current_config, action_schema)
        """
        # Calculate UCB scores for all arms
        ucb_scores = []
        for i in range(len(rewards)):
            if counts[i] == 0:
                ucb_scores.append(float('inf'))  # Ensure each arm is tried at least once
            else:
                average_reward = rewards[i] / counts[i]
                confidence_bound = np.sqrt((2 * np.log(t)) / counts[i])
                ucb_scores.append(average_reward + confidence_bound)

        # Log UCB scores
        print(f"UCB Scores: {ucb_scores}")

        # Select the arm with the highest UCB score
        selected_arm = np.argmax(ucb_scores)
        current_config = arms[selected_arm]

        # Log selected arm and configuration
        print(f"Selected Arm: {selected_arm}, Configuration: {current_config}")

        # Dynamically adjust parameters if performance declines
        if decline_count >= decline_limit:
            print("Adjusting parameters due to performance decline...")
            current_config["exploration_percentage"] = min(current_config["exploration_percentage"] + 0.05, 0.5)
            current_config["re_route_every_ticks"] = max(current_config["re_route_every_ticks"] - 5, 10)
            current_config["freshness_cut_off_value"] = max(current_config["freshness_cut_off_value"] - 1, 2)
            decline_count = 0  # Reset decline count

        # Prepare the action schema
        action_schema = {
            "exploration_percentage": current_config["exploration_percentage"],
            "re_route_every_ticks": current_config["re_route_every_ticks"],
            "freshness_cut_off_value": current_config["freshness_cut_off_value"],
        }

        # Log the action schema
        print(f"Action Schema: {action_schema}")

        return selected_arm, current_config, action_schema
            # step = self.knowledge.analysis_data["step"] 
            # print(step, 'step')
            # if step > 50000 :
            #     self.knowledge.plan_data["exploration_percentage"]  = self.knowledge.analysis_data["exploration_percentage"] + 0.1
            #     print(self.knowledge.plan_data["exploration_percentage"],'exploration')
            #     return True

            # return False

        
    
   
