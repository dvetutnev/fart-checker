# Project FartCHECKER
# Dmitriy Vetutnev, 2021

cmake_minimum_required(VERSION 3.7)
project(fart-checker CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})

include(conan.cmake)

conan_check(VERSION 1.35.0 REQUIRED)
conan_cmake_autodetect(settings)
conan_cmake_install(
    PATH_OR_REFERENCE ${CMAKE_SOURCE_DIR}/conanfile.txt
    BUILD missing
    REMOTE conan-center
    SETTINGS ${settings}
)

find_package(Boost REQUIRED)
find_package(GTest)

add_executable(test test_boost_msm.cpp)
target_link_libraries(test Boost::headers GTest::gmock_main)
