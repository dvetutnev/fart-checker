#pragma once


namespace fc {


struct IWatchdog
{
    virtual void kick() = 0;
    virtual ~IWatchdog() = default;
};

struct ITimer
{
    virtual void start() = 0;
    virtual ~ITimer() = default;
};


}
