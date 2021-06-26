#pragma once

#include <vector>


namespace fc {


struct ISender
{
    virtual void send(const std::vector<unsigned char>&) = 0;
    virtual ~ISender() = default;
};


}
