#include "fsm/packet_receiver.h"

#include <boost/asio.hpp>
#include <date/tz.h>

#include <iostream>
#include <cstdlib>


namespace fc {


unsigned int ppm(const std::vector<unsigned char>& p) {
    return p[1] * 256 + p[2];
}

void printPacket(const std::vector<unsigned char>& p) {
    auto tp = date::zoned_time{
            date::current_zone(),
            std::chrono::system_clock::now()
    };

    std::cout << tp  << ' ' << ppm(p) << " ppm" << std::endl;
}


struct DefMachine : msmf::state_machine_def<DefMachine>
{
    // States
    struct InitState : msmf::state<> {};

    using initial_state = InitState;

    // Actions
    struct onPacket
    {
        template <typename Fsm, typename SourceState, typename TargetState>
        void operator()(const PacketEvent& event, Fsm& fsm, SourceState&, TargetState&) {
            std::vector<unsigned char> p = *(event.packet);
            printPacket(p);
        }
    };


    using SubMachine = boost::msm::back::state_machine<DefPacketReceiverFSM>;

    using SubMachineEntry = SubMachine::entry_pt<DefPacketReceiverFSM::State::Entry>;
    using SubMachineExit = SubMachine::exit_pt<DefPacketReceiverFSM::State::Exit>;

    struct transition_table : boost::mpl::vector<
            //        Start             Event           Next                Action
            msmf::Row<InitState,        msmf::none,     SubMachineEntry,    msmf::none>,
            msmf::Row<SubMachineExit,   PacketEvent,    InitState,          onPacket>
    >{};
};


using Machine = boost::msm::back::state_machine<DefMachine>;


} // namespace fc


int main() {
    boost::asio::io_context ioContext;
    boost::asio::serial_port port{ioContext};

    port.open("/dev/ttyUSB0");
    port.set_option(boost::asio::serial_port::baud_rate{9600});

    fc::Machine machine;
    machine.start();

    unsigned char c;

    for (;;) {
        boost::asio::read(port, boost::asio::buffer(&c, 1));
        machine.process_event(fc::ByteEvent{c});
    }

    return EXIT_SUCCESS;
}
