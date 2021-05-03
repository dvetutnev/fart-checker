# Project FartCHECKER
# Test for calculation checksum
# Dmitriy Vetutnev, 2021


import unittest
from checksum import calc_checksum


class TestCheckSum(unittest.TestCase):
    def test_read_command(self):
        packet = b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79'
        expected = 0x79
        result = calc_checksum(packet)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
