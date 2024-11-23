from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
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
        # strategy.analyze()
        # strategy.get_monitor_schema()
        # strategy.get_adaptation_options_schema()
        # strategy.get_execute_schema()

        while True:
            input("Try to adapt?")
            strategy.monitor(verbose=True)
            if strategy.analyze():
                if strategy.plan():
                    strategy.execute(strategy.knowledge.plan_data,with_validation=False)
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)