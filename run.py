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

    iterations_for_experiment = 500
    exploration_percentages = [0.0, 0.1, 0.2, 0.3]
    results = {} # dict that will contain exploration_percentages as keys, and values would be another dict with trip_overhead and complaints

    try:
        strategy = EmptyStrategy(exemplar)

        for perc in exploration_percentages:
            total_trip_overhead_for_perc = 0
            total_complaints_for_perc = 0

            for i in range(iterations_for_experiment):

                configs = strategy.monitor(with_validation=False)
                configs = configs[-1]
                configs["exploration_percentage"] = perc

                trip_overhead, complaints = strategy.analyze(perc)
                strategy.plan()
                strategy.execute(configs, with_validation=False)

                total_trip_overhead_for_perc += trip_overhead
                total_complaints_for_perc += complaints

                # print(i, total_trip_overhead_for_perc, total_complaints_for_perc, perc)
                print(i, perc)

            results[perc] = {
                "avg_trip_overhead": total_trip_overhead_for_perc / iterations_for_experiment,
                "avg_complaints": total_complaints_for_perc ,
            }
            # print(results)
            
        print(results)

    # try:
    #     strategy = EmptyStrategy(exemplar)
                
    #     while True:
    #         input("Try to adapt?")
    #         strategy.monitor(with_validation=False)
    #         print("monitor ok")
    #         if strategy.analyze():
    #             print("anal ok")
    #             if strategy.plan():
    #                 print("plan ok")
    #                 strategy.execute(strategy.knowledge.plan_data, with_validation=False)
    #                 print("exec ok")
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)