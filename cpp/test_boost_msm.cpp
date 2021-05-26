#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>


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


namespace submachine {


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


} // namespace submacine


TEST(Boost_MSM_submachine, _) {
    submachine::Machine machine;

    {
        InSequence _;

        EXPECT_CALL(machine.mock, onEvent(1));
        EXPECT_CALL(machine.mock, onEvent(10));
        EXPECT_CALL(machine.mock, onEvent(20));
        EXPECT_CALL(machine.mock, onEvent(2));
    }

    std::cout << &machine << std::endl;

    machine.start();

    machine.process_event(submachine::DefMachine::StartSubMachineEvent{});

    machine.process_event(submachine::DefMachine::DefSubMachine::WriteEvent{});
    machine.process_event(submachine::DefMachine::DefSubMachine::ReadEvent{});

    machine.stop();
}


namespace  forward_data {


using Packet = std::vector<unsigned char>;

struct Mock
{
    MOCK_METHOD(void, call, (const Packet&), ());
};


namespace msmf = boost::msm::front;


struct ByteEvent
{
    ByteEvent(unsigned char b) : byte{b} {}
    unsigned char byte;
};

struct ResultEvent
{
    ResultEvent(const Packet& p) : packet{p} {}
    Packet packet;
};

struct PacketEvent
{
    PacketEvent(const ResultEvent& d) : packet{d.packet} {}
    Packet packet;
};

struct DefMachine : msmf::state_machine_def<DefMachine>
{
    // States
    struct InitState : msmf::state<> {};
    struct EndState : msmf::state<> {};

    using initial_state = InitState;

    // Actions
    struct onExitSubMachine
    {
        template <typename Event, typename Fsm, typename SourceState, typename TargetState>
        void operator()(const Event& event, Fsm& fsm, SourceState&, TargetState&) {
            static_assert(std::is_same_v<Event, PacketEvent>);
            fsm.mock.call(event.packet);
        }
    };

    // SubMachine, using as State
    struct DefSubMachine : msmf::state_machine_def<DefSubMachine>
    {
        struct State
        {
            struct Entry : msmf::entry_pseudo_state<> {};
            struct WaitStart : msmf::state<> {};
            struct Receive : msmf::state<> {};
            struct Result : msmf::state<> {};
            struct Exit : msmf::exit_pseudo_state<PacketEvent> {};
        };

        using initial_state = boost::mpl::vector<State::Entry>;

        // Actions
        struct onReceive
        {
            template <typename Event, typename Fsm, typename SourceState, typename TargetState>
            void operator()(const Event& event, Fsm& fsm, SourceState&, TargetState&) {
                static_assert(std::is_same_v<Event, ByteEvent>);
                std::cout << (int) event.byte << std::endl;
                fsm.buffer.push_back(event.byte);
            }
        };

        struct onResult
        {
            template <typename Event, typename Fsm, typename SourceState, typename TargetState>
            void operator()(const Event& event, Fsm& fsm, SourceState&, TargetState&) {
                static_assert(std::is_same_v<Event, ByteEvent>);
                const Packet& p = fsm.buffer;
                fsm.process_event(ResultEvent{p});
            }
        };

        // Guards
        struct isStartByte
        {
            template <typename Fsm, typename Event, typename SourceState, typename TargetState>
            bool operator()(const Event& event, Fsm&, SourceState&, TargetState&) const {
                static_assert(std::is_same_v<Event, ByteEvent>);
                return event.byte == 0xFF;
            }
        };

        struct isDone
        {
            template <typename Fsm, typename Event, typename SourceState, typename TargetState>
            bool operator()(const Event&, Fsm& fsm, SourceState&, TargetState&) const {
                return fsm.buffer.size() == 8;
            }
        };


        struct transition_table : boost::mpl::vector<
                //        Start             Event           Next                Action      Guard
                msmf::Row<State::Entry,     boost::any,     State::WaitStart,   msmf::none, msmf::none>,

                msmf::Row<State::WaitStart, ByteEvent,      State::Receive,     msmf::none, isStartByte>,
                msmf::Row<State::Receive,   ByteEvent,      State::Receive,     onReceive,  msmf::none>,
                msmf::Row<State::Receive,   ByteEvent,      State::Result,      onResult,   isDone>,

                msmf::Row<State::Result,    ResultEvent,    State::Exit,        msmf::none, msmf::none>
        >{};

        Packet buffer;

    }; // DefSubMachine

    using SubMachine = boost::msm::back::state_machine<DefSubMachine>;

    using SubMachineEntry = SubMachine::entry_pt<DefSubMachine::State::Entry>;
    using SubMachineExit = SubMachine::exit_pt<DefSubMachine::State::Exit>;

    struct transition_table : boost::mpl::vector<
            //        Start             Event           Next                Action
            msmf::Row<InitState,        msmf::none,     SubMachineEntry,    msmf::none>,
            msmf::Row<SubMachineExit,   PacketEvent,    EndState,           onExitSubMachine>
    >{};

    Mock mock;
};


using Machine = boost::msm::back::state_machine<DefMachine>;


} // namespace forward_data


TEST(Boost_MSM_forward_data, _) {
    using namespace forward_data;

    Machine machine;

    const Packet expectedPacket = {1, 2, 3, 4, 5, 6, 7, 8};
    EXPECT_CALL(machine.mock, call(expectedPacket));

    machine.start();

    machine.process_event(ByteEvent{0xFF});

    machine.process_event(ByteEvent{1});
    machine.process_event(ByteEvent{2});
    machine.process_event(ByteEvent{3});
    machine.process_event(ByteEvent{4});
    machine.process_event(ByteEvent{5});
    machine.process_event(ByteEvent{6});
    machine.process_event(ByteEvent{7});
    machine.process_event(ByteEvent{8});

    machine.stop();
}

