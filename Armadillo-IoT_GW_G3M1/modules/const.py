class Const:
    SETTING_PATH = '/etc/aiotg3-powermonitor/'
    CONFIG_FILE  = SETTING_PATH+'parameter.json'
    CLOUD_FILE   = SETTING_PATH+'things_cloud.json'
    NETWORK_FILE = SETTING_PATH+'network.json'
    SYSLOG_ORIG_PATH = '/var/log/syslog'
    LOG_DIR      = '/tmp/things_cloud/'
    SYSLOG_PATH  = LOG_DIR+'syslog.log'
    DMESG_PATH   = LOG_DIR+'dmesg.log'
    DEFAULT_CLOUD_REPORT_INTERVAL_SEC = 30
    SLEEP_NO_REPORT_SEC = 10
    MODBUS_PARAM_FILE = SETTING_PATH+'modbus_param.json'
    BULK_REPORT_COUNT = 20
