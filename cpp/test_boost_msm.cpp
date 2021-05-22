#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>

#include <cstdlib>


using ::testing::InSequence;


namespace simple {


struct Mock
{
    MOCK_METHOD(void, call, (), ());
};


struct FirstEvent {};
struct SecondEvent {};

namespace msmf = boost::msm::front;

struct DefStateMachine : msmf::state_machine_def<DefStateMachine>
{
    struct AState : msmf::state<> {};
    struct BState : msmf::state<> {};
    struct CState : msmf::state<> {};

    using initial_state = AState;


    struct onFirst
    {
        template <typename Fsm, typename Evt, typename SourceState, typename TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.firstMock.call();
        }
    };

    struct onSecond
    {
        template <class Fsm,class Evt,class SourceState,class TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.secondMock.call();
        }
    };


    template<typename Fsm, typename Event>
    void no_transition(const Event&, const Fsm&, int) {
        std::abort();
    }


    struct transition_table : boost::mpl::vector<
            //        Start     Event           Next
            msmf::Row<AState,   FirstEvent,     BState,     onFirst>,
            msmf::Row<BState,   SecondEvent,    CState,     onSecond>,
            msmf::Row<CState,   SecondEvent,    CState,     msmf::none>
    >{};


    Mock firstMock;
    Mock secondMock;
};


using StateMachine = boost::msm::back::state_machine<DefStateMachine>;


} // namespace simple


TEST(Boost_MSM_simple, invalidEvent) {
    simple::StateMachine stateMachine;
    stateMachine.start();

    ASSERT_DEATH({ stateMachine.process_event(simple::SecondEvent{}); }, "");
}

TEST(Boost_MSM_simple, actions) {
    simple::StateMachine stateMachine;

    {
        InSequence _;
        EXPECT_CALL(stateMachine.firstMock, call());
        EXPECT_CALL(stateMachine.secondMock, call());
    }

    stateMachine.start();

    stateMachine.process_event(simple::FirstEvent{});
    stateMachine.process_event(simple::SecondEvent{});
    stateMachine.process_event(simple::SecondEvent{});

    stateMachine.stop();
}


namespace choise {

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


    template<typename Fsm, typename Event>
    void no_transition(const Event&, const Fsm&, int) {
        std::abort();
    }


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


} // namespace choise


TEST(Boost_MSM_choise, _) {
    choise::StateMachine stateMachine;

    {
        InSequence _;

        EXPECT_CALL(stateMachine.mock, onEvent());
        EXPECT_CALL(stateMachine.mock, onRepeat());
        EXPECT_CALL(stateMachine.mock, onEvent());
        EXPECT_CALL(stateMachine.mock, onDone());
    }

    stateMachine.start();

    stateMachine.process_event(choise::Event{});
    stateMachine.process_event(choise::Event{});

    stateMachine.stop();
}
