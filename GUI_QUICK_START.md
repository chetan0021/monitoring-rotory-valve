# GUI Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Qt 6.x or Qt 5.15+** with Charts module

3. **CMake 3.16+**

4. **C++17 compiler** (MSVC, GCC, or Clang)

## Build Steps

### Windows

```cmd
cd gui
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

Executable location: `gui\build\Release\PressureControlGUI.exe`

### Linux / macOS

```bash
cd gui
mkdir build
cd build
cmake ..
cmake --build .
```

Executable location: `gui/build/PressureControlGUI`

## Running the GUI

### Windows
Double-click `PressureControlGUI.exe` or run from command line:
```cmd
cd gui\build\Release
PressureControlGUI.exe
```

### Linux / macOS
```bash
cd gui/build
./PressureControlGUI
```

## Using the Application

1. **Start Simulation**
   - Click the green "▶ Start Simulation" button
   - Python simulation starts automatically in the background
   - All three plots begin updating immediately

2. **Monitor System**
   - **Top plot:** Pressure (blue) vs Setpoint (red dashed line)
   - **Middle plot:** Valve angle in degrees (green)
   - **Bottom plot:** Motor current in Amperes (orange)
   - **Dashboard:** Shows current pressure, error, and status

3. **Adjust PID Gains** (optional)
   - Modify Kp, Ki, Kd values in spinboxes
   - Click "Apply Gains" button
   - Gains update in real-time without stopping simulation

4. **Stop Simulation**
   - Click red "■ Stop" button

5. **Reset Simulation**
   - Click grey "↺ Reset" button
   - Clears all plots and restarts simulation

## Status Indicators

- **● STABLE** (green) — Pressure within ±25 bar of setpoint (500 bar)
- **● WARNING** (red) — Pressure outside tolerance

## Troubleshooting

### "Failed to start Python process"
- Ensure Python is installed and in PATH
- Try running `python --version` in terminal
- On some systems, use `python3` instead of `python`

### "Qt Charts module not found"
- Reinstall Qt with Charts component selected
- Or install via package manager:
  - Ubuntu: `sudo apt install libqt5charts5-dev`
  - macOS: `brew install qt@6` (includes Charts)

### Plots not updating
- Check that `simulation_runner.py` exists in project root
- Verify Python dependencies are installed: `pip install -r requirements.txt`
- Check console output for Python errors

### Build errors
- Ensure CMake 3.16+ is installed
- Ensure C++17 compiler is available
- Try cleaning build directory: `rm -rf build` and rebuild

## Default PID Gains

- **Kp:** 115.2
- **Ki:** 34.56
- **Kd:** 49.92

These gains are verified and produce stable, well-damped response.

## Expected Performance

- **Settling Time:** ~1.1 seconds
- **Overshoot:** ~13%
- **Steady-State Error:** ~0%
- **All poles stable** (left half-plane)

## No Configuration Required

The GUI automatically:
- Finds `simulation_runner.py` in project root
- Launches Python subprocess
- Establishes communication via stdout/stdin
- No network, ports, or server configuration needed

## Architecture

```
Qt GUI (C++)
    ↓
Launches Python subprocess
    ↓
simulation_runner.py
    ↓
Uses models from src/
    ↓
Outputs JSON to stdout every 100ms
    ↓
Qt reads and plots data
```

Simple, reliable, cross-platform.

---

**For detailed implementation:** See `STEP7_GUI_IMPLEMENTATION.md`
