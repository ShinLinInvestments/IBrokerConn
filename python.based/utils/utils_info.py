import pandas as pd
import os

class SecInfo(object):
    def __init__(self):
        self._filePath = os.getcwd() + '/../info/sec.info.csv'
        self._secInfo = pd.read_csv(self._filePath)

    def ibContract2msuk(self):
        return 1

secInfo = SecInfo()
