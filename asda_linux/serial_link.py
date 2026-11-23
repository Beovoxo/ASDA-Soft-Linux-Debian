from dataclasses import dataclass
from serial.tools import list_ports
import serial

@dataclass
class PortInfo:
    device: str
    description: str

def available_ports():
    return [PortInfo(p.device, p.description or "Serial device")
            for p in list_ports.comports()]

class SerialLink:
    """Safe port lifecycle only. No undocumented drive commands are sent."""
    def __init__(self):
        self._serial = None

    @property
    def is_open(self):
        return self._serial is not None and self._serial.is_open

    def open(self, device, baudrate=9600):
        self.close()
        self._serial = serial.Serial(
            port=device, baudrate=baudrate, bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
            timeout=0.25, write_timeout=0.25
        )

    def close(self):
        if self._serial:
            try:
                self._serial.close()
            finally:
                self._serial = None
