#pragma once

#include <vector>


namespace fc {


struct ISerial
{
    virtual void open() = 0;
    virtual void read() = 0;
    virtual void write(const std::vector<unsigned char>&) = 0;
    virtual void close() = 0;

    virtual ~ISerial() = default;
};


}
