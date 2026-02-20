# Requirements Document: Qt GUI Integration

## Introduction

This document specifies the requirements for a Qt-based graphical user interface (GUI) that integrates with a Python simulation backend for an industrial pressure control system. The system provides real-time visualization of pressure control dynamics through a cross-platform desktop application.

The GUI communicates with a Python simulation process via JSON over stdout/stdin, displaying three synchronized live plots (pressure, valve angle, motor current) and providing interactive controls for PID gain tuning and simulation management.

## Glossary

- **GUI**: The Qt C++ graphical user interface application
- **Python_Backend**: The Python simulation process (simulation_runner.py)
- **QProcess**: Qt's process management class for launching and communicating with child processes
- **JSON_Protocol**: The communication protocol using JSON-formatted messages over stdout/stdin
- **Plot_Window**: A scrolling time window displaying the most recent 15 seconds of data
- **Dashboard**: The control panel containing LCD display, PID controls, and action buttons
- **PID_Gains**: The three controller parameters (Kp, Ki, Kd) that can be adjusted at runtime
- **Data_Point**: A single measurement containing pressure, valve_angle, motor_current, setpoint, and timestamp
- **Frozen_Files**: Python backend files that cannot be modified (models, controllers, simulation, analysis)

## Requirements

### Requirement 1: Real-Time Data Visualization

**User Story:** As an operator, I want to see live plots of system variables updating in real-time, so that I can monitor the pressure control system's behavior.

#### Acceptance Criteria

1. WHEN the Python_Backend outputs a Data_Point, THE GUI SHALL update all three plots within 100ms
2. THE GUI SHALL display three synchronized plots: pressure vs time, valve angle vs time, and motor current vs time
3. WHILE the simulation is running, THE GUI SHALL maintain a scrolling Plot_Window showing the most recent 15 seconds of data
4. WHEN new data arrives, THE GUI SHALL remove data points older than 15 seconds from the visible Plot_Window
5. THE GUI SHALL display a reference line at 500 bar on the pressure plot showing the setpoint

### Requirement 2: Cross-Platform Process Communication

**User Story:** As a developer, I want the GUI to work on Windows, Linux, and macOS, so that users can run the application on their preferred platform.

#### Acceptance Criteria

1. THE GUI SHALL launch the Python_Backend using QProcess without requiring network sockets
2. WHEN starting the simulation, THE GUI SHALL attempt to find Python using both "python" and "python3" executable names
3. THE GUI SHALL construct the absolute path to simulation_runner.py by navigating from the executable directory to the project root
4. WHEN simulation_runner.py cannot be found, THE GUI SHALL display an error message with the expected file path
5. WHEN Python is not installed or not in PATH, THE GUI SHALL display an error message instructing the user to install Python 3.9+

### Requirement 3: JSON Communication Protocol

**User Story:** As a system integrator, I want a simple text-based protocol between GUI and backend, so that the components remain loosely coupled and debuggable.

#### Acceptance Criteria

1. THE Python_Backend SHALL output JSON lines to stdout containing pressure, valve_angle, motor_current, setpoint, and timestamp fields
2. WHEN the GUI receives a complete JSON line from stdout, THE GUI SHALL parse it and extract all five required fields
3. WHEN the GUI receives malformed JSON, THE GUI SHALL log a warning and continue processing subsequent lines
4. THE GUI SHALL send PID gain updates to the Python_Backend as JSON objects via stdin
5. THE Python_Backend SHALL flush stdout after each JSON line to ensure immediate delivery to the GUI

### Requirement 4: Interactive Dashboard Controls

**User Story:** As an operator, I want to control the simulation and adjust PID gains, so that I can experiment with different controller configurations.

#### Acceptance Criteria

1. WHEN the user clicks the Start button, THE GUI SHALL launch the Python_Backend and disable the Start button
2. WHEN the user clicks the Stop button, THE GUI SHALL terminate the Python_Backend process and enable the Start button
3. WHEN the user clicks the Reset button, THE GUI SHALL stop the simulation, clear all plot data, and restart the simulation after 500ms
4. WHEN the user modifies PID gain values and clicks Apply Gains, THE GUI SHALL send the new gains to the Python_Backend via stdin
5. THE Dashboard SHALL display current pressure on an LCD display with 6-digit precision

### Requirement 5: Status Monitoring and Feedback

**User Story:** As an operator, I want to see the current system status and error magnitude, so that I can quickly assess whether the controller is performing well.

#### Acceptance Criteria

1. THE Dashboard SHALL display the current pressure error (setpoint minus actual pressure) with 2 decimal places
2. WHEN the pressure error magnitude is less than or equal to 25 bar, THE Dashboard SHALL display "STABLE" status in green
3. WHEN the pressure error magnitude exceeds 25 bar, THE Dashboard SHALL display "WARNING" status in red
4. THE Dashboard SHALL update the LCD display, error label, and status indicator with each new Data_Point
5. WHEN a process error occurs, THE GUI SHALL display a modal error dialog with a descriptive error message

### Requirement 6: Plot Visualization Quality

**User Story:** As an operator, I want clear, professional-looking plots with appropriate scaling, so that I can easily interpret the system behavior.

#### Acceptance Criteria

1. THE pressure plot SHALL use a Y-axis range of 0 to 700 bar
2. THE valve angle plot SHALL use a Y-axis range of 0 to 180 degrees
3. THE motor current plot SHALL use a Y-axis range of 0 to 25 amperes
4. THE GUI SHALL render all plots with antialiasing enabled for smooth curves
5. THE GUI SHALL use distinct colors for each plot: blue for pressure, green for valve angle, orange for motor current, and red dashed for setpoint

### Requirement 7: Build System Configuration

**User Story:** As a developer, I want a flexible build system that supports multiple Qt versions, so that the application can be built in different environments.

#### Acceptance Criteria

1. THE build system SHALL attempt to find Qt6 first, then fall back to Qt5 if Qt6 is not available
2. THE build system SHALL require CMake 3.16 or higher
3. THE build system SHALL use C++17 standard
4. THE build system SHALL enable Qt's automatic MOC, RCC, and UIC processing
5. THE build system SHALL link against Qt Widgets, Charts, and Core modules

### Requirement 8: Error Handling and Robustness

**User Story:** As a user, I want the application to handle errors gracefully, so that I understand what went wrong and can take corrective action.

#### Acceptance Criteria

1. WHEN the Python_Backend fails to start, THE GUI SHALL emit a connectionError signal with a descriptive message
2. WHEN the Python_Backend crashes during execution, THE GUI SHALL detect the crash and notify the user
3. WHEN attempting to send gains while the process is not running, THE GUI SHALL log a warning and ignore the request
4. WHEN the GUI receives JSON with missing required fields, THE GUI SHALL log a warning and skip that data point
5. THE GUI SHALL wait up to 2 seconds for the Python process to start before reporting a failure

### Requirement 9: File Structure Constraints

**User Story:** As a maintainer, I want clear boundaries between modifiable and frozen code, so that the integration layer can be updated without affecting the validated simulation backend.

#### Acceptance Criteria

1. THE GUI SHALL NOT modify any files in src/config/, src/models/, src/controllers/, src/simulation/, src/analysis/, tests/, or docs/
2. THE GUI SHALL only interact with the Python_Backend through simulation_runner.py
3. THE simulation_runner.py file SHALL serve as the sole bridge between GUI and Frozen_Files
4. WHEN changes are needed to the simulation interface, THE changes SHALL be made only to simulation_runner.py, mainwindow.cpp, mainwindow.h, communication_client.cpp, or communication_client.h
5. THE build configuration SHALL only modify gui/CMakeLists.txt

### Requirement 10: Data Update Rate and Performance

**User Story:** As an operator, I want smooth, responsive plots without lag or stuttering, so that I can observe transient behavior in real-time.

#### Acceptance Criteria

1. THE Python_Backend SHALL output Data_Points at 100ms intervals (10 Hz)
2. THE GUI SHALL process each Data_Point and update all three plots within the same 100ms interval
3. WHEN removing old data points from plots, THE GUI SHALL maintain smooth scrolling without visible jumps
4. THE Python_Backend SHALL output Data_Points at 100ms intervals and the internal timestep is an implementation detail of simulation_runner.py only
5. THE Python_Backend SHALL not cause excessive CPU load during normal operation
