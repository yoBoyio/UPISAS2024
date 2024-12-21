from UPISAS.exemplars.your_exemplar import StepExemplar
from UPISAS.strategies.empty_strategy import MABTripStrategy
import sys
import time
import logging

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Initialize exemplar with proper startup sequence
        exemplar = StepExemplar(auto_start=True)
        time.sleep(3)  # Wait for container
        exemplar.start_run()
        time.sleep(10)  # Wait for service

        # Initialize strategy and get schemas
        strategy = MABTripStrategy(exemplar)
        strategy.get_monitor_schema()
        strategy.get_execute_schema()
        strategy.get_adaptation_options_schema()

        monitored_count = 0
        while True:
            try:
                # Monitor with validation
                logger.info("Monitoring system state...")
                current_config = strategy.monitor(with_validation=False)  # Disable validation temporarily
                monitored_count += 1

                if monitored_count >= 2:
                    logger.info(f"Analyzing after {monitored_count} samples...")
                    
                    if strategy.analyze():
                        selected_arm, new_config = strategy.plan()
                        
                        if new_config:
                            logger.info(f"Executing new config: {new_config}")
                            strategy.execute(new_config, with_validation=False)  # Disable validation temporarily
                            
                            # Verify changes
                            time.sleep(2)
                            updated_config = strategy.monitor(with_validation=False)
                            logger.info(f"Updated configuration: {updated_config}")
                    
                    monitored_count = 0  # Reset counter
                
                time.sleep(5)  # Adaptation interval

            except Exception as e:
                logger.error(f"Error in adaptation loop: {str(e)}")
                time.sleep(5)  # Wait before retry

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    # finally:
    #     exemplar.stop_container()
    #     sys.exit(0)