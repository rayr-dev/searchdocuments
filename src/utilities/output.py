# utilities/output.py

import os

from datetime import datetime

def create_timestamped_folder(base_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(base_path, timestamp)
    os.makedirs(folder, exist_ok=True)
    return folder
