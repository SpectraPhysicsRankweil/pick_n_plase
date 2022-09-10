import serial
import time
import ast

import atexit

from rpi_hardware_pwm import HardwarePWM


PORT = '/dev/ttyACM0'
BAUDRATE = 115200


class Placer:
    def __init__(self):
        self._serial = serial.Serial(PORT, BAUDRATE, timeout=None)
        self._pwm = HardwarePWM(pwm_channel=0, hz=50)
        self._pwm.start(0)
        self._offset_X = 0
        self._offset_Y = 0
        self._offset_Z = 0
        self._speed = 3600
        self._idle = True
        self._last_angle = 5
        self._wait_for_init()
        self.rotate(0)

    def _wait_for_init(self):
        print('Wait for printer init ...')
        start = time.monotonic()
        while True:
            line = self._serial.readline().decode()
            # if not line:
            #     break
            if line:
                print(line, end='')
            if line == 'ok\r\n':
                print('Printer initialized!')
                break
            if time.monotonic() - start > 30:
                print('timed out ... hope we don\'t break anything :X')
                break

    def _homing_and_define_new_offsets(self):
        print('Do X an Z homing ...')
        self.request('G28 XZ')
        time.sleep(20)
        print('Set new X and Z zero positions')
        self.position_absolute(25, 0 , 125)
        self.request('G92 X0')
        self.request('G92 Z0')
        time.sleep(5)
        self.current_position()


    def _set_initial_offsets(self):
        print(f'Set initial offsets ({self._offset_X}, {self._offset_Y}, {self._offset_Z})')
        self.request('G90')
        self.request(f'G1 X{self._offset_X} Y{self._offset_Y} Z{self._offset_Z} F{self._speed}')

    def set_speed(self, speed):
        self._speed = speed

    def home(self):
        self.request('G28 X Y')
        self.position_absolute(0, 0, 100)

    def emergency_stop(self):
        self.request('M112')

    def position_absolute(self, x, y, z):
        self.request(b'G90')
        x += self._offset_X
        y += self._offset_Y
        z += self._offset_Z
        self._idle = False
        answer = self.request(f'G1 X{x} Y{y} Z{z} F{self._speed}')
        print(answer)
        self.request('M400')
        self._idle = True
        # self._serial.write(f'G1 X{x} Y{y} Z{z} F{self._speed}\r'.encode())

    def position_and_rotate(self, x, y, z, alpha):
        self.position_absolute(x, y, z)
        self.rotate(alpha)

    def _position_relative(self, x, y, z):
        self._serial.write(b'G91\r')
        self._serial.write(f'G1 X{x} Y{y} Z{z} F{self._speed}\r'.encode())

    def current_position(self):
        positions = self.request('M114')
        x = float(positions[2:positions.index('Y')-1])
        y = float(positions[positions.index('Y')+2:positions.index('Z')-1])
        z = float(positions[positions.index('Z')+2:positions.index('E')-1])
        return (x, y, z)

    def rotate(self, value):
        if value > 180:
            value = 180
        if value != self._last_angle:
            # time.sleep(1)
            pwm = value * (11.2 - 1.9) / 180 + 1.9
            self._pwm.change_duty_cycle(pwm)
            self._last_angle = value
            # time.sleep(1)

    def request(self, message):
        self._serial.flushInput()
        self._serial.write(f'{message}\r'.encode())
        return self._read()

    def _read(self):
        received = b''
        while True:
            byte = self._serial.read(1)
            if len(byte) < 1:
                raise TimeoutError
            if byte == b'\r' or byte == b'\n':
                if received[-2:] == b'ok':
                    return received.decode()
            else:
                received += byte

    def exit_handler(self):
        self.position_absolute(0, 0, 0)
        self._serial.close()
