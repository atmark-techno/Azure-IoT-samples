import json
from modules.const import Const
from modules.lib.agent_utils import run_on_bash


class G3M1Wireless:
    def __parse_wireless(self, config, key):
        try:
            if config['wireless'][key] == '':
                return None
            else:
                return config['wireless'][key]
        except KeyError:
            return None

    def __read_wireless_config(self, filename):
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                essid       = self.__parse_wireless(config, 'essid')
                passphrase  = self.__parse_wireless(config, 'passphrase')
                return (essid, passphrase)    
        except FileNotFoundError:
            return (None, None)
        except json.JSONDecodeError:
            return (None, None)

    def __init__(self):
        (essid, passphrase) = self.__read_wireless_config(Const.NETWORK_FILE)

        if None in (essid, passphrase):
            return

        (result,_) = run_on_bash('nmcli connection show '+essid)
        if result == 0:
            return   

        run_on_bash('nmcli device wifi connect '+essid+' password '+passphrase)
