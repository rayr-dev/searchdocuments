# utilities/output.py

import os
#local
from utilities.logging_setup import diag

from datetime import datetime

def create_timestamped_folder(base_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(base_path, timestamp)
    os.makedirs(folder, exist_ok=True)
    diag("OUTPUT/create_timestamped_folder: timestamp {folder}")
    return folder
