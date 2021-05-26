#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>


using ::testing::InSequence;


namespace {


struct Mock
{
    MOCK_METHOD(void, onEvent, (int), ());
};


namespace msmf = boost::msm::front;

struct DefMachine : msmf::state_machine_def<DefMachine>
{
    // States
    struct InitState : msmf::state<> {};
    struct EndState : msmf::state<> {};

    using initial_state = InitState;

    // Events
    struct StartSubMachineEvent {};

    // Actions
    struct enterSubMachine
    {
        template <typename Fsm, typename Evt, typename SourceState, typename TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.mock.onEvent(1);
        }
    };

    struct exitSubMachine
    {
        template <class Fsm,class Evt,class SourceState,class TargetState>
        void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
            fsm.mock.onEvent(2);
        }
    };

    // SubMachine, using as State
    struct DefSubMachine : msmf::state_machine_def<DefSubMachine>
    {
        Mock* outerMock = nullptr;

        template<typename Event, typename Fsm>
        void on_entry(const Event&, Fsm& fsm) {
            outerMock = &(fsm.mock);
            std::cout << "DefSubMachine::on_entry: " << &fsm << std::endl;
        }

        // States
        struct EntryState : msmf::entry_pseudo_state<> {};
        struct WriteState : msmf::state<> {};
        struct ReadState : msmf::state<> {};
        struct ProcessResultState : msmf::state<> {};
        struct ExitState : msmf::exit_pseudo_state<msmf::none> {};

        //using initial_state = WriteState;
        using initial_state = boost::mpl::vector<EntryState>;

        // Events
        struct WriteEvent {};
        struct ReadEvent {};

        // Actions
        struct onWrite
        {
            template <typename Fsm, typename Evt, typename SourceState, typename TargetState>
            void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
                fsm.outerMock->onEvent(10);
            }
        };

        struct onRead
        {
            template <typename Fsm, typename Evt, typename SourceState, typename TargetState>
            void operator()(const Evt&, Fsm& fsm, SourceState&,TargetState&) {
                fsm.outerMock->onEvent(20);
            }
        };


        struct transition_table : boost::mpl::vector<
                //        Start         Event       Next        Action
                msmf::Row<EntryState,   boost::any, WriteState, msmf::none>,
                msmf::Row<WriteState,   WriteEvent, ReadState,  onWrite>,
                msmf::Row<ReadState,    ReadEvent,  ExitState,  onRead>
        >{};

    }; // DefSubMachine

    using SubMachine = boost::msm::back::state_machine<DefSubMachine>;

    using SubMachineEntry = SubMachine::entry_pt<DefSubMachine::EntryState>;
    using SubMachineExit = SubMachine::exit_pt<DefSubMachine::ExitState>;

    struct transition_table : boost::mpl::vector<
            //        Start             Event                   Next                Action
            msmf::Row<InitState,        StartSubMachineEvent,   SubMachineEntry,    enterSubMachine>,
            msmf::Row<SubMachineExit,   msmf::none,             EndState,           exitSubMachine>
    >{};

    Mock mock;
};


using Machine = boost::msm::back::state_machine<DefMachine>;


} // Anonymous namespace


TEST(Boost_MSM_submachine, _) {
    Machine machine;

    {
        InSequence _;

        EXPECT_CALL(machine.mock, onEvent(1));
        EXPECT_CALL(machine.mock, onEvent(10));
        EXPECT_CALL(machine.mock, onEvent(20));
        EXPECT_CALL(machine.mock, onEvent(2));
    }

    std::cout << &machine << std::endl;

    machine.start();

    machine.process_event(DefMachine::StartSubMachineEvent{});

    machine.process_event(DefMachine::DefSubMachine::WriteEvent{});
    machine.process_event(DefMachine::DefSubMachine::ReadEvent{});

    machine.stop();
}
