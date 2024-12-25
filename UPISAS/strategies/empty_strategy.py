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
        """Analyze system state and update knowledge"""
        # Get monitored data
        data = self.knowledge.monitored_data
        car_stats = data.get('car_stats', [{}])[-1]
        configs = data.get('configs', [{}])[-1]

        # Calculate metrics
        trip_overhead = car_stats.get('total_trip_overhead_average', 0.0)
        trip_average = car_stats.get('total_trip_average', 1.0)
        total_trips = car_stats.get('total_trips', 0)
        
        # Store analysis results
        self.knowledge.analysis_data = {
            "trip_overhead": trip_overhead,
            "trip_average": trip_average,
            "total_trips": total_trips,
            "reward": self.calculate_reward(trip_overhead, trip_average)
        }

        # Update MAB statistics
        chosen_arm = self.knowledge.plan_data.get("chosen_arm", 0)
        self.counts[chosen_arm] += 1
        self.rewards[chosen_arm] += self.knowledge.analysis_data["reward"]
        self.t += 1

        # Check performance
        if self.knowledge.analysis_data["reward"] < self.reward_threshold:
            self.decline_count += 1
        else:
            self.decline_count = 0

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
        # Calculate UCB scores and select best arm
        ucb_scores = self.calculate_ucb()  # Already returns a list
        chosen_arm = np.argmax(ucb_scores)
        best_config = self.arms[chosen_arm].copy()

        # Store all planning data in knowledge
        self.knowledge.plan_data = {
            "chosen_arm": chosen_arm,
            "ucb_scores": ucb_scores,  # Remove .tolist() since it's already a list
            "best_config": best_config,
            "exploration_percentage": best_config["exploration_percentage"],
            "re_route_every_ticks": best_config["re_route_every_ticks"],
            "freshness_cut_off_value": best_config["freshness_cut_off_value"]
        }

        print(f"[MAB] UCB Scores: {self.knowledge.plan_data['ucb_scores']}")
        print(f"[MAB] Chosen Arm: {self.knowledge.plan_data['chosen_arm']}")
        print(f"[MAB] Selected Config: {self.knowledge.plan_data['best_config']}")

        # Return complete schema for execution
        schema = {
            "configs": {
                "exploration_percentage": self.knowledge.plan_data["exploration_percentage"],
                "re_route_every_ticks": self.knowledge.plan_data["re_route_every_ticks"],
                "freshness_cut_off_value": self.knowledge.plan_data["freshness_cut_off_value"],
                "route_random_sigma": 0.2,
                "max_speed_and_length_factor": 1.0,
                "average_edge_duration_factor": 1.0,
                "freshness_update_factor": 10.0,
                "total_car_counter": 750,
                "edge_average_influence": 140.0
            }
        }

        return chosen_arm, schema["configs"]
>>>>>>> test
