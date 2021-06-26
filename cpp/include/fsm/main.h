#pragma once

#include "run_worker_event.h"

#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>


namespace fc {


namespace msmf = boost::msm::front;


struct DefMainFSM : boost::msm::front::state_machine_def<DefMainFSM>
{
    //DefMainFSM(IFactoryRunWorkerEvent& f) : factory{f} {}

private:
    IFactoryRunWorkerEvent& factory;
};


using MainFSM = boost::msm::back::state_machine<DefMainFSM>;


}
