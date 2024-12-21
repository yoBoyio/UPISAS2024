from UPISAS.strategy import Strategy
from UPISAS.strategies.mab import MAB
import numpy as np

class EmptyStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.data = self.knowledge.monitored_data

        # Define possible arms (parameter sets)
        self.mab = MAB([
            {"exploration_percentage": 0.1, "re_route_every_ticks": 50, "freshness_cut_off_value": 10},
            {"exploration_percentage": 0.2, "re_route_every_ticks": 25, "freshness_cut_off_value": 5},
            {"exploration_percentage": 0.3, "re_route_every_ticks": 10, "freshness_cut_off_value": 2},
        ])
        self.reward_threshold = 0.6
        self.decline_count = 0
        self.decline_limit = 5

    def analyze(self):
        """
        Analyze system performance and update MAB rewards.

        Returns:
            bool: Whether to plan an adaptation.
        """
        # Get monitored data
        self.knowledge.plan_data["total_trip_overhead_average"] = self.knowledge.monitored_data.get("total_trip_overhead_average", [{}])[-1]
        self.knowledge.plan_data["total_trips"] = self.knowledge.monitored_data.get("total_trips", [{}])[-1]



        # Calculate reward
        reward = 1.0 - (self.knowledge.plan_data["total_trip_overhead_average"] / self.knowledge.plan_data["total_trips"]) if self.knowledge.plan_data["total_trips"] > 0 else 0.0

        # Log the reward calculation
        print(f"Calculated Reward: {reward}")

        # Update the MAB rewards for the chosen arm
        chosen_arm = self.knowledge.plan_data.get("chosen_arm", 0)
        self.mab.update_rewards(chosen_arm, reward)

        # Update decline count
        if reward < self.reward_threshold:
            self.decline_count += 1
        else:
            self.decline_count = 0

        return True  # Always proceed to planning

    def plan(self):
        """
        Plan the next adaptation based on MAB.

        Returns:
            tuple: (bool, dict) Whether to adapt and the chosen configuration.
        """
        # Use MAB to select the best arm
        chosen_arm, best_config = self.mab.select_arm()

        # Handle repeated poor performance
        if self.decline_count >= self.decline_limit:
            print("Adjusting configuration due to poor performance.")
            best_config["exploration_percentage"] = min(best_config["exploration_percentage"] + 0.05, 0.5)
            best_config["re_route_every_ticks"] = max(best_config["re_route_every_ticks"] - 5, 10)
            best_config["freshness_cut_off_value"] = max(best_config["freshness_cut_off_value"] - 1, 2)
            self.decline_count = 0

        # Log selected configuration
        print(f"Chosen Arm: {chosen_arm}, Configuration: {best_config}")

        # Store the chosen arm and configuration
        self.knowledge.plan_data["chosen_arm"] = chosen_arm
        self.knowledge.plan_data.update(best_config)

        return True, best_config