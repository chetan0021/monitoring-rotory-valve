"""
Compute eigenvalues of closed-loop A matrix.
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.closed_loop_model import ClosedLoopSystem

# Build closed-loop system
cl_system = ClosedLoopSystem()

# Get closed-loop A matrix
A_cl = cl_system.A_cl

# Compute eigenvalues
eigenvalues = np.linalg.eigvals(A_cl)

# Sort by real part (most negative first)
eigenvalues = sorted(eigenvalues, key=lambda x: x.real)

print("=" * 70)
print("CLOSED-LOOP EIGENVALUES (POLES)")
print("=" * 70)
print("\nPID Gains Used:")
print(f"  Kp = {cl_system.Kp}")
print(f"  Ki = {cl_system.Ki}")
print(f"  Kd = {cl_system.Kd}")
print(f"  Ks = {cl_system.Ks}")

print("\nClosed-Loop Poles:")
for i, pole in enumerate(eigenvalues, 1):
    if abs(pole.imag) < 1e-10:
        print(f"  s{i} = {pole.real:.6f}")
    else:
        print(f"  s{i} = {pole.real:.6f} {'+' if pole.imag >= 0 else ''}{pole.imag:.6f}j")

print("\n" + "=" * 70)
