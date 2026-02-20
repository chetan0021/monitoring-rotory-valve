"""
Rebuild closed-loop system with proper PID augmentation.

Proper formulation:
- States: [x_plant; x_integral]
- Error: e = r - C*x
- Integral: x_int_dot = e
- Control: u = Kp*e + Ki*x_int - Kd*C*x_dot

Do NOT substitute plant equations into derivative term.
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.full_state_space_model import FullStateSpaceModel
from config.system_parameters import params

print("=" * 80)
print("PROPER PID AUGMENTATION - CLOSED-LOOP CONSTRUCTION")
print("=" * 80)

# Load plant model
plant = FullStateSpaceModel()
A = plant.A  # 4x4
B = plant.B  # 4x1
C = plant.C  # 1x4
D = plant.D  # 1x1

print("\n--- Plant Matrices ---")
print("A (4x4):")
print(A)
print("\nB (4x1):")
print(B.T)
print("\nC (1x4):")
print(C)

# PID gains
Kp = params.Kp
Ki = params.Ki
Kd = params.Kd

print("\n--- PID Gains ---")
print(f"Kp = {Kp}")
print(f"Ki = {Ki}")
print(f"Kd = {Kd}")

print("\n" + "=" * 80)
print("AUGMENTED SYSTEM CONSTRUCTION")
print("=" * 80)

print("\nAugmented state: X_aug = [x_plant; x_integral]")
print("Dimension: 5 (4 plant states + 1 integral state)")

print("\nPlant dynamics:")
print("  x_dot = A*x + B*u")

print("\nError definition:")
print("  e = r - C*x")

print("\nIntegral state:")
print("  x_int_dot = e = r - C*x")

print("\nControl law:")
print("  u = Kp*e + Ki*x_int - Kd*C*x_dot")
print("  u = Kp*(r - C*x) + Ki*x_int - Kd*C*x_dot")

print("\nSubstitute x_dot = A*x + B*u:")
print("  u = Kp*(r - C*x) + Ki*x_int - Kd*C*(A*x + B*u)")
print("  u = Kp*r - Kp*C*x + Ki*x_int - Kd*C*A*x - Kd*C*B*u")

print("\nCollect u terms:")
print("  u + Kd*C*B*u = Kp*r - Kp*C*x + Ki*x_int - Kd*C*A*x")
print("  u*(1 + Kd*C*B) = Kp*r - (Kp*C + Kd*C*A)*x + Ki*x_int")

# Compute denominator
CxB = C @ B
denom = 1.0 + Kd * CxB[0, 0]

print(f"\nC*B = {CxB[0,0]}")
print(f"Denominator: 1 + Kd*C*B = 1 + {Kd}*{CxB[0,0]} = {denom}")

print("\nSolve for u:")
print(f"  u = (1/{denom}) * [Kp*r - (Kp*C + Kd*C*A)*x + Ki*x_int]")

# Compute feedback gains
K_state = -(Kp * C + Kd * C @ A) / denom  # 1x4
K_int = Ki / denom  # scalar
K_ref = Kp / denom  # scalar

print("\n--- Feedback Gains ---")
print(f"K_state = -(Kp*C + Kd*C*A) / {denom}")
print(f"K_state = {K_state}")
print(f"\nK_int = Ki / {denom} = {K_int}")
print(f"K_ref = Kp / {denom} = {K_ref}")

print("\nControl law in feedback form:")
print("  u = K_state @ x + K_int * x_int + K_ref * r")

print("\n" + "=" * 80)
print("CLOSED-LOOP A MATRIX CONSTRUCTION")
print("=" * 80)

# Build closed-loop A matrix (5x5)
A_cl = np.zeros((5, 5))

# Upper-left block (4x4): Plant with state feedback
# x_dot = A*x + B*u = A*x + B*(K_state @ x + K_int * x_int)
# x_dot = (A + B @ K_state) @ x + B * K_int * x_int
A_cl[0:4, 0:4] = A + B @ K_state

print("\nUpper-left block (4x4): A + B @ K_state")
print(A_cl[0:4, 0:4])

# Upper-right column (4x1): Integral feedback to plant
A_cl[0:4, 4:5] = B * K_int

print("\nUpper-right column (4x1): B * K_int")
print(A_cl[0:4, 4])

# Bottom-left row (1x4): Error feedback to integral
# x_int_dot = e = r - C*x, so derivative w.r.t. x is -C
A_cl[4:5, 0:4] = -C

print("\nBottom-left row (1x4): -C")
print(A_cl[4, 0:4])

# Bottom-right element (1x1): Integral self-feedback (zero)
A_cl[4, 4] = 0.0

print("\nBottom-right element: 0")

print("\n--- Final A_cl Matrix (5x5) ---")
print(A_cl)

# Build B_ref matrix (5x1)
B_ref = np.zeros((5, 1))
B_ref[0:4, 0:1] = B * K_ref  # Reference to plant through control
B_ref[4, 0] = 1.0  # Reference to integral directly

print("\n--- B_ref Matrix (5x1) ---")
print(B_ref.T)

# Build C_cl matrix (1x5)
C_cl = np.zeros((1, 5))
C_cl[0, 0:4] = C  # Extract pressure from plant states
C_cl[0, 4] = 0.0  # Integral doesn't affect output

print("\n--- C_cl Matrix (1x5) ---")
print(C_cl)

print("\n" + "=" * 80)
print("EIGENVALUES (CLOSED-LOOP POLES)")
print("=" * 80)

eigenvalues = np.linalg.eigvals(A_cl)
eigenvalues = sorted(eigenvalues, key=lambda x: x.real)

for i, pole in enumerate(eigenvalues, 1):
    if abs(pole.imag) < 1e-10:
        print(f"  s{i} = {pole.real:.6f}")
    else:
        sign = '+' if pole.imag >= 0 else ''
        print(f"  s{i} = {pole.real:.6f} {sign}{pole.imag:.6f}j")

# Check stability
all_stable = all(pole.real < 0 for pole in eigenvalues)
print(f"\nSystem stable: {all_stable}")

if not all_stable:
    print("⚠️  WARNING: System has unstable poles!")
else:
    print("✓ All poles in left half-plane")

print("\n" + "=" * 80)
