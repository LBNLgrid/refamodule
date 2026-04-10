import json
import pandas as pd

def load_conductors():
    data = pd.read_csv("input_data_raw/conductors.csv")
    return data


