import time
from numpy import median
from UPISAS.exemplars.your_exemplar import StepExemplar
from UPISAS.strategies.empty_strategy import EmptyStrategy

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
amount_of_runs = 300

if __name__ == "__main__":
    rounds = 0
    exemplar = StepExemplar(auto_start=True)
    exemplar.start_run()
    time.sleep(30)

    try:
        strategy = EmptyStrategy(exemplar)
        median_saved = []

        while rounds < amount_of_runs + 1:
            time.sleep(4)
            count = 0
            rounds += 1
            print(f"--------------- NEW ROUND {rounds} ---------------")

            try:
                # Monitor values until there are 30 values for calculating median
                while count < 30:
                    print("Monitoring...")
                    cs = strategy.monitor(with_validation=False)
                    print(f"Current state: {len(cs)}")
                    time.sleep(0.5)

                    try:
                        if strategy.knowledge.monitored_data:
                            count += 1
                            print(f"Waiting until 30 values have been gathered: {count}")
                    except KeyError:
                        count = 0

                # Analyze the monitored data
                print("Analyzing...")
                strategy.analyze()

                # Planning phase
                print("Planning...")
                _, action_schema = strategy.plan()
                median_saved.append(strategy.knowledge.analysis_data["total_trip_overhead_average"])
                print(f"Median total trip overhead average: {median(median_saved)}")

                # Execute the selected configuration
                print("Executing...")
                strategy.execute(action_schema, with_validation=False)

            except Exception as main_error:
                print(f"Error during main loop: {main_error}")
                for attempt in range(MAX_RETRIES):
                    print(f"Retrying in {RETRY_DELAY} seconds (attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)

                    try:
                        while count < 30:
                            print("Monitoring (retry)...")
                            strategy.monitor(with_validation=False)
                            time.sleep(0.5)
                            count = len(strategy.knowledge.monitored_data["total_trip_overhead_average"])
                            print(f"Waiting until 30 values have been gathered: {count}")

                        print("Analyzing (retry)...")
                        strategy.analyze()

                        print("Planning (retry)...")
                        _, action_schema = strategy.plan()
                        median_saved.append(strategy.knowledge.analysis_data["total_trip_overhead_average"])
                        print(f"Median total trip overhead average: {median(median_saved)}")

                        print("Executing (retry)...")
                        strategy.execute(action_schema, with_validation=False)
                        break  # Exit retry loop if successful

                    except Exception as retry_error:
                        print(f"Error during retry: {retry_error}")
                else:
                    print("Max retries reached. Returning to main loop.")

        # Print the final median values
        print("\nFinal Median Values of Total Trip Overhead Average:")
        print(median_saved)

    except Exception as e:
        print(e)
        exemplar.stop()
        sys.exit(0)