#include "packet_receiver.h"
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


    using SubMachine = boost::msm::back::state_machine<DefPacketReceiver>;

    using SubMachineEntry = SubMachine::entry_pt<DefPacketReceiver::State::Entry>;
    using SubMachineExit = SubMachine::exit_pt<DefPacketReceiver::State::Exit>;

    struct transition_table : boost::mpl::vector<
            //        Start             Event           Next                Action
            msmf::Row<InitState,        msmf::none,     SubMachineEntry,    msmf::none>,
            msmf::Row<SubMachineExit,   PacketEvent,    InitState,          onExitSubMachine>
    >{};


    std::vector<unsigned char> data;
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

    std::vector<unsigned char> expected = {0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
    ASSERT_EQ(machine.data, expected);
}

TEST(PacketReceiver, invalidChecksum) {
    ASSERT_DEATH({
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
                 }, "");
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

    ASSERT_EQ(machine.count, 2);

    std::vector<unsigned char> expected = {0x01, 0x78, 0x03, 0x00, 0x00, 0x00, 0x00, 0x84};
    ASSERT_EQ(machine.data, expected);
}
