# STEP 7 — GUI Communication Implementation

## Summary

Implemented Qt C++ GUI with Python subprocess communication via stdout/stdin. No ZeroMQ, no network, no ports — simple process-based communication.

## Actions Completed

### 1. Deleted Files (ZeroMQ approach replaced)
- ❌ `src/communication/zmq_server.py`
- ❌ `src/communication/protocol_definition.py`

### 2. Created New File
- ✅ `simulation_runner.py` (project root)
  - Python stdout bridge for Qt GUI
  - Runs closed-loop simulation
  - Outputs JSON to stdout every 100ms
  - Accepts gain updates from stdin
  - Uses existing models from `src/`

### 3. Implemented Qt GUI Files

#### `gui/qt_interface/communication_client.h`
- QProcess-based communication
- Launches Python as subprocess
- Reads JSON from stdout
- Sends gains to stdin

#### `gui/qt_interface/communication_client.cpp`
- Full implementation of subprocess management
- JSON parsing with QJsonDocument
- Signal emission for data updates
- Error handling

#### `gui/qt_interface/mainwindow.h`
- Main window with 3 live plots
- Dashboard with controls
- LCD display and status indicators
- PID gain adjustment spinboxes

#### `gui/qt_interface/mainwindow.cpp`
- Three QChartView plots (pressure, valve angle, motor current)
- Scrolling time window (15 seconds)
- Real-time data updates
- Dashboard with:
  - Pressure LCD display
  - Error calculation
  - Status indicator (STABLE/WARNING)
  - PID gain controls
  - Start/Stop/Reset buttons

#### `gui/qt_interface/main.cpp`
- Application entry point
- Window setup (1400x900)
- Fusion style

#### `gui/CMakeLists.txt`
- Qt6/Qt5 compatibility
- Links Widgets, Charts, Core modules
- C++17 standard

### 4. Updated Documentation
- ✅ `README.md` — Updated with GUI installation and usage instructions
- Removed ZeroMQ references
- Added step-by-step build instructions
- Added physical parameters table

## Architecture

### Communication Flow
```
Qt GUI (C++)
    ↓ QProcess::start("python simulation_runner.py")
Python Simulation
    ↓ print(json.dumps(data), flush=True)
Qt GUI reads stdout
    ↓ QJsonDocument::fromJson()
Update plots and dashboard
```

### Data Format (JSON per line)
```json
{
  "pressure": 312.4,
  "valve_angle": 23.1,
  "motor_current": 4.2,
  "setpoint": 500.0,
  "timestamp": 0.1
}
```

### Gain Updates (stdin to Python)
```json
{
  "Kp": 115.2,
  "Ki": 34.56,
  "Kd": 49.92
}
```

## GUI Features

### Three Live Plots
1. **Pressure vs Time**
   - Blue line: actual pressure
   - Red dashed line: setpoint (500 bar)
   - Y-axis: 0-700 bar

2. **Valve Angle vs Time**
   - Green line: valve angle in degrees
   - Y-axis: 0-180°

3. **Motor Current vs Time**
   - Orange line: motor current
   - Y-axis: auto-range

### Dashboard Panel
- **Pressure Monitor**
  - 6-digit LCD display
  - Current pressure in bar
  - Error from setpoint
  - Status indicator (green STABLE / red WARNING)

- **PID Controller Gains**
  - Kp spinbox (default 115.2)
  - Ki spinbox (default 34.56)
  - Kd spinbox (default 49.92)
  - Apply Gains button

- **Control Buttons**
  - ▶ Start Simulation (green)
  - ■ Stop (red)
  - ↺ Reset (grey)

- **Footer**
  - "Industrial Pressure Control System"
  - "Etheral X — Assignment II"

## Key Implementation Details

### simulation_runner.py
- Uses `scipy.integrate.odeint` for simulation
- Builds 5x5 closed-loop A matrix from plant model
- Proper PID augmentation (same as `rebuild_closed_loop.py`)
- Non-blocking stdin reading (Windows and Unix compatible)
- 10ms integration step, 100ms output interval
- `flush=True` on every print (critical for Qt to receive data)

### CommunicationClient
- `QProcess` for subprocess management
- `readyReadStandardOutput` signal for data reception
- `canReadLine()` loop to read all available JSON lines
- `write()` to send gains to Python stdin
- Error handling for process failures

### MainWindow
- `QChartView` with `QLineSeries` for plotting
- `QValueAxis` for scrolling time window
- Data point management (remove old points outside window)
- Setpoint reference line updated every frame
- Status color changes based on error threshold (±25 bar)

## Build Instructions

```bash
cd gui
mkdir build
cd build
cmake ..
cmake --build .
```

Windows with Visual Studio:
```bash
cmake --build . --config Release
```

## Run Instructions

1. Launch Qt executable
2. Click "▶ Start Simulation"
3. Python starts automatically
4. Plots update in real-time
5. Adjust gains and click "Apply Gains" to update live

## No Configuration Required

- No network setup
- No port configuration
- No server to start manually
- No ZeroMQ installation
- Works on Windows, Linux, macOS
- One-click operation

## Files NOT Modified (Frozen)

As instructed, the following were NOT touched:
- `src/config/system_parameters.py`
- `src/models/` (entire folder)
- `src/controllers/` (entire folder)
- `src/simulation/` (entire folder)
- `src/analysis/` (entire folder)
- `src/main_simulation.py`
- `tests/` (entire folder)
- `docs/` (entire folder)

All physics, mathematics, and parameters remain exactly as verified.

## Status

✅ GUI implementation complete
✅ Python bridge complete
✅ Documentation updated
✅ Ready for demonstration

---

**Completed:** 2026-02-20
