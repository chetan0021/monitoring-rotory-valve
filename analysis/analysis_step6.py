"""
Complete System Analysis - Step 6

Performs comprehensive analysis of the closed-loop system:
1. Eigenvalue verification
2. Step response analysis
3. Bode plot analysis
4. Gain and phase margins

All matrices and parameters from verified implementation.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from numpy.linalg import eig

# ============================================================
# PLANT MATRICES (From Verified Model)
# ============================================================
A = np.array([
    [-240.0, -160.0,   0.0,   0.0],
    [  32.64816204, 0.0, 0.0, 0.0],
    [   0.0, 1.0, 0.0, 0.0],
    [   0.0, 0.0, 7.5, -2.0]
])

B = np.array([
    [200.0],
    [0.0],
    [0.0],
    [0.0]
])

C = np.array([[0.0, 0.0, 0.0, 0.01]])

# ============================================================
# PID GAINS
# ============================================================
Kp = 115.2
Ki = 34.56
Kd = 49.92

# ============================================================
# BUILD AUGMENTED CLOSED-LOOP SYSTEM
# ============================================================
CB = C @ B
den = 1 + Kd * CB[0,0]

K_state = -(Kp*C + Kd*C@A) / den
K_int = Ki / den
K_ref = Kp / den

A_cl = np.zeros((5,5))
A_cl[0:4,0:4] = A + B @ K_state
A_cl[0:4,4]   = (B * K_int).flatten()
A_cl[4,0:4]   = -C
A_cl[4,4]     = 0.0

B_ref = np.zeros((5,1))
B_ref[0:4,0] = (B * K_ref).flatten()
B_ref[4,0] = 1.0

C_cl = np.array([[0,0,0,0.01,0]])

print("=" * 80)
print("COMPLETE SYSTEM ANALYSIS")
print("=" * 80)

# ============================================================
# 1️⃣ Eigenvalue Verification
# ============================================================
print("\n" + "=" * 80)
print("1. CLOSED-LOOP EIGENVALUES")
print("=" * 80)

eigvals = eig(A_cl)[0]
eigvals_sorted = sorted(eigvals, key=lambda x: x.real)

print("\nClosed-loop Poles:")
for i, val in enumerate(eigvals_sorted, 1):
    if abs(val.imag) < 1e-10:
        print(f"  s{i} = {val.real:.6f}")
    else:
        sign = '+' if val.imag >= 0 else ''
        print(f"  s{i} = {val.real:.6f} {sign}{val.imag:.6f}j")

# Check stability
all_stable = all(pole.real < 0 for pole in eigvals)
print(f"\nSystem Stable: {all_stable}")
if all_stable:
    print("✓ All poles in left half-plane")
else:
    print("⚠️  WARNING: System has unstable poles!")

# ============================================================
# 2️⃣ Step Response
# ============================================================
print("\n" + "=" * 80)
print("2. STEP RESPONSE ANALYSIS")
print("=" * 80)

sys_cl = signal.StateSpace(A_cl, B_ref, C_cl, 0)
t = np.linspace(0, 15, 2000)
t, y = signal.step(sys_cl, T=t)

# Compute metrics
final_value = y[-1]
peak_value = np.max(y)
overshoot = (peak_value - final_value) / final_value * 100

# Settling time (2% band)
within_band = np.where(np.abs(y - final_value) <= 0.02*final_value)[0]
settling_time = t[within_band[0]] if len(within_band) > 0 else None

# Rise time (10% to 90%)
val_10 = 0.1 * final_value
val_90 = 0.9 * final_value
idx_10 = np.where(y >= val_10)[0]
idx_90 = np.where(y >= val_90)[0]
rise_time = None
if len(idx_10) > 0 and len(idx_90) > 0:
    rise_time = t[idx_90[0]] - t[idx_10[0]]

print("\nStep Response Metrics:")
print(f"  Final Value: {final_value:.6f}")
print(f"  Peak Value: {peak_value:.6f}")
print(f"  Overshoot: {overshoot:.2f}%")
print(f"  Settling Time (2%): {settling_time:.3f} s" if settling_time else "  Settling Time: N/A")
print(f"  Rise Time (10%-90%): {rise_time:.3f} s" if rise_time else "  Rise Time: N/A")

# Plot step response
plt.figure(figsize=(10, 6))
plt.plot(t, y, 'b-', linewidth=2, label='Pressure Response')
plt.axhline(y=final_value, color='r', linestyle='--', alpha=0.5, label='Final Value')
plt.axhline(y=final_value*1.02, color='g', linestyle=':', alpha=0.3, label='±2% Band')
plt.axhline(y=final_value*0.98, color='g', linestyle=':', alpha=0.3)
plt.title("Closed-Loop Step Response", fontsize=14, fontweight='bold')
plt.xlabel("Time (s)", fontsize=12)
plt.ylabel("Pressure Output (bar)", fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('step_response.png', dpi=150)
print("\n✓ Step response plot saved as 'step_response.png'")

# ============================================================
# 3️⃣ Open-Loop Transfer Function for Bode
# ============================================================
print("\n" + "=" * 80)
print("3. BODE PLOT ANALYSIS")
print("=" * 80)

# Open-loop: G(s)*PID(s)
plant = signal.StateSpace(A, B, C, 0)
G = signal.ss2tf(A, B, C, 0)
numG = G[0][0]
denG = G[1]

# PID Transfer Function
numPID = [Kd, Kp, Ki]
denPID = [1, 0]

# Convolution for open-loop
numOL = np.convolve(numPID, numG)
denOL = np.convolve(denPID, denG)
sys_ol = signal.TransferFunction(numOL, denOL)

w, mag, phase = signal.bode(sys_ol)

# Plot Bode magnitude
plt.figure(figsize=(10, 5))
plt.semilogx(w, mag, 'b-', linewidth=2)
plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='0 dB')
plt.title("Open-Loop Bode Magnitude", fontsize=14, fontweight='bold')
plt.xlabel("Frequency (rad/s)", fontsize=12)
plt.ylabel("Magnitude (dB)", fontsize=12)
plt.grid(True, which='both', alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('bode_magnitude.png', dpi=150)
print("\n✓ Bode magnitude plot saved as 'bode_magnitude.png'")

# Plot Bode phase
plt.figure(figsize=(10, 5))
plt.semilogx(w, phase, 'b-', linewidth=2)
plt.axhline(y=-180, color='r', linestyle='--', alpha=0.5, label='-180°')
plt.title("Open-Loop Bode Phase", fontsize=14, fontweight='bold')
plt.xlabel("Frequency (rad/s)", fontsize=12)
plt.ylabel("Phase (degrees)", fontsize=12)
plt.grid(True, which='both', alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('bode_phase.png', dpi=150)
print("✓ Bode phase plot saved as 'bode_phase.png'")

# ============================================================
# 4️⃣ Gain & Phase Margins
# ============================================================
print("\n" + "=" * 80)
print("4. STABILITY MARGINS")
print("=" * 80)

# Compute margins manually from Bode data
# Gain crossover: where |G(jw)| = 1 (0 dB)
idx_gc = np.where(np.diff(np.sign(mag)))[0]
if len(idx_gc) > 0:
    wg = w[idx_gc[0]]
    phase_at_gc = phase[idx_gc[0]]
    pm = 180 + phase_at_gc
else:
    wg = None
    pm = None

# Phase crossover: where phase = -180°
idx_pc = np.where(np.diff(np.sign(phase + 180)))[0]
if len(idx_pc) > 0:
    wp = w[idx_pc[0]]
    mag_at_pc = mag[idx_pc[0]]
    gm_db = -mag_at_pc
else:
    wp = None
    gm_db = None

print("\nStability Margins:")
if gm_db is not None:
    print(f"  Gain Margin: {gm_db:.2f} dB")
    print(f"  Phase Crossover Frequency: {wp:.4f} rad/s")
else:
    print("  Gain Margin: N/A (no phase crossover)")

if pm is not None:
    print(f"  Phase Margin: {pm:.2f}°")
    print(f"  Gain Crossover Frequency: {wg:.4f} rad/s")
else:
    print("  Phase Margin: N/A (no gain crossover)")

# ============================================================
# 5️⃣ Summary Report
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY REPORT")
print("=" * 80)

print("\n✓ System Configuration:")
print(f"  - PID Gains: Kp={Kp}, Ki={Ki}, Kd={Kd}")
print(f"  - System Order: 5 (4 plant states + 1 integral)")
print(f"  - Stability: {'STABLE' if all_stable else 'UNSTABLE'}")

print("\n✓ Performance:")
print(f"  - Overshoot: {overshoot:.2f}%")
print(f"  - Settling Time: {settling_time:.3f} s" if settling_time else "  - Settling Time: N/A")
print(f"  - Rise Time: {rise_time:.3f} s" if rise_time else "  - Rise Time: N/A")

print("\n✓ Robustness:")
if gm_db is not None:
    print(f"  - Gain Margin: {gm_db:.2f} dB")
else:
    print("  - Gain Margin: N/A")
if pm is not None:
    print(f"  - Phase Margin: {pm:.2f}°")
else:
    print("  - Phase Margin: N/A")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

# Show all plots
plt.show()
