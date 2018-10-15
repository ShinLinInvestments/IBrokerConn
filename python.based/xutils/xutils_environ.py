import os
import logging
from xutils.xutils_infra import *

os.environ['TZ'] = config_manager['xutils']['time_zone']

logging.basicConfig(format = '%(asctime)s|%(levelname)s|%(funcName)s|%(thread)d|%(filename)s:%(lineno)d|%(message)s',
                    datefmt='%Y%m%d.%H%M%S.%Z')
xlog = logging.getLogger('SLFD')
xlog.setLevel(level = config_manager['xutils']['log_level'])

