import serial
import serial.tools.list_ports


def port(vid, pid, serial_number=False):
    vid = int(vid, 16)
    pid = int(pid, 16)

    for i in serial.tools.list_ports.comports():
        if i.vid == vid and i.pid == pid:
            if (serial_number == i.serial_number
                or not serial_number):
                return i.device
    return False

class CodeReader:
    def __init__(self, port):
        if port:
            self.com = serial.Serial(port=port, baudrate=115200)
            if self.com == None:
                raise Exception('2D code reader is not found')
        else:
            raise Exception('No such CodeReader COM port ')

class ALX3601(CodeReader):

    def _read(self):
        return self.com.read().decode('ascii')

    def _readline(self, eol):
        # pyserial > 3.x readline indicate EOL "\n" only.
        buf = []
        while True:
            c = self.com.read().decode('ascii')
            buf.append(c)
            if eol in c:
                return ''.join(buf)

    def command(self, c):
        self.com.write(b'\x1b')  # command start
        self.com.write(c.encode('ascii'))
        self.com.write(b'\x0d')  # command end


    def trigger_read(self):
        self.command('Z')  # trigger
        data = self._readline(eol='\r')
        self.command('Y')  # untrigger
        return data
