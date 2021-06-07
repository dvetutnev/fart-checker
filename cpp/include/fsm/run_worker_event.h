#pragma once

#include "serial.h"
#include "watchdog.h"
#include "sender.h"

#include <memory>


namespace fc {


struct RunWorkerEvent
{
    std::shared_ptr<ISerial> serial;
    std::shared_ptr<IWatchdog> watchdog;
    std::shared_ptr<ISender> sender;
};


}
