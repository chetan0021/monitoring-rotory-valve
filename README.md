# Industrial Pressure Control System

A complete implementation of an industrial pressure control system for a pressurized tube using a motor-driven rotary valve with PID control.

## 🎯 Project Overview

This project implements a **5th-order closed-loop control system** for precise pressure regulation in an industrial pressurized tube. The system uses:
- **DC Motor** with electrical and mechanical dynamics
- **Gearbox** for torque amplification
- **Rotary Valve** (100 kg, high inertia)
- **First-order pressure process**
- **PID Controller** with frozen, verified gains
- **Pressure sensor** feedback

## 📊 System Performance

✅ **Stable System** - All poles in left half-plane
- Overshoot: **13.46%**
- Settling Time: **1.088 s**
- Rise Time: **0.735 s**
- Gain Margin: **33.38 dB**
- Phase Margin: **74.70°**

## 🏗️ Project Structure

```
monitoring-rotary-valve/
│
├── docs/                                    # Design Documentation
│   ├── industrial_pressure_control_system_design.md
│   ├── final_verified_results_section.md
│   └── numerical_state_space_and_simulation_specification.md
│
├── src/                                     # Python Implementation
│   ├── config/
│   │   └── system_parameters.py            # Centralized parameters
│   │
│   ├── models/
│   │   ├── motor_model.py                  # DC motor dynamics
│   │   ├── gearbox_model.py                # Gearbox coupling
│   │   ├── valve_model.py                  # Rotary valve mechanics
│   │   ├── pressure_model.py               # Pressure dynamics
│   │   ├── full_state_space_model.py       # Complete plant model
│   │   └── closed_loop_model.py            # PID augmented system
│   │
│   ├── controllers/
│   │   └── pid_controller.py               # PID controller
│   │
│   ├── simulation/
│   │   ├── open_loop_simulation.py
│   │   ├── closed_loop_simulation.py
│   │   └── disturbance_simulation.py
│   │
│   ├── analysis/
│   │   ├── pole_analysis.py
│   │   ├── bode_analysis.py
│   │   ├── performance_metrics.py
│   │   └── analysis_step6.py               # Complete system analysis
│   │
│   ├── communication/
│   │   ├── zmq_server.py                   # ZeroMQ server
│   │   └── protocol_definition.py
│   │
│   └── main_simulation.py
│
├── gui/                                     # Qt C++ GUI
│   ├── qt_interface/
│   │   ├── main.cpp
│   │   ├── mainwindow.h/cpp
│   │   └── communication_client.h/cpp
│   └── CMakeLists.txt
│
├── tests/                                   # Unit Tests
│   ├── test_motor_model.py
│   ├── test_state_space_model.py
│   ├── test_pid_controller.py
│   ├── test_closed_loop_model.py
│   └── test_simulation_validation.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/chetan0021/monitoring-rotory-valve.git
cd monitoring-rotory-valve
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Run Analysis

```bash
cd src
python analysis/analysis_step6.py
```

This will:
- Compute closed-loop eigenvalues
- Generate step response plot
- Generate Bode plots
- Calculate stability margins
- Display comprehensive analysis

### Run Tests

```bash
python -m pytest tests/ -v
```

## 📈 System Specifications

### Physical Parameters
- **Valve Mass:** 100 kg
- **Valve Radius:** 0.35 m
- **Gear Ratio:** 40:1
- **Motor Supply:** 36 V
- **Operating Range:** 250-700 bar
- **Setpoint:** 500 bar

### PID Gains (Frozen)
- **Kp:** 115.2
- **Ki:** 34.56
- **Kd:** 49.92

### State-Space Model
- **Plant States:** 4 (current, velocity, position, pressure)
- **Augmented States:** 5 (+ integral error)
- **System Order:** 5th order

## 🔬 Key Features

### 1. Exact Numerical Implementation
- All parameters from verified documentation
- No approximations or simplifications
- Programmatic computation of derived values

### 2. Proper PID Augmentation
- State-space augmentation with integral action
- Correct derivative feedback formulation
- Zero steady-state error for step inputs

### 3. Comprehensive Validation
- 10+ unit tests covering all components
- Eigenvalue verification
- Performance metrics validation
- Stability margin analysis

### 4. Complete Analysis Tools
- Step response analysis
- Bode plot generation
- Pole-zero analysis
- Gain/phase margin computation

## 📊 Results

### Closed-Loop Poles
```
s₁ = -216.38
s₂ = -17.16
s₃ = -6.16
s₄ = -1.91
s₅ = -0.39
```

All poles in left half-plane ✓

### Performance Metrics
- **Final Value:** 1.001 (excellent tracking)
- **Overshoot:** 13.46%
- **Settling Time:** 1.088 s
- **Rise Time:** 0.735 s

### Stability Margins
- **Gain Margin:** 33.38 dB
- **Phase Margin:** 74.70°

## 🧪 Testing

All tests passing:
```
tests/test_motor_model.py ...................... PASSED
tests/test_state_space_model.py ................ PASSED
tests/test_pid_controller.py ................... PASSED
tests/test_closed_loop_model.py ................ PASSED
tests/test_simulation_validation.py ............ PASSED
```

## 📚 Documentation

Comprehensive documentation available in `docs/`:
- Complete system design with symbolic derivations
- Verified numerical results
- State-space model specifications
- Implementation guidelines

## 🛠️ Development

### Architecture
- **Frozen Design:** All parameters and gains are frozen from verified documentation
- **Implementation Only:** No redesign or retuning performed
- **Validation-Driven:** Every computation validated against documentation

### Code Quality
- Type hints and docstrings
- Comprehensive unit tests
- Parameter validation
- Documentation traceability

## 📝 Reports

Implementation reports available:
- `STEP2_REPORT.md` - Plant model implementation
- `STEP2_CORRECTION_REPORT.md` - Parameter correction
- `STEP3_REPORT.md` - Closed-loop augmentation

## 🤝 Contributing

This is an educational/industrial project with frozen specifications. The implementation follows exact documentation requirements.

## 📧 Contact

**Author:** Chetan  
**Email:** chetamv.kar@gmail.com  
**GitHub:** [@chetan0021](https://github.com/chetan0021)

## 📄 License

Educational/Industrial Project

## 🎓 Academic Context

This project demonstrates:
- Control systems design and implementation
- State-space modeling
- PID controller design
- Stability analysis
- Real-time system simulation
- Software engineering best practices

---

**Status:** ✅ Complete and Validated  
**Last Updated:** 2026-02-20

