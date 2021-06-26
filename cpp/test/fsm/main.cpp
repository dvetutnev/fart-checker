#include "fsm/main.h"
#include <gmock/gmock.h>


using ::testing::StrictMock;
using ::testing::SaveArg;
using ::testing::Return;
using ::testing::DoAll;


namespace {


struct MockSerial : fc::ISerial
{
    MOCK_METHOD(void, open, (), (override));
    MOCK_METHOD(void, read, (), (override));
    MOCK_METHOD(void, writeSwitchMode, (), (override));
    MOCK_METHOD(void, writeRequest, (), (override));
    MOCK_METHOD(void, close, (), (override));
};

struct MockTimer : fc::ITimer
{
    MOCK_METHOD(void, start, (), (override));
    MOCK_METHOD(void, restart, (), (override));
    MOCK_METHOD(void, cancel, (), (override));
};

struct MockSender : fc::ISender
{
    MOCK_METHOD(void, send, (const std::vector<unsigned char>&), ());
};

struct MockFactory : fc::IFactoryRunWorkerEvent
{
    MOCK_METHOD(fc::RunWorkerEvent, create, (Emitters), (override));
};


} // Anonyomus namespace


TEST(MainFSM, _) {
    MockFactory factory;
    fc::IFactoryRunWorkerEvent::Emitters emitters;
    fc::RunWorkerEvent event{
                std::make_shared<StrictMock<MockSerial>>(),
                nullptr,
                nullptr,
                nullptr
    };
    EXPECT_CALL(factory, create)
            .WillOnce(DoAll(SaveArg<0>(&emitters), Return(event)))
            ;

    //fc::MainFSM fsm{factory};
    fc::MainFSM fsm{};
}
