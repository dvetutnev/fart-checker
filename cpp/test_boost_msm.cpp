#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>

#include <cstdlib>


using ::testing::InSequence;


struct Mock
{
    MOCK_METHOD(void, call, (), ());
};


TEST(GMock, normal) {
    Mock mock1;
    Mock mock2;

    {
        InSequence _;

        EXPECT_CALL(mock1, call());
        EXPECT_CALL(mock2, call());
    }

    mock1.call();
    mock2.call();
}

TEST(GMock, DISABLED_failed) {
    Mock mock1;
    Mock mock2;

    {
        InSequence _;

        EXPECT_CALL(mock1, call());
        EXPECT_CALL(mock2, call());
    }

    mock2.call();
    mock1.call();
}


namespace simple {


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
        template <class Fsm,class Evt,class SourceState,class TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            std::cout << "onFirst event" << std::endl;
            fsm.firstMock.call();
        }
    };

    struct onSecond
    {
        template <class Fsm,class Evt,class SourceState,class TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            std::cout << "onSecond event" << std::endl;
            fsm.secondMock.call();
        }
    };


    template<typename Fsm, typename Event>
    void no_transition(const Event&, const Fsm&, int);


    struct transition_table : boost::mpl::vector<
            //        Start     Event           Next
            msmf::Row<AState,   FirstEvent,     BState,     onFirst>,
            msmf::Row<BState,   SecondEvent,    CState,     onSecond>,
            msmf::Row<CState,   SecondEvent,    CState,     msmf::none>
    >{};


    Mock firstMock;
    Mock secondMock;
};

template<typename Fsm, typename Event>
void DefStateMachine::no_transition(const Event&, const Fsm&, int) {
    std::abort();
}


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
