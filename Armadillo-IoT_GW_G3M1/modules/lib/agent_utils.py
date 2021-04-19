import uuid
from subprocess import STDOUT, CalledProcessError, check_output


def run_on_bash(cmd, timeout=None):
    if timeout is not None:
        cmd = 'timeout --kill-after {} {} {}'.format(timeout, timeout, cmd)

    try:
        #print('run command {}'.format(cmd))
        output = check_output(
            cmd,
            stderr=STDOUT,
            shell=True,
            executable='/bin/bash'
        )
        returncode = 0
    except CalledProcessError as e:
        output = e.output
        returncode = e.returncode

    return (returncode, output.decode('utf-8'))

def get_mac():
    return '{:012x}'.format(uuid.getnode()).upper()
