import pandas as pd
import os

class SecInfo(object):
    def __init__(self):
        self._filePath = os.getcwd() + '/../info/sec.info.csv'
        self._secInfo = pd.read_csv(self._filePath)

    def update(self):
        self._secInfo.to_csv(self._filePath, index = False)


secInfo = SecInfo()
