#pragma once

#include "checksum.h"

#include <boost/msm/front/state_machine_def.hpp>
#include <boost/msm/front/functor_row.hpp>
#include <boost/msm/back/state_machine.hpp>

#include <optional>


namespace fc {


struct ByteEvent
{
    ByteEvent(unsigned char b) : byte{b} {}
    unsigned char byte;
};

struct EmptyResultEvent {};

struct ResultEvent
{
    ResultEvent(const std::vector<unsigned char>& p) : packet{p} {}
    std::vector<unsigned char> packet;
};

struct PacketEvent
{
    PacketEvent(EmptyResultEvent) : packet{std::nullopt} {}
    PacketEvent(const ResultEvent& r) : packet{r.packet} {}

    std::optional< std::vector<unsigned char> > packet;
};


namespace msmf = boost::msm::front;


struct DefPacketReceiver : msmf::state_machine_def<DefPacketReceiver>
{
    std::vector<unsigned char> buffer;

    struct State
    {
        struct Entry : msmf::entry_pseudo_state<> {};
        struct WaitStart : msmf::state<> {};
        struct Receive : msmf::state<> {};
        struct CheckLength : msmf::state<> {};
        struct CheckChecksum : msmf::state<> {};
        struct Result : msmf::state<> {};
        struct Exit : msmf::exit_pseudo_state<PacketEvent> {};
    };

    using initial_state = boost::mpl::vector<State::Entry>;

    // Actions
    struct onStart
    {
        template <typename Fsm, typename SourceState, typename TargetState>
        void operator()(const ByteEvent&, Fsm& fsm, SourceState&, TargetState&) {
            fsm.buffer.clear();
        }
    };

    struct onReceive
    {
        template <typename Fsm, typename SourceState, typename TargetState>
        void operator()(const ByteEvent& event, Fsm& fsm, SourceState&, TargetState&) {
            fsm.buffer.push_back(event.byte);
        }
    };

    struct onResult
    {
        template <typename Fsm, typename Event, typename SourceState, typename TargetState>
        void operator()(const Event&, Fsm& fsm, SourceState&, TargetState&) {
            const std::vector<unsigned char>& p = fsm.buffer;
            fsm.process_event(ResultEvent{p});
        }
    };

    struct onInvalidChecksum
    {
        template <typename Fsm, typename Event, typename SourceState, typename TargetState>
        void operator()(const Event&, Fsm& fsm, SourceState&, TargetState&) {
            fsm.process_event(EmptyResultEvent{});
        }
    };

    // Guards
    struct isStartByte
    {
        template <typename Fsm, typename SourceState, typename TargetState>
        bool operator()(const ByteEvent& event, Fsm&, SourceState&, TargetState&) const {
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

    struct isValidChecksum
    {
        template <typename Fsm, typename Event, typename SourceState, typename TargetState>
        bool operator()(const Event&, Fsm& fsm, SourceState&, TargetState&) const {
            const std::vector<unsigned char>& p = fsm.buffer;
            return calcChecksum(p) == fsm.buffer.back();
        }
    };

    struct transition_table : boost::mpl::vector<
            //        Start                 Event               Next                    Action              Guard
            msmf::Row<State::Entry,         msmf::none,         State::WaitStart,       msmf::none,         msmf::none>,

            msmf::Row<State::WaitStart,     ByteEvent,          State::Receive,         onStart,            isStartByte>,
            msmf::Row<State::Receive,       ByteEvent,          State::CheckLength,     onReceive,          msmf::none>,

            msmf::Row<State::CheckLength,   msmf::none,         State::Receive,         msmf::none,         msmf::none>,
            msmf::Row<State::CheckLength,   msmf::none,         State::CheckChecksum,   msmf::none,         isDone>,

            msmf::Row<State::CheckChecksum, msmf::none,         State::Result,          onInvalidChecksum,  msmf::none>,
            msmf::Row<State::CheckChecksum, msmf::none,         State::Result,          onResult,           isValidChecksum>,

            msmf::Row<State::Result,        EmptyResultEvent,   State::Exit,            msmf::none,         msmf::none>,
            msmf::Row<State::Result,        ResultEvent,        State::Exit,            msmf::none,         msmf::none>
    >{};
};


} // namespace fc
