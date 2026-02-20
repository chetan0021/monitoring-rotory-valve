"""
Diagnostic script to show closed-loop A matrix construction in detail.
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.closed_loop_model import ClosedLoopSystem
from models.full_state_space_model import FullStateSpaceModel
from config.system_parameters import params

print("=" * 80)
print("CLOSED-LOOP A MATRIX CONSTRUCTION DIAGNOSTIC")
print("=" * 80)

# Build plant model
plant = FullStateSpaceModel()

print("\n" + "=" * 80)
print("STEP 1: PLANT MATRICES (from Step 2)")
print("=" * 80)

print("\nA_plant (4x4):")
print(plant.A)

print("\nB_plant (4x1):")
print(plant.B.T)

print("\nC_plant (1x4):")
print(plant.C)

# PID gains
Kp = params.Kp
Ki = params.Ki
Kd = params.Kd
Ks = params.Ks

print("\n" + "=" * 80)
print("STEP 2: PID GAINS (FROZEN)")
print("=" * 80)
print(f"Kp = {Kp}")
print(f"Ki = {Ki}")
print(f"Kd = {Kd}")
print(f"Ks = {Ks}")

# Extract pressure dynamics
pressure_index = 3
A_pressure_row = plant.A[pressure_index, :]
B_pressure = plant.B[pressure_index, 0]

print("\n" + "=" * 80)
print("STEP 3: PRESSURE DYNAMICS EXTRACTION")
print("=" * 80)
print(f"Pressure state index: {pressure_index}")
print(f"A[{pressure_index},:] = {A_pressure_row}")
print(f"B[{pressure_index}] = {B_pressure}")
print(f"\ndP/dt = A[{pressure_index},:] @ X + B[{pressure_index}] * u")
print(f"dP/dt = {A_pressure_row} @ X + {B_pressure} * u")

print("\n" + "=" * 80)
print("STEP 4: CONTROL LAW DERIVATION")
print("=" * 80)

print("\nError definition:")
print("  e = P_ref - P = P_ref - x[3]")

print("\nError derivative (for constant P_ref):")
print("  de/dt = -dP/dt")
print(f"  de/dt = -(A[{pressure_index},:] @ X + B[{pressure_index}] * u)")
print(f"  de/dt = -({A_pressure_row} @ X + {B_pressure} * u)")

print("\nPID control law:")
print("  u = Kp*e + Ki*e_int + Kd*de/dt")
print(f"  u = {Kp}*e + {Ki}*e_int + {Kd}*de/dt")

print("\nSubstitute e and de/dt:")
print(f"  u = {Kp}*(P_ref - x[3]) + {Ki}*x[4] + {Kd}*(-dP/dt)")
print(f"  u = {Kp}*(P_ref - x[3]) + {Ki}*x[4] - {Kd}*(A[{pressure_index},:] @ X + B[{pressure_index}]*u)")

print("\nExpand:")
print(f"  u = {Kp}*P_ref - {Kp}*x[3] + {Ki}*x[4] - {Kd}*A[{pressure_index},:] @ X - {Kd}*B[{pressure_index}]*u")

print("\nCollect u terms:")
print(f"  u + {Kd}*{B_pressure}*u = {Kp}*P_ref - {Kp}*x[3] + {Ki}*x[4] - {Kd}*A[{pressure_index},:] @ X")
print(f"  u*(1 + {Kd*B_pressure}) = {Kp}*P_ref - {Kp}*x[3] + {Ki}*x[4] - {Kd}*A[{pressure_index},:] @ X")

denom = 1.0 + Kd * B_pressure
print(f"\nDenominator: denom = 1 + {Kd}*{B_pressure} = {denom}")

print("\nSolve for u:")
print(f"  u = (1/{denom}) * [{Kp}*P_ref - {Kp}*x[3] + {Ki}*x[4] - {Kd}*A[{pressure_index},:] @ X]")

print("\n" + "=" * 80)
print("STEP 5: FEEDBACK GAIN COMPUTATION")
print("=" * 80)

K_feedback = np.zeros(4)
K_feedback[0] = -Kd * A_pressure_row[0] / denom
K_feedback[1] = -Kd * A_pressure_row[1] / denom
K_feedback[2] = -Kd * A_pressure_row[2] / denom
K_feedback[3] = (-Kp - Kd * A_pressure_row[3]) / denom

K_integral = Ki / denom
K_ref = Kp / denom

print(f"\nK_feedback (state feedback gains):")
print(f"  K[0] (current)  = -{Kd}*{A_pressure_row[0]}/{denom} = {K_feedback[0]}")
print(f"  K[1] (velocity) = -{Kd}*{A_pressure_row[1]}/{denom} = {K_feedback[1]}")
print(f"  K[2] (position) = -{Kd}*{A_pressure_row[2]}/{denom} = {K_feedback[2]}")
print(f"  K[3] (pressure) = (-{Kp} - {Kd}*{A_pressure_row[3]})/{denom} = {K_feedback[3]}")

print(f"\nK_integral (integral feedback):")
print(f"  K_int = {Ki}/{denom} = {K_integral}")

print(f"\nK_ref (reference feedforward):")
print(f"  K_ref = {Kp}/{denom} = {K_ref}")

print("\nControl law in feedback form:")
print(f"  u = {K_feedback} @ X_plant + {K_integral}*e_int + {K_ref}*P_ref")

print("\n" + "=" * 80)
print("STEP 6: CLOSED-LOOP A MATRIX CONSTRUCTION")
print("=" * 80)

# Build A_cl
A_cl = np.zeros((5, 5))

# Upper-left block: Plant with state feedback
A_cl_plant = plant.A + plant.B @ K_feedback.reshape(1, -1)
A_cl[0:4, 0:4] = A_cl_plant

print("\nUpper-left block (4x4): A_plant + B_plant @ K_feedback")
print("A_cl[0:4, 0:4] =")
print(A_cl_plant)

# Upper-right column: Integral feedback
A_cl[0:4, 4] = (plant.B * K_integral).flatten()

print("\nUpper-right column (4x1): B_plant * K_integral")
print(f"A_cl[0:4, 4] = {A_cl[0:4, 4]}")

# Bottom row: Integral state dynamics
A_cl[4, 3] = -1.0

print("\nBottom row (1x5): Integral state equation")
print(f"A_cl[4, :] = {A_cl[4, :]}")
print("  (ė_int = P_ref - P, so A_cl[4,3] = -1.0)")

print("\n" + "=" * 80)
print("FINAL A_cl MATRIX (5x5)")
print("=" * 80)
print(A_cl)

print("\n" + "=" * 80)
print("EIGENVALUES OF A_cl")
print("=" * 80)
eigenvalues = np.linalg.eigvals(A_cl)
eigenvalues = sorted(eigenvalues, key=lambda x: x.real)

for i, pole in enumerate(eigenvalues, 1):
    if abs(pole.imag) < 1e-10:
        print(f"  s{i} = {pole.real:.6f}")
    else:
        print(f"  s{i} = {pole.real:.6f} {'+' if pole.imag >= 0 else ''}{pole.imag:.6f}j")

print("\n" + "=" * 80)
