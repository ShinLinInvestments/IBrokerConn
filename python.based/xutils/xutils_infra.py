import xmltodict
import os

class ConfigManager:
    def __init__(self, config_path):
        self._cfg_dict = xmltodict.parse(open(os.getcwd() + '/' + config_path).read())

    def __getitem__(self, item):
        return self._cfg_dict[item]

config_manager = ConfigManager('config/config.xml')