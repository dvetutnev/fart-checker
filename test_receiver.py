# Project FartCHECKER
# Tests Receiver (Winsen gas sensors)
# Dmitriy Vetutnev, 2021


import pytest
from unittest.mock import Mock
from uart import Receiver, calc_checksum
from transitions import Machine


def test_checksum():
    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    assert calc_checksum(packet) == 0x56


def test_mock_callback():
    cb = Mock()
    cb(b'\x86\x04\x20\x00\x00\x00\x00')
    cb.assert_called_with(b'\x86\x04\x20\x00\x00\x00\x00')


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


def test_normal():
    cb = Mock()
    rx = Receiver(cb)

    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    for b in packet:
        rx.put(b)

    cb.assert_called_with(b'\x04\x20\x00\x00\x00\x00')


def test_not_cb_called_before_done():
    cb = Mock()
    rx = Receiver(cb)

    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'

    for b in packet[:4]:
        rx.put(b)
    cb.assert_not_called()

    for b in packet[4:]:
        rx.put(b)
    cb.assert_called_with(b'\x04\x20\x00\x00\x00\x00')


def test_invalid_checksum():
    cb = Mock()
    rx = Receiver(cb)

    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x47'
    for b in packet:
        rx.put(b)

    cb.assert_not_called()


def test_restart_after_invalid_checksum():
    cb = Mock()
    rx = Receiver(cb)

    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x47'
    for b in packet:
        rx.put(b)

    packet = b'\xFF\x86\x04\x20\x00\x00\x00\x00\x56'
    for b in packet:
        rx.put(b)

    cb.assert_called_with(b'\x86\x04\x20\x00\x00\x00\x00')
