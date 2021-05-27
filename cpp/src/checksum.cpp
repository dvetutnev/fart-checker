#include "checksum.h"

#include <numeric>
#include <cassert>


unsigned char calcChecksum(const std::vector<unsigned char>& p) {
    assert(p.size() == 8);
    unsigned char result = std::accumulate(std::begin(p), std::begin(p) + 7, 0);
    result = ~result;
    result += 1;
    return result;
}
