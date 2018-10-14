import pandas as pd
import os

def read_csv(path, sdatetime, edatetime):
    filenames = os.listdir(path)