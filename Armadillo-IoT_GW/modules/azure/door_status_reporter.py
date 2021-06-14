import asyncio
import json
import datetime
from datetime import datetime
from enum import Enum
from time import time
from time import localtime, strftime
from serial import Serial
from serial.tools.list_ports import comports
from azure.iot.device import Message

from modules.lib.report import Report
from modules.lib.active_reporter import ActiveReporter


def get_port(vid, pid):
    vid = int(vid, 16)
    pid = int(pid, 16)

    for i in comports():
        if i.vid == vid or i.pid == pid:
            return i.device
    return None

class ReceiverState(Enum):
    WAIT_DATA   = 1,
    READY_REPORT= 2

class DoorStatusReporter(ActiveReporter):
    DOOR_OPEN_CLOSE = "door_open_close"
    SID = "sid"
    IS_ON = "is_on"
    NOTIFI_TIME = "notified_time"

    DOOR_STATE_MAP = "door_state_map"
    DOOR_STATE = "door_state"
#    mapKey : sid
#    mapValue : door_state (type Object)
    CHANGE_TIME = "change_time"
    LAST_SENSE_TIME = "last_sense_time"

    TZ_INFO = strftime("%z", localtime())
    INVALID_TIME = datetime.fromtimestamp(0).isoformat() + "Z"

    def __init__(self, report_queue, 
                 report_repository, 
                 disable_whitelist,
                 component_name,
                 port=None):
        super().__init__(report_queue, report_repository)
        self._component_name = component_name
        self._curr_state     = ReceiverState.WAIT_DATA
        # receive data
        self._sid_sensor_list = []
        self._disable_whitelist = disable_whitelist
        self._ready = True
        self._data_list = []
        self._head_list = []
        self._opt_list = []
        self._byte_count = 0
        self._data_len = 0
        self._opt_len = 0
        self._notifi_sensor = {
            DoorStatusReporter.SID: "",
            DoorStatusReporter.IS_ON: False,
            DoorStatusReporter.NOTIFI_TIME: DoorStatusReporter.INVALID_TIME
            }
        # sonsor dict
        self._sensor_dict = {}
        if port is None:
            port = get_port("0403","6001")
            if port is None:
                raise Exception("weighin machine's COM port is not found")
        self._receiver  = Serial(port, 57600, timeout=1.0)
        self._receiver.close()

    def receiver_update_prop(self):
        prop = {DoorStatusReporter.DOOR_STATE_MAP: self._sensor_dict}
        return prop

    def set_sid_sensor_list(self, value):
        for key in value:
            if value[key] == None:
                self._sid_sensor_list.remove(key)
                break
            if not key in self._sid_sensor_list:
                self._sid_sensor_list.append(key)

    def request_stop(self):
        super().request_stop()

    def _before_loop(self):
        self._receiver.open()

    def _after_loop(self):
        self._receiver.close()

    def _check_exit_sid(self, curr_sid):
        for sid in self._sid_sensor_list:
            if sid == curr_sid:
                return True
        return False

    def _push_sensor_dict(self, sid, is_on, datetime):
        if not sid in self._sensor_dict:
            self._sensor_dict[sid] = {
                DoorStatusReporter.IS_ON: is_on,
                DoorStatusReporter.CHANGE_TIME: datetime,
                DoorStatusReporter.LAST_SENSE_TIME: datetime
                }
        else:
             sensor = self._sensor_dict[sid]
             if sensor[DoorStatusReporter.IS_ON] == is_on:
                 sensor[DoorStatusReporter.LAST_SENSE_TIME] = datetime
             else:
                 sensor[DoorStatusReporter.IS_ON] = is_on
                 sensor[DoorStatusReporter.CHANGE_TIME] = datetime
                 sensor[DoorStatusReporter.LAST_SENSE_TIME] = datetime
             self._sensor_dict[sid] = sensor

    def _handle_state(self):
        if ReceiverState.WAIT_DATA == self._curr_state:
            self._handle_wait_data()
        elif ReceiverState.READY_REPORT == self._curr_state:
            self._handle_ready_report()

    def _do_transit_action(self, next_state):
        return

    def _handle_wait_data(self):
        bytes = self._receiver.read().hex()

        if bytes == "":
            return
        
        if bytes == '55' and self._ready:
            self._byte_count, self._data_len ,self._opt_len = 0,0,0
            self._data_list,self._head_list,self._opt_list = [],[],[]
            self._ready = False
        self._byte_count += 1

        if 2 <= self._byte_count <= 5:
            self._head_list.append(bytes)

        if self._byte_count == 5:
            self._data_len = int(self._head_list[1],16)
            self._opt_len  = int(self._head_list[2],16)

        if 7 <= self._byte_count <= (6+self._data_len): # data
            self._data_list.append(bytes)

        if (7+self._data_len) <= self._byte_count <= (6+self._data_len+self._opt_len): # optional data
            self._opt_list.append(bytes)

        if self._byte_count == (6+self._data_len+self._opt_len+1):
            self._ready = True
            dt = datetime.now().isoformat() + DoorStatusReporter.TZ_INFO
            sid = ''.join(self._data_list[1:5])

            if not self._check_door_status_data(self._data_list):
                return

            if not self._disable_whitelist:
                if not self._check_exit_sid(sid):
                    return
            
            if self._check_door_status_data(self._data_list):
                is_on = self._is_on(self._data_list)
                # send telemetry sid, is_on, notifi_time
                self._notifi_sensor[DoorStatusReporter.SID] = sid
                self._notifi_sensor[DoorStatusReporter.IS_ON] = is_on
                self._notifi_sensor[DoorStatusReporter.NOTIFI_TIME] = dt
                # send read only prop sid, is_on, change_time, last_change_time
                # check sensor dict
                self._push_sensor_dict(sid, is_on, dt)
                self._transit_state(ReceiverState.READY_REPORT)

    def _handle_ready_report(self):
        # make report and enqueue it
        report = Report.report_now(
            'measurement',
            type=DoorStatusReporter.DOOR_OPEN_CLOSE,
            key=DoorStatusReporter.DOOR_STATE,
            value={
                DoorStatusReporter.SID: self._notifi_sensor[DoorStatusReporter.SID],
                DoorStatusReporter.IS_ON: self._notifi_sensor[DoorStatusReporter.IS_ON],
                DoorStatusReporter.NOTIFI_TIME: self._notifi_sensor[DoorStatusReporter.NOTIFI_TIME]
                },
            unit='door_sensor_status'
        )
        report.reported_data['$.sub'] = self._component_name
        self._report_queue.push(report)

        sensor_info = self._sensor_dict[self._notifi_sensor[DoorStatusReporter.SID]]

        door_state_report = Report.report_now(
            'measurement',
            type=DoorStatusReporter.DOOR_STATE,
            key=DoorStatusReporter.DOOR_STATE,
            value={
                DoorStatusReporter.SID: self._notifi_sensor[DoorStatusReporter.SID],
                DoorStatusReporter.IS_ON: sensor_info[DoorStatusReporter.IS_ON],
                DoorStatusReporter.CHANGE_TIME: sensor_info[DoorStatusReporter.CHANGE_TIME],
                DoorStatusReporter.LAST_SENSE_TIME: sensor_info[DoorStatusReporter.LAST_SENSE_TIME]
                },
            unit='door_sensor_status'
        )
        self._report_queue.push(door_state_report)

        # update status
        self._transit_state(ReceiverState.WAIT_DATA)

    @staticmethod
    def _check_door_status_data(bytes_data):
        if bytes_data[5] == '08' or bytes_data[5] == '09':
            return True
        else:
            return False

    @staticmethod
    def _is_on(bytes_data):
        if bytes_data[5] == '08':
            return True
        elif  bytes_data[5] == '09':
            return False

#
# End of File
#

