# Project FartCHECKER
# Tests Receiver (Winsen gas sensors)
# Dmitriy Vetutnev, 2021


import pytest
from uart import Receiver, calc_checksum


def test_checksum():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    assert calc_checksum(packet) == 0x56


def test_normal():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    rx = Receiver()
    rx.put(packet)

    assert rx.is_done()
    assert rx.get_data() == packet[1:8]


def test_empty():
    rx = Receiver()
    assert not rx.is_done()
    with pytest.raises(Exception):
        rx.get_data()


def test_wait_start_byte():
    packet = b'\x00\x56\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    rx = Receiver()
    rx.put(packet)

    assert rx.is_done()
    assert rx.get_data() == packet[3:10]


def test_without_start_byte():
    packet = b'\x00\x56\x42\x86\x04\x20\x00\x00\x00\x00\x56'
    rx = Receiver()
    rx.put(packet)

    assert not rx.is_done()


def test_chunks():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    rx = Receiver()

    rx.put(packet[:4])
    assert not rx.is_done()

    rx.put(packet[4:])
    assert rx.is_done()
    assert rx.get_data() == packet[1:8]


def test_invalid_checksum():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x57'
    rx = Receiver()

    rx.put(packet)
    assert not rx.is_done()


def test_separated_checksum():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    rx = Receiver()

    rx.put(packet[:8])
    assert not rx.is_done()

    rx.put(packet[8:])
    assert rx.is_done()


def test_separated_invalid_checksum():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x65'
    rx = Receiver()

    rx.put(packet[:8])
    rx.put(packet[8:])
    assert not rx.is_done()


def test_restart_after_invalid_checksum():
    rx = Receiver()

    invalid_checksum = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x65'
    rx.put(invalid_checksum)
    assert not rx.is_done()

    normal_checksum = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    rx.put(normal_checksum)
    assert rx.is_done()


from transitions import Machine


def test_state_machine():
    class Matter(object):
        pass
    lump = Matter()

    states = ["wait_start", "receiving", "done"]
    transitions = [
        {"trigger": "start", "source": "wait_start", "dest": "receiving"},
        {"trigger": "done", "source": "receiving", "dest": "done"}
    ]


    machine = Machine(model=lump, states=states, transitions=transitions, initial="wait_start")

    assert lump.is_wait_start()
    assert not lump.is_receiving()
    assert not lump.is_done()

    lump.start()

    assert not lump.is_wait_start()
    assert lump.is_receiving()

    lump.done()

    assert not lump.is_wait_start()
    assert not lump.is_receiving()
    assert lump.is_done()
