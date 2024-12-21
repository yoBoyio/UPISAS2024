from UPISAS.exemplars.your_exemplar import StepExemplar
from UPISAS.strategies.empty_strategy import MABTripStrategy
import sys
import time

if __name__ == '__main__':
    exemplar = StepExemplar(auto_start=True)
    time.sleep(3)
    exemplar.start_run()
    time.sleep(3)

    try:
        strategy = MABTripStrategy(exemplar)

        strategy.get_monitor_schema()
        strategy.get_execute_schema()
        strategy.get_adaptation_options_schema()
        while True:
            if strategy.analyze():
                new_config = strategy.plan()  # Unpack returned tuple
                if new_config:  # Check if we got a valid configuration
                    strategy.execute(new_config, with_validation=True)
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)