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
        """
        Analyze system performance and track adjustments based on traffic data.

        Args:
            reward_threshold (float): The minimum acceptable reward.
            decline_count (int): The current count of consecutive performance declines.
            decline_limit (int): The limit of declines before triggering adjustments.

        Returns:
            tuple: (adjust_parameters, decline_count, reward, trip_overhead, trip_average)
        """
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

        # Update decline count and check if parameters need adjustment
        if reward < reward_threshold:
            decline_count += 1
        else:
            decline_count = 0

        adjust_parameters = decline_count >= decline_limit

        # Log analysis results
        print(f"Reward: {reward}, Decline Count: {decline_count}, Adjust Parameters: {adjust_parameters}")
        print(f"Trip Overhead: {trip_overhead}, Trip Average: {trip_average}")

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
    def calculate_ucb(self, rewards, counts, t):
        """
        Calculate UCB scores for each arm.

        Args:
            rewards (list): Total rewards for each arm.
            counts (list): Number of times each arm has been selected.
            t (int): Current timestep.

        Returns:
            list: UCB scores for all arms.
        """
        ucb_scores = []
        for i in range(len(rewards)):
            if counts[i] == 0:
                ucb_scores.append(float('inf'))  # Ensure each arm is tried at least once
            else:
                average_reward = rewards[i] / counts[i]
                confidence_bound = np.sqrt((2 * np.log(t)) / counts[i])
                ucb_scores.append(average_reward + confidence_bound)

        # Log or debug the UCB scores
        print(f"UCB Scores: {ucb_scores}")
        return ucb_scores
    
        # Planner method
    def plan(self, ucb_scores, arms, decline_count, decline_limit):
        """
        Select the best configuration and prepare the action schema.

        Args:
            ucb_scores (list): UCB scores for all arms.
            arms (list): Configurations for each arm.
            decline_count (int): Current count of performance declines.
            decline_limit (int): Limit for triggering parameter adjustments.

        Returns:
            tuple: (selected_arm, current_config, action_schema)
        """
        # Select the arm with the highest UCB score
        selected_arm = np.argmax(ucb_scores)
        current_config = arms[selected_arm]

        # Log selected arm
        print(f"Selected Arm: {selected_arm}, Configuration: {current_config}")

        # Dynamically adjust parameters if needed
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

        
    
   
