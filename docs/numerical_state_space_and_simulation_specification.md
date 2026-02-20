# NUMERICAL STATE-SPACE MODEL AND SIMULATION SPECIFICATION

This document defines the EXACT numerical plant model that must be implemented in Python.
No approximations. No dominant pole reductions.
All parameters traceable to previous design documents.

---------------------------------------------------------------------
# 1. FINAL NUMERICAL PARAMETERS (AUTHORITATIVE – DESIGN CONSISTENT)
---------------------------------------------------------------------

This parameter set is frozen and matches the plant used in
industrial_pressure_control_system_design.md for PID derivation.
No deviations allowed.

---------------------------------------------------------------------
## 1.1 Mechanical

Valve mass m = 100 kg
Valve radius r = 0.35 m

Moment of inertia (solid disk):
J_valve = (1/2) m r^2 = 6.125 kg·m^2

Gear ratio N = 40
Gear efficiency η assumed ideal for dynamic model

Motor inertia:
J_m = 0.002 kg·m^2

Reflected inertia to motor:
J_ref = J_valve / N^2
J_ref = 6.125 / 1600 = 0.003828125 kg·m^2

Total equivalent inertia:
J_total = J_m + J_ref
J_total = 0.002 + 0.003828125
J_total = 0.005828125 kg·m^2

---------------------------------------------------------------------
## 1.2 Electrical

Armature resistance R = 1.2 Ω
Armature inductance L = 0.02 H

Torque constant Kt = 0.8 Nm/A
Back EMF constant Ke = 0.8 V·s/rad

Supply voltage = 36 V

---------------------------------------------------------------------
## 1.3 Pressure System

Sensor gain:
Ks = 0.01 V/bar

Pressure gain:
Kp_pressure = 250 bar/rad

Pressure time constant:
τp = 0.8 s

First-order model:
τp (dP/dt) + P = Kp_pressure θ


---------------------------------------------------------------------
# 2. COMPLETE STATE DEFINITIONS

States:

x1 = armature current i
x2 = motor angular velocity ω
x3 = motor angular position θm
x4 = tube pressure P

Output:

y = Ks P

---------------------------------------------------------------------
# 3. EXACT STATE-SPACE EQUATIONS

Electrical:

di/dt = (1/L) [ V − R i − Ke ω ]

Mechanical:

dω/dt = (1/J_total) [ Kt i − T_load ]

Load torque:
T_load = (Static friction reflected) + dynamic torque

Position:

dθm/dt = ω

Pressure dynamics:

dP/dt = (1/τp)( Kp_pressure (θm/N) − P )

---------------------------------------------------------------------
# 4. NUMERICAL STATE-SPACE MATRICES (FROZEN AUTHORITY)
---------------------------------------------------------------------

State vector:
X = [ i, ω, θm, P ]^T

Input:
U = V (motor voltage)

---------------------------------------------------------------------
A Matrix (4×4)

A = [
 -60        -40        0           0
 137.216     0         0           0
  0          1         0           0
  0          0      7.8125      -1.25
]

---------------------------------------------------------------------
B Matrix (4×1)

B = [
 50
  0
  0
  0
]

---------------------------------------------------------------------
C Matrix (1×4)

C = [ 0  0  0  0.01 ]

---------------------------------------------------------------------
D Matrix

D = [ 0 ]

---------------------------------------------------------------------

These matrices correspond exactly to the plant used to derive:

• The full 5th-order closed-loop characteristic polynomial
• The Routh table
• The verified poles in final_verified_results_section.md

No parameter modification allowed.

---------------------------------------------------------------------
# 5. PID CONTROLLER STRUCTURE

Controller form (continuous):

Gc(s) = Kp + Ki/s + Kd s

Controller must be implemented in state-space form when simulating.

Augmented state required for integral action.

---------------------------------------------------------------------
# 6. SIMULATION REQUIREMENTS

The following must be simulated numerically using scipy:

1. Open-loop actuator step response (Voltage → Angle)
2. Closed-loop pressure control (Setpoint → Pressure)
3. Motor current waveform
4. Valve angle response
5. Disturbance rejection test:
   - Apply 10% pressure disturbance
   - Verify recovery within 3 s

---------------------------------------------------------------------
# 7. NUMERICAL VALIDATION CHECKLIST

The Python implementation must compute:

• Closed-loop poles using numpy.linalg.eig
• Step response using scipy.signal.lsim or step
• Bode plot using scipy.signal.bode
• Gain margin and phase margin
• Peak motor current
• Settling time
• Overshoot
• Steady-state error

Each computed value must be cross-checked with:

final_verified_results_section.md

No hardcoded performance numbers allowed.

---------------------------------------------------------------------
# 8. GUI COMMUNICATION SPECIFICATION (FOR KIRO)

The Python simulation must expose:

• Current pressure
• Valve angle
• Motor current
• Setpoint
• Controller gains

Communication protocol:

Recommended: ZeroMQ or TCP socket (low latency industrial control)

GUI stack (C++/Qt):

• Qt Widgets for real-time plotting
• QCustomPlot or QtCharts
• Non-blocking threaded communication

---------------------------------------------------------------------
# END OF NUMERICAL STATE-SPACE AND SIMULATION SPECIFICATION

