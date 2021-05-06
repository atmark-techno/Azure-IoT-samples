import json
from modules.const import Const
from modules.lib.agent_utils import run_on_bash

class G3M1Lte:
    def __parse_lte(self, config, key):
        try:
            if config['lte'][key] == '':
                return None
            else:
                return config['lte'][key]
        except KeyError:
            return None

    def __read_lte_config(self, filename):
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                device_name = self.__parse_lte(config, 'device_name')
                apn         = self.__parse_lte(config, 'apn')
                username    = self.__parse_lte(config, 'username')
                password    = self.__parse_lte(config, 'password')
                ppp         = self.__parse_lte(config, 'ppp')
                if device_name != 'ttyCommModem':
                    device_name = 'ttyUSB2'
                return (device_name, apn, username, password, ppp)    
        except FileNotFoundError:
            return (None, None, None, None, None)
        except json.JSONDecodeError:
            return (None, None, None, None, None)


    def __init__(self):
        CHAP_DISABLE = ' ppp.refuse-eap true ppp.refuse-chap true ppp.refuse-mschap true ppp.refuse-mschapv2 true  ppp.refuse-pap false'
        (device_name, apn, username, password, ppp) = self.__read_lte_config(Const.NETWORK_FILE)

        if apn is None:
            return

        (_, output) = run_on_bash('nmcli connection show gsm-'+device_name+' | grep gsm.apn')
        if apn in output:
             # always setup
             return

        run_on_bash('nmcli connection delete gsm-'+device_name)

        if ppp == 'chap' or ppp == 'CHAP':
            if username is None or password is None:
                run_on_bash('nmcli connection add type gsm ifname '+device_name+\
                            ' apn '+apn+CHAP_DISABLE)
            else:
                run_on_bash('nmcli connection add type gsm ifname '+device_name+\
                            ' apn '+apn+' user '+username+' password '+password+CHAP_DISABLE)
        else:
            if username is None or password is None:
                run_on_bash('nmcli connection add type gsm ifname '+device_name+' apn '+apn)
            else:
                run_on_bash('nmcli connection add type gsm ifname '+device_name+\
                            ' apn '+apn+' user '+username+' password '+password)
