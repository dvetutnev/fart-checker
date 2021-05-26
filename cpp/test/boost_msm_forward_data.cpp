#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <gmock/gmock.h>


namespace {


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


} // Anonymous_namespace


TEST(Boost_MSM_forward_data, _) {
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
