#include "fsm/packet_receiver.h"
#include <gtest/gtest.h>


namespace {


using namespace fc;


struct DefMachine : msmf::state_machine_def<DefMachine>
{
    // States
    struct InitState : msmf::state<> {};
    struct EndState : msmf::state<> {};

    using initial_state = InitState;

    // Actions
    struct onExitSubMachine
    {
        template <typename Fsm, typename SourceState, typename TargetState>
        void operator()(const PacketEvent& event, Fsm& fsm, SourceState&, TargetState&) {
            fsm.data = event.packet;
            fsm.count++;
        }
    };


    using SubMachine = boost::msm::back::state_machine<DefPacketReceiverFSM>;

    using SubMachineEntry = SubMachine::entry_pt<DefPacketReceiverFSM::State::Entry>;
    using SubMachineExit = SubMachine::exit_pt<DefPacketReceiverFSM::State::Exit>;

    struct transition_table : boost::mpl::vector<
            //        Start             Event           Next                Action
            msmf::Row<InitState,        msmf::none,     SubMachineEntry,    msmf::none>,
            msmf::Row<SubMachineExit,   PacketEvent,    InitState,          onExitSubMachine>
    >{};


    std::optional< std::vector<unsigned char> > data;
    int count = 0;
};


using Machine = boost::msm::back::state_machine<DefMachine>;


} // Anonymous namespace


TEST(PacketReceiver, normal) {
    Machine machine;

    machine.start();

    machine.process_event(ByteEvent{0xFF});

    machine.process_event(ByteEvent{0x01});
    machine.process_event(ByteEvent{0x86});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x79});

    machine.stop();

    ASSERT_TRUE(machine.data);

    std::vector<unsigned char> expected = {0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
    ASSERT_EQ(*(machine.data), expected);
}

TEST(PacketReceiver, invalidChecksum) {
    Machine machine;

    machine.start();

    machine.process_event(ByteEvent{0xFF});

    machine.process_event(ByteEvent{0x01});
    machine.process_event(ByteEvent{0x86});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x97});

    machine.stop();

    ASSERT_FALSE(machine.data);
}

TEST(PacketReceiver, reenter) {
    Machine machine;

    machine.start();

    machine.process_event(ByteEvent{0xFF});

    machine.process_event(ByteEvent{0x01});
    machine.process_event(ByteEvent{0x86});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x79});

    machine.process_event(ByteEvent{0xFF});

    machine.process_event(ByteEvent{0x01});
    machine.process_event(ByteEvent{0x78});
    machine.process_event(ByteEvent{0x03});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x00});
    machine.process_event(ByteEvent{0x84});

    machine.stop();

    ASSERT_TRUE(machine.data);

    ASSERT_EQ(machine.count, 2);

    std::vector<unsigned char> expected = {0x01, 0x78, 0x03, 0x00, 0x00, 0x00, 0x00, 0x84};
    ASSERT_EQ(*(machine.data), expected);
}
