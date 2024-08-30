# file_utils.py
import os
from datetime import datetime, timedelta

def clear_input_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def round_to_nearest_hour(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return datetime(dt.year, dt.month, dt.day, dt.hour)

def arrondir_heure_plus_proche(datetime_format):
    if datetime_format.minute >= 30:
        return datetime_format.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        return datetime_format.replace(minute=0, second=0, microsecond=0)