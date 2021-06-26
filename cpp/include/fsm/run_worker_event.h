#pragma once

#include "serial.h"
#include "timer.h"
#include "sender.h"

#include <memory>
#include <functional>


namespace fc {


struct RunWorkerEvent
{
    std::shared_ptr<ISerial> serial;
    std::shared_ptr<ISerial> timer;
    std::shared_ptr<ISerial> watchdog;
    std::shared_ptr<ISender> sender;
};

struct IFactoryRunWorkerEvent
{
    struct Emitters
    {
        std::function<void(unsigned char)> onRead;
        std::function<void()> onWrite;
        std::function<void()> onPortError;
        std::function<void()> onTimer;
        std::function<void()> onWatchdog;
    };

    virtual RunWorkerEvent create(Emitters) = 0;

    virtual ~IFactoryRunWorkerEvent() = default;
};


}
