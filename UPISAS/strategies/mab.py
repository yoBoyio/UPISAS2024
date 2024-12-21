import numpy as np

class MAB:
    def __init__(self, arms):
        """
        Initialize the Multi-Armed Bandit (MAB) logic.
        Args:
            arms (list): A list of arm configurations (e.g., different parameter sets).
        """
        self.arms = arms
        self.num_arms = len(arms)
        self.counts = [0] * self.num_arms  # How many times each arm has been used
        self.rewards = [0.0] * self.num_arms  # Total reward for each arm
        self.t = 1  # Global counter for UCB calculations

    def update_rewards(self, arm_index, reward):
        """
        Update the rewards and counts for a given arm.
        Args:
            arm_index (int): The index of the selected arm.
            reward (float): The reward obtained for selecting the arm.
        """
        self.counts[arm_index] += 1
        self.rewards[arm_index] += reward
        self.t += 1

    def calculate_ucb(self):
        """
        Compute UCB (Upper Confidence Bound) scores for all arms.
        Returns:
            list: UCB scores for each arm.
        """
        ucb_scores = []
        for i in range(self.num_arms):
            if self.counts[i] == 0:
                # If an arm has never been selected, give it infinite score
                ucb_scores.append(float('inf'))
            else:
                average_reward = self.rewards[i] / self.counts[i]
                confidence = np.sqrt((2.0 * np.log(self.t)) / self.counts[i])
                ucb_scores.append(average_reward + confidence)
        return ucb_scores

    def select_arm(self):
        """
        Select the arm with the highest UCB score.
        Returns:
            tuple: (index of the selected arm, selected arm configuration)
        """
        ucb_scores = self.calculate_ucb()
        best_arm_index = np.argmax(ucb_scores)
        return best_arm_index, self.arms[best_arm_index]