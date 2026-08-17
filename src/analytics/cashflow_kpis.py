from pathlib import Path
import pandas as pd

def load_output(path):
    return pd.read_excel(path)
