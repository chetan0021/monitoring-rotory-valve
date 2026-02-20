cmake_minimum_required(VERSION 3.16)
project(PressureControlGUI VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Try Qt6 first, fall back to Qt5
find_package(Qt6 COMPONENTS Widgets Charts Core QUIET)
if(Qt6_FOUND)
    set(QT_VERSION_MAJOR 6)
    message(STATUS "Using Qt6")
else()
    find_package(Qt5 COMPONENTS Widgets Charts Core REQUIRED)
    set(QT_VERSION_MAJOR 5)
    message(STATUS "Using Qt5")
endif()

set(SOURCES
    qt_interface/main.cpp
    qt_interface/mainwindow.cpp
    qt_interface/communication_client.cpp
)

set(HEADERS
    qt_interface/mainwindow.h
    qt_interface/communication_client.h
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_add_executable(PressureControlGUI ${SOURCES} ${HEADERS})
    target_link_libraries(PressureControlGUI PRIVATE
        Qt6::Widgets
        Qt6::Charts
        Qt6::Core
    )
else()
    add_executable(PressureControlGUI ${SOURCES} ${HEADERS})
    target_link_libraries(PressureControlGUI PRIVATE
        Qt5::Widgets
        Qt5::Charts
        Qt5::Core
    )
endif()

# Enable testing
enable_testing()

# Find Qt Test module
if(QT_VERSION_MAJOR EQUAL 6)
    find_package(Qt6 COMPONENTS Test REQUIRED)
else()
    find_package(Qt5 COMPONENTS Test REQUIRED)
endif()

# Integration test executable
set(TEST_SOURCES
    qt_interface/test_integration.cpp
    qt_interface/communication_client.cpp
    qt_interface/mainwindow.cpp
)

set(TEST_HEADERS
    qt_interface/communication_client.h
    qt_interface/mainwindow.h
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_add_executable(test_integration ${TEST_SOURCES} ${TEST_HEADERS})
    target_link_libraries(test_integration PRIVATE
        Qt6::Widgets
        Qt6::Charts
        Qt6::Core
        Qt6::Test
    )
else()
    add_executable(test_integration ${TEST_SOURCES} ${TEST_HEADERS})
    target_link_libraries(test_integration PRIVATE
        Qt5::Widgets
        Qt5::Charts
        Qt5::Core
        Qt5::Test
    )
endif()

# Add test to CTest
add_test(NAME IntegrationTest COMMAND test_integration)
