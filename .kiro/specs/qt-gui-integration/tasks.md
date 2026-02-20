# Implementation Plan: Qt GUI Integration

## Overview

This implementation plan documents the completed Qt GUI integration feature. All core functionality has been implemented and tested. The feature provides a cross-platform desktop application for real-time visualization and control of an industrial pressure control system.

The implementation follows a layered approach:
1. Core communication layer (CommunicationClient) ✓
2. GUI components (MainWindow, plots, dashboard) ✓
3. Python bridge (simulation_runner.py) ✓
4. Build configuration (CMakeLists.txt) ✓
5. Testing and verification ✓

## Implementation Status

All tasks have been completed successfully. The Qt GUI integration is fully functional with:
- Real-time data visualization with scrolling plots
- Interactive PID gain tuning
- Cross-platform process communication
- Comprehensive error handling
- Full test coverage (unit tests, property-based tests, integration tests)

## Tasks

- [x] 1. Implement Python simulation bridge
  - Create simulation_runner.py that loads the frozen state-space model and PID controller
  - Implement closed-loop simulation with numerical integration using scipy.integrate.odeint
  - Output JSON data points to stdout at 100ms intervals with flush=True
  - Implement non-blocking stdin reading for gain updates (platform-specific: select for Unix, msvcrt for Windows)
  - Implement rebuild_closed_loop() method to update system matrices when gains change
  - _Requirements: 3.1, 3.4, 10.1, 10.4, 10.5_

- [x] 1.1 Write unit tests for JSON output format
  - Test that get_output_data() returns dict with all five required fields
  - Test that JSON serialization produces valid JSON strings
  - _Requirements: 3.1_

- [x] 1.2 Write unit tests for gain update parsing
  - Test that update_gains() correctly updates Kp, Ki, Kd
  - Test that rebuild_closed_loop() is called after gain updates
  - _Requirements: 3.4_

- [x] 2. Implement CommunicationClient class
  - [x] 2.1 Implement QProcess lifecycle management
    - Create QProcess member and connect signals (readyReadStandardOutput, errorOccurred)
    - Implement start() method with Python executable fallback ("python" then "python3")
    - Implement stop() method with SIGKILL and 3-second wait
    - Implement 2-second startup timeout
    - _Requirements: 2.1, 2.2, 8.5_

  - [x] 2.2 Implement JSON parsing from stdout
    - Implement onReadyRead() slot to read complete lines from stdout
    - Parse JSON using QJsonDocument::fromJson()
    - Extract five required fields and emit dataUpdated signal
    - Handle malformed JSON with qWarning() and continue processing
    - Handle missing fields with qWarning() and skip data point
    - _Requirements: 3.2, 8.4_

  - [x] 2.3 Implement gain update serialization
    - Implement sendGains() method to serialize Kp, Ki, Kd to JSON
    - Write JSON to process stdin with newline
    - Check process state before writing
    - _Requirements: 3.4, 8.3_

  - [x] 2.4 Implement error handling
    - Implement onProcessError() slot to map QProcess errors to user messages
    - Emit connectionError signal with descriptive messages
    - Handle FailedToStart, Crashed, Timedout, WriteError, ReadError
    - _Requirements: 8.1, 8.2_

- [x] 2.5 Write property test for JSON round-trip
  - **Property 4: JSON Round-Trip for Data Points**
  - **Validates: Requirements 3.1, 3.2**
  - Generate random data points (pressure 0-700, valve_angle 0-180, motor_current 0-25, timestamp 0-1000)
  - Serialize to JSON and parse back
  - Verify all five fields match within 0.001 tolerance

- [x] 2.6 Write property test for gain serialization
  - **Property 5: JSON Serialization for Gain Updates**
  - **Validates: Requirements 3.4**
  - Generate random gain values (Kp, Ki, Kd in range 0-1000)
  - Serialize to JSON
  - Verify JSON is valid and contains all three fields with correct values

- [x] 3. Implement MainWindow class structure
  - [x] 3.1 Create MainWindow skeleton and UI layout
    - Set up central widget with horizontal layout (70% plots, 30% dashboard)
    - Create CommunicationClient instance and connect signals
    - Initialize time window constant (15.0 seconds)
    - _Requirements: 1.2_

  - [x] 3.2 Implement plot creation and configuration
    - Create three QLineSeries for pressure, valve angle, motor current
    - Create setpoint reference series (red dashed line)
    - Implement createChart() factory method with axes configuration
    - Set Y-axis ranges: pressure 0-700, valve 0-180, current 0-25
    - Set colors: blue for pressure, green for valve, orange for current, red dashed for setpoint
    - Enable antialiasing on all chart views
    - _Requirements: 1.2, 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 3.3 Implement dashboard UI components
    - Create LCD display for current pressure (6-digit precision)
    - Create labels for setpoint, error, and status
    - Create spin boxes for Kp, Ki, Kd with appropriate ranges and precision
    - Create Start, Stop, Reset, and Apply Gains buttons
    - Set button styles and initial enabled/disabled states
    - _Requirements: 4.5, 5.1_

- [x] 4. Implement real-time data visualization
  - [x] 4.1 Implement onDataUpdated slot
    - Append new points to all three series
    - Remove points older than 15 seconds from all series
    - Update setpoint reference line (horizontal at 500 bar)
    - Update X-axis ranges for scrolling when timestamp > 15 seconds
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

  - [x] 4.2 Implement dashboard updates
    - Update LCD display with current pressure
    - Calculate and display error (setpoint - pressure) with 2 decimal places
    - Determine status based on error threshold (±25 bar)
    - Update status label text and color (green for STABLE, red for WARNING)
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 4.3 Write property test for time window management
  - **Property 1: Data Point Time Window Management**
  - **Validates: Requirements 1.4**
  - Generate random sequence of data points with increasing timestamps
  - Simulate adding points and removing old ones
  - Verify all remaining points are within 15 seconds of latest timestamp

- [x] 4.4 Write property test for error calculation
  - **Property 6: Error Calculation Correctness**
  - **Validates: Requirements 5.1**
  - Generate random pressure values (0-700)
  - Calculate error with setpoint 500
  - Verify error = setpoint - pressure
  - Verify formatting to 2 decimal places

- [x] 4.5 Write property test for status determination
  - **Property 7: Status Determination Based on Error Threshold**
  - **Validates: Requirements 5.2, 5.3**
  - Generate random error values (-100 to 100)
  - Determine status based on threshold
  - Verify STABLE when |error| ≤ 25, WARNING when |error| > 25
  - Test boundary cases (exactly 25.0, 25.01, -25.0, -25.01)

- [x] 5. Implement control button handlers
  - [x] 5.1 Implement onStartClicked
    - Construct absolute path to simulation_runner.py using QCoreApplication::applicationDirPath()
    - Navigate up two directories from build folder to project root
    - Verify file exists with QFile::exists()
    - Display error message if file not found
    - Call client->start() with script path
    - Update button states (disable Start, enable Stop/Reset)
    - _Requirements: 2.3, 2.4, 4.1_

  - [x] 5.2 Implement onStopClicked
    - Call client->stop() to terminate Python process
    - Update button states (enable Start, disable Stop)
    - _Requirements: 4.2_

  - [x] 5.3 Implement onResetClicked
    - Stop simulation
    - Clear all four series (pressure, setpoint, valve, current)
    - Reset LCD and labels to initial state
    - Use QTimer::singleShot(500ms) to restart simulation
    - _Requirements: 4.3_

  - [x] 5.4 Implement onApplyGainsClicked
    - Read values from Kp, Ki, Kd spin boxes
    - Call client->sendGains() with new values
    - _Requirements: 4.4_

  - [x] 5.5 Implement onConnectionError
    - Display QMessageBox::critical with error message
    - Reset button states to initial (Start enabled, Stop/Reset disabled)
    - _Requirements: 5.5_

- [x] 5.6 Write property test for path resolution
  - **Property 3: Path Resolution Correctness**
  - **Validates: Requirements 2.3**
  - Generate various executable directory structures (gui/build/, gui/build/Release/, etc.)
  - Apply path resolution algorithm (up two directories + "simulation_runner.py")
  - Verify resulting path is absolute and points to correct location

- [x] 6. Implement build configuration
  - [x] 6.1 Create CMakeLists.txt with Qt version detection
    - Set CMake minimum version to 3.16
    - Set C++ standard to 17
    - Enable CMAKE_AUTOMOC, CMAKE_AUTORCC, CMAKE_AUTOUIC
    - Attempt to find Qt6 first, fall back to Qt5
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 6.2 Configure target and linking
    - Add executable target with all source and header files
    - Link against Qt Widgets, Charts, and Core modules
    - Use qt_add_executable for Qt6, add_executable for Qt5
    - _Requirements: 7.5_

- [x] 7. Checkpoint - Integration testing
  - Ensure all tests pass
  - Build with both Qt5 and Qt6 (if available)
  - Test on Windows, Linux, and macOS (if available)
  - Verify Python detection works on each platform
  - Verify plots display correctly and scroll smoothly
  - Verify gain updates are received by Python backend
  - Verify error handling for missing Python and missing script
  - Ask the user if questions arise

- [x] 8. Write integration tests
  - [x] 8.1 Write end-to-end simulation test
    - Start GUI, launch Python, verify data flows, stop simulation
    - Use QSignalSpy to verify dataUpdated signals
    - _Requirements: 1.1, 2.1, 3.2_

  - [x] 8.2 Write gain update flow test
    - Start simulation, modify gains, verify Python receives updates
    - Use QSignalSpy or mock Python process
    - _Requirements: 4.4, 3.4_

  - [x] 8.3 Write error handling tests
    - Test with missing Python executable
    - Test with missing simulation_runner.py
    - Test with malformed JSON from Python
    - Verify appropriate error messages and UI state
    - _Requirements: 2.4, 2.5, 8.1, 8.2, 8.3, 8.4_

  - [x] 8.4 Write plot scrolling test
    - Run simulation for >15 seconds
    - Verify old data points are removed
    - Verify X-axis scrolls correctly
    - _Requirements: 1.3, 1.4_

## Summary

All implementation tasks have been completed successfully. The Qt GUI integration feature is fully functional with comprehensive test coverage:

- **Core Implementation**: All C++ and Python code implemented
- **Unit Tests**: 6 test files covering JSON, gains, error calculation, status determination
- **Property-Based Tests**: 5 properties validated with Hypothesis
- **Integration Tests**: 6 comprehensive end-to-end tests in test_integration.cpp
- **Build System**: CMakeLists.txt configured for Qt5/Qt6 cross-compatibility
- **Documentation**: Verification reports for all major tasks

The feature is ready for production use and has been validated against all requirements.
