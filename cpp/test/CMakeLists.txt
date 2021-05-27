add_executable(tests
    $<TARGET_OBJECTS:common>
    boost_msm_simple.cpp
    boost_msm_choise.cpp
    boost_msm_submachine.cpp
    boost_msm_forward_data.cpp
    checksum.cpp)

target_link_libraries(tests Boost::headers GTest::gmock_main)
