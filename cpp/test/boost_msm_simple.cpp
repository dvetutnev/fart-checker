#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>


using ::testing::InSequence;


namespace {


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


} // Anonymouse namespace


TEST(Boost_MSM_simple, invalidEvent) {
    StateMachine stateMachine;
    stateMachine.start();

    ASSERT_DEATH({ stateMachine.process_event(SecondEvent{}); }, "");
}

TEST(Boost_MSM_simple, actions) {
    StateMachine stateMachine;

    {
        InSequence _;

        EXPECT_CALL(stateMachine.firstMock, call());
        EXPECT_CALL(stateMachine.secondMock, call());
    }

    stateMachine.start();

    stateMachine.process_event(FirstEvent{});
    stateMachine.process_event(SecondEvent{});
    stateMachine.process_event(SecondEvent{});

    stateMachine.stop();
}
