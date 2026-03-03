# utilities/logging_setup.py

# System
import os
from datetime import datetime
import logging

def init_logging(output_dir=None, diagnostic=False):
    """
    Initializes logging for both CLI and GUI modes.
    If output_dir is provided, logs go there. Otherwise, logs go to cwd.
    """
    diag("LOGGING_SETUP/init_logging: Started")
    # Ensure directory exists
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.getcwd()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(output_dir, f"reconciliation_{timestamp}.log")

    # Clear existing handlers (important for GUI re-runs)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    level = logging.DEBUG if diagnostic else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler()  # CLI only; GUI ignores console
        ]
    )

    diag("LOGGING_SETUP/init_logging: Ended")
    return log_path

def dump_diagnostics(data, output_dir, filename="diagnostics_dump.json"):
    """
    Writes structured diagnostic data to a JSON file in the output directory.
    Safe for GUI and CLI. Uses the unified logging system.
    """
    import json
    try:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        diag(f"Diagnostic dump written: {path}")
        return path

    except Exception as error:
        logging.info(f"Failed to write diagnostic dump.-[{error}]") # Keep logging for Unit Testing
        return None

def diag(msg):
    logging.debug(msg)
