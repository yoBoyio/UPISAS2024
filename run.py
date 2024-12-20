from UPISAS.exemplars.your_exemplar import StepExemplar
from UPISAS.strategies.empty_strategy import EmptyStrategy
import signal
import sys
import time

if __name__ == '__main__':
    
    exemplar = StepExemplar(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(10)

    try:
        
        strategy = EmptyStrategy(exemplar)
        strategy.monitor(with_validation=False)
        time.sleep(10)

        values = len(strategy.knowledge.monitored_data["tripOverhead"])

        if values >= 40:
            strategy.analyze()
            strategy.execute()
        else:
            print("Not enough data to analyze and execute")
        
        # strategy.get_monitor_schema()
        # strategy.get_adaptation_options_schema()
        # strategy.get_execute_schema()

        while True:
            input("Try to adapt?")
            strategy.monitor(verbose=True)
            if strategy.analyze():
                if strategy.plan():
                    strategy.execute(strategy.knowledge.plan_data,with_validation=False)

    # max_iterations = 1000
    # for iteration in range(max_iterations):
    #     # MONITOR: Gather traffic metrics
    #     trip_overhead, trip_average = monitor()

    #     # Calculate current reward
    #     reward = calculate_reward(trip_overhead, trip_average)

    #     # ANALYZE: Check performance and update feedback count
    #     adjust_parameters, decline_count = analyze(reward, decline_count, reward_threshold, decline_limit)

    #     # PLAN: Calculate UCB scores and select the best arm
    #     ucb_scores = calculate_ucb(rewards, counts, t)
    #     selected_arm, current_config = plan(ucb_scores, rewards, counts, t, arms, decline_count)

    #     # EXECUTE: Apply the selected configuration
    #     EmptyStrategy.execute(EmptyStrategy, current_config, selected_arm, EmptyStrategy.rewards, EmptyStrategy.counts, reward, EmptyStrategy)
        

    #     # KNOWLEDGE: Log system performance
    #     log_performance(iteration, reward, current_config)

    #     # Increment timestep
    #     t += 1
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)