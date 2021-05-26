#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>


using ::testing::InSequence;


namespace {


struct Mock
{
    MOCK_METHOD(void, onEvent, (), ());
    MOCK_METHOD(void, onRepeat, (), ());
    MOCK_METHOD(void, onDone, (), ());
};


struct Event {};

namespace msmf = boost::msm::front;

struct DefStateMachine : msmf::state_machine_def<DefStateMachine>
{
    struct State : msmf::state<> {};
    struct Choise : msmf::state<> {};
    struct End : msmf::state<> {};

    using initial_state = State;

    struct onEvent
    {
        template <typename Fsm, typename Evt, typename SourceState, typename TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.count++;
            fsm.mock.onEvent();
        }
    };

    struct onRepeat
    {
        template <class Fsm,class Evt,class SourceState,class TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.mock.onRepeat();
        }
    };

    struct onDone
    {
        template <class Fsm,class Evt,class SourceState,class TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.mock.onDone();
        }
    };


    struct Guard
    {
        template <class Fsm,class Evt,class SourceState,class TargetState>
        bool operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) const {
            return fsm.count == 2;
        }
    };


    struct transition_table : boost::mpl::vector<
            //        Start     Event       Next    Action      Guard
            msmf::Row<State,    Event,      Choise, onEvent,    msmf::none>,
            msmf::Row<Choise,   msmf::none, State,  onRepeat,   msmf::none>,
            msmf::Row<Choise,   msmf::none, End,    onDone,     Guard>
    >{};

    int count = 0;
    Mock mock;
};


using StateMachine = boost::msm::back::state_machine<DefStateMachine>;


} // Anonymouse namespace


TEST(Boost_MSM_choise, _) {
    StateMachine stateMachine;

    {
        InSequence _;

        EXPECT_CALL(stateMachine.mock, onEvent());
        EXPECT_CALL(stateMachine.mock, onRepeat());
        EXPECT_CALL(stateMachine.mock, onEvent());
        EXPECT_CALL(stateMachine.mock, onDone());
    }

    stateMachine.start();

    stateMachine.process_event(Event{});
    stateMachine.process_event(Event{});

    stateMachine.stop();
}
