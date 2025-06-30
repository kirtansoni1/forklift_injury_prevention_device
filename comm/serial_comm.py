import serial
import threading
from utils.defines import SERIAL_PORT, SERIAL_BAUDRATE


class SerialComm:
    """
    UART communication with ESP32-S3.
    """

    def __init__(self):
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        self.lock = threading.Lock()
        self.running = False

    def send(self, message: str):
        with self.lock:
            self.ser.write(message.encode('utf-8') + b'\n')

    def receive(self):
        with self.lock:
            if self.ser.in_waiting:
                return self.ser.readline().decode('utf-8').strip()
            return None

    def close(self):
        self.ser.close()
