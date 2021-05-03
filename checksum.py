# Project FartCHECKER
# Checksum calculation for Winsen gas sensors
# Dmitriy Vetutnev, 2021


def calc_checksum(packet):
    result = sum(packet[1:7])
    result = ~result
    result += 1
    return result & 0xFF
