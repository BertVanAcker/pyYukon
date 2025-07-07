import json

import yaml


import threading
import time

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def replace_wildcard(path_template: str, id_value: str) -> str:
    """
    Replaces the first occurrence of '*' in the path_template with id_value.

    Parameters:
        path_template (str): The string containing a '*', e.g., 'YUKON/*/ENABLE'.
        id_value (str): The value to replace '*' with.

    Returns:
        str: The modified string with '*' replaced.
    """
    return path_template.replace("*", id_value, 1)



class PeriodicThread(threading.Thread):
    def __init__(self, interval, function, *args, **kwargs):
        super().__init__()
        self.interval = interval  # in seconds
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            start_time = time.time()
            self.function(*self.args, **self.kwargs)
            elapsed = time.time() - start_time
            time_to_wait = self.interval - elapsed
            if time_to_wait > 0:
                time.sleep(time_to_wait)

    def stop(self):
        self.stop_event.set()

def formatMessage(module="BOARD",action="None",value="None"):

    data = {
        "module": module,
        "action": action,
        "value": value
    }
    json_data = json.dumps(data)
    return json_data