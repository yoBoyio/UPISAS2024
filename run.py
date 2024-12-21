from UPISAS.exemplars.your_exemplar import StepExemplar
from UPISAS.strategies.empty_strategy import MABTripStrategy
import sys
import time

if __name__ == '__main__':
    # Initialize exemplar
    exemplar = StepExemplar(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(10)

    try:
        # Initialize strategy
        strategy = MABTripStrategy(exemplar)

        # Get initial schemas
        strategy.get_monitor_schema()
        strategy.get_execute_schema()
        strategy.get_adaptation_options_schema()

        monitored_count = 0  # Track number of monitored values
        while True:
            # Monitor current state
            print("Monitoring...")
            current_config = strategy.monitor(with_validation=True)
            monitored_count += 1  # Increment monitored values count

            # Check if we have 30 new monitored values before analyzing
            if monitored_count >= 30:
                print(f"Collected {monitored_count} values. Starting analysis and planning...")
                
                # Analyze and plan
                if strategy.analyze():
                    selected_arm, new_config = strategy.plan()  # Get both arm and config
                    
                    if new_config and new_config != current_config:
                        print(f"Applying new config: {new_config}")
                        strategy.execute(new_config, with_validation=False)

                        # Verify changes
                        time.sleep(2)  # Wait for changes to take effect
                        updated_config = strategy.monitor(with_validation=False)
                        print(f"Updated config: {updated_config}")
                
                # Reset monitored count
                monitored_count = 0
            else:
                print(f"Waiting for more data... Monitored values count: {monitored_count}")

            time.sleep(5)  # Wait before the next monitoring cycle

    except (Exception, KeyboardInterrupt) as e:
        print(f"Error: {str(e)}")
        exemplar.stop_container()
        sys.exit(0)