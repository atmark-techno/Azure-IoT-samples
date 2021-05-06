import datetime
from datetime import datetime
from time import localtime, strftime
from dataclasses import dataclass

from modules.lib.alarm import Alarm
from modules.lib.alarm_condition_parser import parse_alarm_condition
from modules.reporters.kmn1_wattage_reporter import Kmn1WattageReporter

from modules.azure.model_dev_base import ModelDevBase
from modules.azure.model_config_powermonitor import ModelConfigPowerMonitor

"""
@dataclass
class PowerMonitorAlert:
    current_status : bool
    num_occurrence : int
    last_occur_time : datetime
"""


class ModelDevG3LPowerMonitor(ModelDevBase):
    ALERT = "powermonitor_alert"
    CURR_STAT       = "current_status"
    NUN_OCCUR       = "num_occurrence"
    LAST_OCCUR_TIME = "last_occur_time"

    TZ_INFO = strftime("%z", localtime())
    INVALID_TIME = datetime.fromtimestamp(0).isoformat() + "Z"

    def __init__(self, modelConfig):
        super().__init__(modelConfig)
        self._props[ModelDevG3LPowerMonitor.ALERT] = {
            ModelDevG3LPowerMonitor.CURR_STAT: False,
            ModelDevG3LPowerMonitor.NUN_OCCUR: 0,
            ModelDevG3LPowerMonitor.LAST_OCCUR_TIME: ModelDevG3LPowerMonitor.INVALID_TIME
        }
        self._wattageReporter = None

    def model_id(self):
        return "dtmi:atmark_techno:Armadillo:IoT_GW_G3L_PowerMonitor;1"

    def set_prop(self, name, value):
        if name == ModelConfigPowerMonitor.INTERVAL:
            value = self._modelConfig.set_powermonitor_interval(value)
            if self._wattageReporter:
                self._wattageReporter.set_interval(value)
        elif name == ModelConfigPowerMonitor.ALERT_CONF:
            enabled = self._modelConfig.alert_conf()[ModelConfigPowerMonitor.ENABLED]
            value = self._modelConfig.set_alert_config(value)
            is_enable = value[ModelConfigPowerMonitor.ENABLED]
            if enabled and (not is_enalbe):
                self._wattageReporter.set_alarm_condition(None)
            if is_enable:
                self._wattageReporter.set_alarm_condition([
                    ModelDevG3LPowerMonitor._make_alarm_condition(
                        value[ModelConfigPowerMonitor.THRESHOLD]
                    )
                ])
        else:
            value = super().set_prop(name, value)
        return value

    def powermonitor_alert(self):
        return self._props[ModelDevG3LPowerMonitor.ALERT]

    def process_alarm(self, alarm):
        if not self._modelConfig.alert_conf()[ModelConfigPowerMonitor.ENABLED]:
            return None
        alert_stat = self.powermonitor_alert()
        if alert_stat[ModelDevG3LPowerMonitor.CURR_STAT] == alarm.is_activate:
            return None
        alert_stat[ModelDevG3LPowerMonitor.CURR_STAT] = alarm.is_activate
        if alarm.is_activate:
            alarm_time = alarm.time.isoformat() + ModelDevG3LPowerMonitor.TZ_INFO
            alert_stat[ModelDevG3LPowerMonitor.NUN_OCCUR] += 1
            alert_stat[ModelDevG3LPowerMonitor.LAST_OCCUR_TIME] = alarm_time

        return {ModelDevG3LPowerMonitor.ALERT: alert_stat}

    def _aux_props(self):
        props = super()._aux_props()
        conf = self._modelConfig
        props.append((ModelConfigPowerMonitor.ALERT_CONF, conf.alert_conf()))
        props.append((ModelConfigPowerMonitor.INTERVAL, conf.powermonitor_interval()))
        return props

    def _make_reporters(self, config):
        reporters = super()._make_reporters(config)
        wattageReporter = Kmn1WattageReporter("/dev/ttymxc1", parity="N", stopbits=2)
        wattageReporter.set_interval(config.powermonitor_interval())
        reporters.append(wattageReporter)
        self._wattageReporter = wattageReporter

        return reporters

    def _get_command_method(self, name):
        if (name == "clear_alert"):
            return self._command_clear_alert
        else:
            return super()._get_command_method(name)

    async def _command_clear_alert(self, params):
        if 0 == self._props[ModelDevG3LPowerMonitor.ALERT][ModelDevG3LPowerMonitor.NUN_OCCUR]:
            return (True, None)
        self._props[ModelDevG3LPowerMonitor.ALERT] = {
            ModelDevG3LPowerMonitor.CURR_STAT: False,
            ModelDevG3LPowerMonitor.NUN_OCCUR: 0,
            ModelDevG3LPowerMonitor.LAST_OCCUR_TIME: ModelDevG3LPowerMonitor.INVALID_TIME
        }
        return (True, self._post_clear_alert)
    #
    # Note: command handler method must be async.
    #       ('21. 4/26, koga)

    def _post_clear_alert(self):
        self.report_repository().send_updated_prop(self.powermonitor_alert())

    def _make_alarm_condition(threshold):
        condition = {
            'type': 'too_many',
            'description': 'Wattage is too high',
            'generate_on': {
                'condition': ('wattage > ' + str(threshold)),
                'hysteresis': '1'
            },
            'clear_on': {
                'condition': ('wattage <= ' + str(threshold)),
                'hysteresis': '1'
            }
        }
        return parse_alarm_condition(condition)


#
# End of File
#
