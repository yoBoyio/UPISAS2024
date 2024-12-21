from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
import time
import statistics
import logging
import pandas as pd

from UPISAS.strategies.empty_strategy import MABTripStrategy

from UPISAS.exemplars.your_exemplar import StepExemplar



class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name:                       str             = "new_runner_experiment"

    """The path in which Experiment Runner will create a folder with the name `self.name`, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path:        Path            = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use `OperationType.AUTO`."""
    operation_type:             OperationType   = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms:    int             = 1000

    exemplar = None
    strategy = None
    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
    def __init__(self):
        """Executes immediately after program start, on config load"""

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN       , self.before_run       ),
            (RunnerEvents.START_RUN        , self.start_run        ),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT         , self.interact         ),
            (RunnerEvents.STOP_MEASUREMENT , self.stop_measurement ),
            (RunnerEvents.STOP_RUN         , self.stop_run         ),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT , self.after_experiment )
        ])
        self.run_table_model = None  # Initialized later

        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        factor1 = FactorModel("exploration_percentage", [0.1, 0.2, 0.3])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            exclude_variations=[
            ],
            data_columns=['configs']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        output.console_log("Config.before_experiment() called!")

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        self.exemplar = StepExemplar(auto_start=True)
        self.strategy = MABTripStrategy(self.exemplar)
        time.sleep(3)
        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""
        
        self.exemplar.start_run()
        time.sleep(10)  # Wait for service
        output.console_log("Config.start_run() called!")

    def start_measurement(self, context: RunnerContext) -> None:
        """Perform any activity required for starting measurements."""
        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""
        time_slept = 0
        self.strategy.get_monitor_schema()
        self.strategy.get_adaptation_options_schema()
        self.strategy.get_execute_schema()

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        monitored_count = 0
        while time_slept < 5000:
            
            try:
                # Monitor with validation
                logger.info("Monitoring system state...")
                current_config = self.strategy.monitor(with_validation=False)  # Disable validation temporarily
                monitored_count += 1

                if monitored_count >= 2:
                    logger.info(f"Analyzing after {monitored_count} samples...")
                    
                    if self.strategy.analyze():
                        selected_arm, new_config = self.strategy.plan()
                        
                        if new_config:
                            logger.info(f"Executing new config: {new_config}")
                            self.strategy.execute(new_config, with_validation=False)  # Disable validation temporarily
                            
                            # Verify changes
                            time.sleep(2)
                            updated_config = self.strategy.monitor(with_validation=False)
                            logger.info(f"Updated configuration: {updated_config}")
                            self.save_results(context=context, data=updated_config, run_number=monitored_count )
                    monitored_count = 0  # Reset counter
                
            except Exception as e:
                logger.error(f"Error in adaptation loop: {str(e)}")
                time.sleep(5)  # Wait before retry

            time.sleep(3)
            time_slept+=3


        output.console_log("Config.interact() called!")

    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""

        output.console_log("Config.stop_measurement called!")

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        self.exemplar.stop_container()
        output.console_log("Config.stop_run() called!")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Parse and process any measurement data here.
        You can also store the raw measurement data under `context.run_dir`
        Returns a dictionary with keys `self.run_table_model.data_columns` and their values populated"""

        output.console_log("Config.populate_run_data() called!")

        basicRevenue = 1
        optRevenue = 1.5
        serverCost = 10
        
        precision = 1e-5
        mon_data = self.strategy.knowledge.monitored_data
        utilities = []
        print("MON DATA")
        print(mon_data)
        for i in range(len(mon_data["max_servers"])):

            maxServers = int(mon_data["max_servers"][i])
            arrivalRateMean = mon_data["arrival_rate"][i]
            dimmer = mon_data["dimmer_factor"][i]
            maxThroughput = maxServers * self.strategy.MAX_SERVICE_RATE
            avgServers = mon_data["servers"][i]
            avgResponseTime = (mon_data["basic_rt"][i] * mon_data["basic_throughput"][i] + mon_data["opt_rt"][i] * mon_data["opt_throughput"][i]) / (mon_data["basic_throughput"][i] + mon_data["opt_throughput"][i])

            Ur = (arrivalRateMean * ((1 - dimmer) * basicRevenue + dimmer * optRevenue))
            Uc = serverCost * (maxServers - avgServers)
            UrOpt = arrivalRateMean * optRevenue
            utility = 0

            if(avgResponseTime <= self.strategy.STEP_THRESHOLD and Ur >= UrOpt - precision):
                utility = Ur + Uc
            else:                
                if(avgResponseTime <= self.strategy.STEP_THRESHOLD):
                    utility = Ur
                else:
                    utility = min(0.0, arrivalRateMean - maxThroughput) * optRevenue
            utilities.append(utility)
        
        return {"utility" : utilities}

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""
        output.console_log("Config.after_experiment() called!")


    def save_results(self, context: RunnerContext, data: dict, run_number: int) -> None:
        output.console_log("Config.populate_run_data() called!")

        # Extract data from the input dictionary
        car_stats = data.get("car_stats", {})
        configs = data.get("configs", {})

        # Ensure both car_stats and configs have data
        if not car_stats or not configs:
            print("Car stats or configs data is missing. Aborting save.")
            return

        # Create a row combining car_stats and configs
        row = {
            'step': car_stats.get('step', ''),
            'tick_duration': car_stats.get('tick_duration', ''),
            'routing_duration': car_stats.get('routing_duration', ''),
            'driving_car_counter': car_stats.get('driving_car_counter', ''),
            'total_trip_average': car_stats.get('total_trip_average', ''),
            'total_trips': car_stats.get('total_trips', ''),
            'total_trip_overhead_average': car_stats.get('total_trip_overhead_average', ''),
            'total_complaints': car_stats.get('total_complaints', ''),
            'exploration_percentage': configs.get('exploration_percentage', ''),
            'route_random_sigma': configs.get('route_random_sigma', ''),
            'max_speed_and_length_factor': configs.get('max_speed_and_length_factor', ''),
            'average_edge_duration_factor': configs.get('average_edge_duration_factor', ''),
            'freshness_update_factor': configs.get('freshness_update_factor', ''),
            'freshness_cut_off_value': configs.get('freshness_cut_off_value', ''),
            're_route_every_ticks': configs.get('re_route_every_ticks', ''),
            'total_car_counter': configs.get('total_car_counter', ''),
            'edge_average_influence': configs.get('edge_average_influence', ''),
            '_run_id': f'run{run_number}_repetition_0',
            '__done': 'DONE'
        }

        # Convert the row to a DataFrame
        df = pd.DataFrame([row])

        # Specify the path to the CSV file
        run_table_path = context.run_dir / 'run_table.csv'

        # Append the row to the CSV file, creating the file if it doesn't exist
        df.to_csv(run_table_path, mode='a', header=not run_table_path.exists(), index=False)

        print(f"Data successfully written to {run_table_path}.")
