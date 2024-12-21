from UPISAS.strategy import Strategy
import numpy as np

class MABTripStrategy(Strategy):
    """
    A multi-armed bandit (MAB) strategy that adapts system parameters
    (exploration_percentage, re_route_every_ticks, freshness_cut_off_value)
    based on trip_overhead / trip_average metrics.
    """

    def __init__(self, exemplar):
        super().__init__(exemplar)

        # Define possible configurations ("arms")
        self.arms = [
            {"exploration_percentage": 0.1, "re_route_every_ticks": 50, "freshness_cut_off_value": 10},
            {"exploration_percentage": 0.2, "re_route_every_ticks": 25, "freshness_cut_off_value": 5},
            {"exploration_percentage": 0.3, "re_route_every_ticks": 10, "freshness_cut_off_value": 2},
        ]
        
        self.num_arms = len(self.arms)

        # Keep track of MAB statistics
        self.counts  = [0] * self.num_arms      # Number of times each arm is chosen
        self.rewards = [0.0] * self.num_arms    # Cumulative reward for each arm
        self.t       = 1                        # Global counter for UCB

        # Feedback control
        self.reward_threshold = 0.6
        self.decline_count    = 0
        self.decline_limit    = 5

    def calculate_reward(self, trip_overhead: float, trip_average: float) -> float:
        """
        Convert trip_overhead / trip_average into a reward in [0, 1].
        Example: reward = 1 - (trip_overhead / trip_average).
        """
        if trip_average == 0:
            return 0.0
        raw_reward = 1.0 - (trip_overhead / trip_average)

        # Clamp the reward between 0.0 and 1.0
        return max(0.0, min(1.0, raw_reward))

    def analyze(self) -> bool:
        """
        1. Pull the newest monitoring data (trip_overhead, configs).
        2. Compute the reward for the previously chosen arm.
        3. Update MAB stats (counts, rewards).
        4. Decide if we want to adapt and return True or False accordingly.
        """
        # 1) Retrieve the newest data
        # "trip_overhead" is a list; we take the last item (dict), then get "trip_overhead" from it.
        overhead_list = self.knowledge.monitored_data.get("trip_overhead", [{}])
        trip_data     = overhead_list[-1] if overhead_list else {}
        trip_overhead = trip_data.get("trip_overhead", 0.0)

        # "configs" is also a list; we assume the last item has "trip_average"
        configs_list  = self.knowledge.monitored_data.get("configs", [{}])
        config_data   = configs_list[-1] if configs_list else {}
        trip_average  = config_data.get("trip_average", 1.0)

        # 2) Calculate reward
        reward = self.calculate_reward(trip_overhead, trip_average)

        # 3) Determine which arm was used last time
        #    (If none chosen yet, default to arm 0)
        chosen_arm = self.knowledge.plan_data.get("chosen_arm", 0)

        # Update MAB stats
        self.counts[chosen_arm]  += 1
        self.rewards[chosen_arm] += reward
        self.t += 1  # Increase global counter

        # 4) Update decline count and decide whether to adapt
        if reward < self.reward_threshold:
            self.decline_count += 1
        else:
            self.decline_count = 0

        # Example policy: adapt if we hit the decline limit or adapt every iteration
        # Here, we'll just return True every time so that plan() is always called.
        # If you only want to adapt when performance is repeatedly poor, you can do:
        # return (self.decline_count >= self.decline_limit)
        return True

    def calculate_ucb(self) -> list:
        """
        Compute UCB (Upper Confidence Bound) scores for each arm.
        If an arm has never been used, give it 'inf' so it will be chosen next.
        """
        ucb_scores = []
        for i in range(self.num_arms):
            if self.counts[i] == 0:
                # Never tried this arm
                ucb_scores.append(float('inf'))
            else:
                avg_reward = self.rewards[i] / self.counts[i]
                confidence = np.sqrt((2.0 * np.log(self.t)) / self.counts[i])
                ucb_scores.append(avg_reward + confidence)
        return ucb_scores

    def plan(self):
        """Plan adaptation using MAB strategy"""
        # Calculate UCB and select arm
        ucb_scores = self.calculate_ucb()
        chosen_arm = np.argmax(ucb_scores)
        best_config = self.arms[chosen_arm].copy()

        # Adjust parameters if needed
        if self.decline_count >= self.decline_limit:
            print("Adjusting parameters due to repeated poor performance.")
            # Increment exploration_percentage but cap it at 1.0
            best_config["exploration_percentage"] = min(best_config["exploration_percentage"] + 0.05, 1.0)
            # Decrease re_route_every_ticks but ensure it's at least 1
            best_config["re_route_every_ticks"] = max(best_config["re_route_every_ticks"] - 5, 1)
            # Decrease freshness_cut_off_value but ensure it's at least 1
            best_config["freshness_cut_off_value"] = max(best_config["freshness_cut_off_value"] - 1, 1)
            self.decline_count = 0  # Reset decline count

        # Store in knowledge
        self.knowledge.plan_data["chosen_arm"] = chosen_arm
        self.knowledge.plan_data.update(best_config)

        # Complete schema with constraints
        schema = {
            "configs": {
                "exploration_percentage": best_config["exploration_percentage"],  # Between 0 and 1
                "re_route_every_ticks": best_config["re_route_every_ticks"],  # Minimum 1
                "freshness_cut_off_value": best_config["freshness_cut_off_value"]  # Minimum 1
            },
            "status": "success",
            "message": "Adaptation plan generated successfully."
        }

        print(f"Returning schema: {schema}")
        return arm , schema