#include "checksum.h"
#include <gtest/gtest.h>


TEST(calcChecksum, command) {
    std::vector<unsigned char> p = {0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
    ASSERT_EQ(fc::calcChecksum(p), 0x79);
}

TEST(calcChecksum, ze03) {
    std::vector<unsigned char> p = {0x01, 0x78, 0x03, 0x00, 0x00, 0x00, 0x00, 0x84};
    ASSERT_EQ(fc::calcChecksum(p), 0x84);
}

TEST(calcChecksum, ze08) {
    std::vector<unsigned char> p = {0x01, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0x46};
    ASSERT_EQ(fc::calcChecksum(p), 0x46);
}
