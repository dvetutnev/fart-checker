add_executable(test
    boost_msm_simple.cpp
    boost_msm_choise.cpp
    boost_msm_submachine.cpp
    boost_msm_forward_data.cpp)

target_link_libraries(test Boost::headers GTest::gmock_main)
