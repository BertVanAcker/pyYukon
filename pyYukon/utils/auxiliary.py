import yaml

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