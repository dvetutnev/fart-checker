# Project FartCHECKER
# Test for calculation checksum
# Dmitriy Vetutnev, 2021


from uart import calc_checksum


def test_read_command():
    packet = b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79'
    assert calc_checksum(packet) == 0x79


def test_set_qa_command_ze03():
    packet = b'\xFF\x01\x78\x03\x00\x00\x00\x00\x84'
    assert calc_checksum(packet) == 0x84


def test_set_qa_command_ze08():
    packet = b'\xFF\x01\x78\x41\x00\x00\x00\x00\x46'
    assert calc_checksum(packet) == 0x46

def test_data():
    packet = b'\xFF\x86\x00\x00\x00\x00\x00\x00\x7A'
    assert calc_checksum(packet) == 0x7A

def test_data2():
    packet = b'\xFF\x86\x00\x03\x00\x00\x00\x00\x77'
    assert calc_checksum(packet) == 0x77
