from gas_sensor.sensor import Measure, BaseSensor, ZE03
from gas_sensor.read_packet import readPacket
from gas_sensor.read_sensor import readSensor
from gas_sensor.calc_checksum import calcChecksum


class ASerialException(Exception):
    pass
