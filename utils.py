import json
import pandas as pd

def load_conductors():
    data = pd.read_csv("conductors.csv")
    return data

def convert_to_float(data):
    if isinstance(data, dict):
        return {key: convert_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_float(value) for value in data]
    elif isinstance(data, str):
        try:  # Attempt to convert string to float
            return float(data)
        except ValueError:
            return data  # Return unchanged if conversion fails
    return data  # Non-numeric data is returned unchanged


def convert_to_int(data, keys):
    if isinstance(data, dict):
        return {key: int(value) if key in keys else convert_to_int(value, keys) for key, value in data.items()}
    else:
        return data
