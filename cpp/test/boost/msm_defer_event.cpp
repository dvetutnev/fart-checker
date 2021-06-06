#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>


using ::testing::StrictMock;
using ::testing::InSequence;


namespace {


struct Mock
{
    MOCK_METHOD(void, call, (int), ());
};


struct DataEvent
{
    int data;
};

struct DataSentEvent {};


namespace msmf = boost::msm::front;


struct DefFSM : msmf::state_machine_def<DefFSM>
{
    struct WaitDataState : msmf::state<> {};
    struct SendDataState : msmf::state<>
    {
        template <typename Fsm>
        void on_entry(const DataEvent& event, Fsm& fsm) {
            fsm.mock.call(event.data);
        }

        using deferred_events = boost::mpl::vector<DataEvent>;
    };

    using initial_state = WaitDataState;

    struct transition_table : boost::mpl::vector<
                //          Start           Event           Next            Action
                msmf::Row < WaitDataState,  DataEvent,      SendDataState,  msmf::none >,
                msmf::Row < SendDataState,  DataEvent,      msmf::none,     msmf::Defer >,
                msmf::Row < SendDataState,  DataSentEvent,  WaitDataState,  msmf::none >
            > {};

    StrictMock<Mock> mock;
};


using FSM = boost::msm::back::state_machine<DefFSM>;


} // Anonymous namespace


TEST(Boost_MSM_defer, enqueue) {
    FSM fsm;

    EXPECT_CALL(fsm.mock, call(1));

    fsm.start();

    fsm.process_event(DataEvent{1});
    fsm.process_event(DataEvent{2});

    fsm.stop();
}

TEST(Boost_MSM_defer, dequeue) {
    FSM fsm;

    {
        InSequence _;

        EXPECT_CALL(fsm.mock, call(1));
        EXPECT_CALL(fsm.mock, call(2));
        EXPECT_CALL(fsm.mock, call(3));
    }

    fsm.start();

    fsm.process_event(DataEvent{1});
    fsm.process_event(DataEvent{2});
    fsm.process_event(DataEvent{3});

    fsm.process_event(DataSentEvent{});
    fsm.process_event(DataSentEvent{});
    fsm.process_event(DataSentEvent{});

    fsm.stop();
}
