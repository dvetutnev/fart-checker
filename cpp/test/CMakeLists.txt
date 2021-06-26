add_executable(tests
    $<TARGET_OBJECTS:common>

    boost/msm_simple.cpp
    boost/msm_choise.cpp
    boost/msm_submachine.cpp
    boost/msm_forward_data.cpp
    boost/msm_defer_event.cpp

    checksum.cpp

    fsm/main.cpp
    fsm/packet_receiver.cpp)

target_link_libraries(tests Boost::headers GTest::gmock_main)
