#pragma once


namespace fc {


struct ITimer
{
    virtual void start() = 0;
    virtual void restart() = 0;
    virtual void cancel() = 0;

    virtual ~ITimer() = default;
};


}
