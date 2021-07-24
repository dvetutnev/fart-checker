from gas_sensor.sensor import BaseSensor
from gas_sensor.read_packet import readPacket
from gas_sensor.read_sensor import readSensor


class ASerialException(Exception):
    pass
