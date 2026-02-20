"""
Closed-Loop Augmented State-Space Model

Implements the closed-loop system with PID controller augmentation.
All parameters and gains are FROZEN from documentation.

References:
- docs/industrial_pressure_control_system_design.md (Section 3)
- docs/numerical_state_space_and_simulation_specification.md (Section 5)

Augmented State Vector:
X_aug = [i, ω, θm, P, e_int]^T

where:
- i: Armature current (A)
- ω: Motor angular velocity (rad/s)
- θm: Motor angular position (rad)
- P: Tube pressure (bar)
- e_int: Integral of pressure error (bar·s)

PID Control Law (FROZEN):
u = Kp*e + Ki*e_int + Kd*de/dt

where:
- e = P_ref - P
- de/dt = -dP/dt (for constant reference)
- Kp = 115.2 (FROZEN)
- Ki = 34.56 (FROZEN)
- Kd = 49.92 (FROZEN)

Closed-Loop Form:
Ẋ_aug = A_cl * X_aug + B_ref * P_ref
Y = C_cl * X_aug
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.system_parameters import params
from models.full_state_space_model import FullStateSpaceModel


class ClosedLoopSystem:
    """
    Closed-loop system with PID controller augmentation.
    
    References:
    - industrial_pressure_control_system_design.md: Section 3
    - numerical_state_space_and_simulation_specification.md: Section 5
    """
    
    def __init__(self):
        """
        Initialize closed-loop system from plant model and PID gains.
        """
        # Load plant model (verified from Step 2)
        self.plant = FullStateSpaceModel()
        
        # Extract plant matrices
        self.A_plant = self.plant.A  # 4x4
        self.B_plant = self.plant.B  # 4x1
        self.C_plant = self.plant.C  # 1x4 (pressure output)
        self.D_plant = self.plant.D  # 1x1
        
        # Load PID gains (FROZEN)
        self.Kp = params.Kp
        self.Ki = params.Ki
        self.Kd = params.Kd
        
        # Sensor gain
        self.Ks = params.Ks
        
        # Augmented system matrices (to be built)
        self.A_cl = None  # 5x5 closed-loop system matrix
        self.B_ref = None  # 5x1 reference input matrix
        self.C_cl = None  # 1x5 output matrix
        
        # Build augmented matrices
        self.build_augmented_matrices()
    
    def build_augmented_matrices(self):
        """
        Build closed-loop augmented state-space matrices.
        
        Augmented state: X_aug = [i, ω, θm, P, e_int]^T
        
        System equations:
        1. Plant dynamics: Ẋ_plant = A*X + B*u
        2. Error: e = P_ref - P
        3. Integral: ė_int = e = P_ref - P
        4. PID law: u = Kp*e + Ki*e_int + Kd*de/dt
        5. Error derivative: de/dt = -dP/dt (for constant P_ref)
        
        Closed-loop form:
        Ẋ_aug = A_cl * X_aug + B_ref * P_ref
        
        Construction approach:
        - Extract pressure row from plant A matrix (row 3, index 3)
        - Compute dP/dt = A[3,:] * X + B[3] * u
        - Substitute PID law into plant dynamics
        - Add integral state equation
        """
        # Extract dimensions
        n_plant = self.A_plant.shape[0]  # 4
        n_aug = n_plant + 1  # 5 (add integral state)
        
        # Initialize augmented matrices
        self.A_cl = np.zeros((n_aug, n_aug))
        self.B_ref = np.zeros((n_aug, 1))
        self.C_cl = np.zeros((1, n_aug))
        
        # ================================================================
        # STEP 1: Extract pressure output row from C matrix
        # C_plant = [0, 0, 0, Ks] extracts pressure
        # Pressure is state x[3] (index 3)
        # ================================================================
        pressure_index = 3  # P is the 4th state (index 3)
        
        # ================================================================
        # STEP 2: Compute error and its derivative
        # e = P_ref - P = P_ref - x[3]
        # de/dt = -dP/dt = -(A[3,:] @ X + B[3] * u)
        # ================================================================
        # Extract pressure dynamics row from A matrix
        A_pressure_row = self.A_plant[pressure_index, :]  # Row that computes dP/dt
        B_pressure = self.B_plant[pressure_index, 0]  # Pressure row of B
        
        # ================================================================
        # STEP 3: PID Control Law
        # u = Kp*e + Ki*e_int + Kd*de/dt
        # u = Kp*(P_ref - P) + Ki*e_int + Kd*(-dP/dt)
        # u = Kp*(P_ref - x[3]) + Ki*x[4] + Kd*(-(A[3,:] @ X + B[3]*u))
        # 
        # Solve for u:
        # u = Kp*P_ref - Kp*x[3] + Ki*x[4] - Kd*A[3,:] @ X - Kd*B[3]*u
        # u + Kd*B[3]*u = Kp*P_ref - Kp*x[3] + Ki*x[4] - Kd*A[3,:] @ X
        # u*(1 + Kd*B[3]) = Kp*P_ref - Kp*x[3] + Ki*x[4] - Kd*A[3,:] @ X
        # u = (Kp*P_ref - Kp*x[3] + Ki*x[4] - Kd*A[3,:] @ X) / (1 + Kd*B[3])
        # ================================================================
        
        # Compute denominator for PID feedback
        denom = 1.0 + self.Kd * B_pressure
        
        # Compute feedback gains for each state
        # u = (1/denom) * [Kp*P_ref - Kp*x[3] + Ki*x[4] - Kd*A[3,:] @ X]
        # u = (1/denom) * [Kp*P_ref + (-Kd*A[3,0])*x[0] + (-Kd*A[3,1])*x[1] 
        #                  + (-Kd*A[3,2])*x[2] + (-Kp - Kd*A[3,3])*x[3] + Ki*x[4]]
        
        # Feedback gain vector for plant states [i, ω, θm, P]
        K_feedback = np.zeros(n_plant)
        K_feedback[0] = -self.Kd * A_pressure_row[0]  # Current
        K_feedback[1] = -self.Kd * A_pressure_row[1]  # Velocity
        K_feedback[2] = -self.Kd * A_pressure_row[2]  # Position
        K_feedback[3] = -self.Kp - self.Kd * A_pressure_row[3]  # Pressure
        
        # Integral state feedback
        K_integral = self.Ki
        
        # Reference feedforward
        K_ref = self.Kp
        
        # Scale by denominator
        K_feedback = K_feedback / denom
        K_integral = K_integral / denom
        K_ref = K_ref / denom
        
        # ================================================================
        # STEP 4: Build closed-loop A matrix (5x5)
        # 
        # Plant dynamics with feedback:
        # Ẋ_plant = A*X + B*u
        # where u = K_feedback @ X_plant + K_integral * e_int + K_ref * P_ref
        # 
        # Ẋ_plant = A*X + B*(K_feedback @ X_plant + K_integral * e_int)
        # Ẋ_plant = (A + B*K_feedback) @ X_plant + B*K_integral * e_int
        # 
        # Integral dynamics:
        # ė_int = P_ref - P = P_ref - x[3]
        # ================================================================
        
        # Upper-left block: Plant dynamics with state feedback (4x4)
        A_cl_plant = self.A_plant + self.B_plant @ K_feedback.reshape(1, -1)
        self.A_cl[0:n_plant, 0:n_plant] = A_cl_plant
        
        # Upper-right column: Integral feedback to plant states (4x1)
        self.A_cl[0:n_plant, n_plant] = (self.B_plant * K_integral).flatten()
        
        # Bottom row: Integral state dynamics (1x5)
        # ė_int = P_ref - P = -x[3] (when P_ref contribution goes to B_ref)
        self.A_cl[n_plant, pressure_index] = -1.0  # -P term
        # All other states don't affect integral directly
        
        # ================================================================
        # STEP 5: Build reference input matrix B_ref (5x1)
        # 
        # Plant states: affected by u, which has K_ref * P_ref term
        # Integral state: affected by P_ref directly
        # ================================================================
        
        # Plant states get reference through control input
        self.B_ref[0:n_plant, 0] = (self.B_plant * K_ref).flatten()
        
        # Integral state gets reference directly
        self.B_ref[n_plant, 0] = 1.0  # +P_ref term in ė_int
        
        # ================================================================
        # STEP 6: Build output matrix C_cl (1x5)
        # 
        # Output is pressure: y = P = x[3]
        # ================================================================
        self.C_cl[0, pressure_index] = 1.0  # Extract pressure state
        
    def get_state_space_model(self):
        """
        Get closed-loop state-space matrices.
        
        Returns:
            A_cl: 5x5 closed-loop system matrix
            B_ref: 5x1 reference input matrix
            C_cl: 1x5 output matrix
        """
        return self.A_cl, self.B_ref, self.C_cl
    
    def state_derivative(self, t, X_aug, P_ref):
        """
        Compute augmented state derivative.
        
        Ẋ_aug = A_cl * X_aug + B_ref * P_ref
        
        Args:
            t: Time (s)
            X_aug: Augmented state vector [i, ω, θm, P, e_int]
            P_ref: Reference pressure (bar)
        
        Returns:
            dX_aug_dt: Augmented state derivative
        """
        X_aug = np.array(X_aug).reshape(-1, 1)
        P_ref_vec = np.array([[P_ref]])
        
        dX_aug_dt = self.A_cl @ X_aug + self.B_ref @ P_ref_vec
        
        return dX_aug_dt.flatten()
    
    def output(self, X_aug):
        """
        Compute output (pressure).
        
        Y = C_cl * X_aug
        
        Args:
            X_aug: Augmented state vector [i, ω, θm, P, e_int]
        
        Returns:
            Y: Pressure output (bar)
        """
        X_aug = np.array(X_aug).reshape(-1, 1)
        Y = self.C_cl @ X_aug
        return Y[0, 0]
    
    def validate_against_documentation(self):
        """
        Validate closed-loop system against documentation.
        
        Checks:
        - Matrix dimensions
        - PID gains match documentation
        - Sensor gain matches documentation
        - No parameter drift
        """
        print("\n" + "=" * 70)
        print("CLOSED-LOOP SYSTEM VALIDATION")
        print("=" * 70)
        
        # Check dimensions
        print("\n--- Matrix Dimensions ---")
        print(f"A_cl: {self.A_cl.shape} (expected: (5, 5))")
        print(f"B_ref: {self.B_ref.shape} (expected: (5, 1))")
        print(f"C_cl: {self.C_cl.shape} (expected: (1, 5))")
        
        assert self.A_cl.shape == (5, 5), "A_cl dimension mismatch"
        assert self.B_ref.shape == (5, 1), "B_ref dimension mismatch"
        assert self.C_cl.shape == (1, 5), "C_cl dimension mismatch"
        print("✓ All matrix dimensions correct")
        
        # Check PID gains
        print("\n--- PID Gains (FROZEN) ---")
        print(f"Kp = {self.Kp} (expected: 115.2)")
        print(f"Ki = {self.Ki} (expected: 34.56)")
        print(f"Kd = {self.Kd} (expected: 49.92)")
        
        assert abs(self.Kp - 115.2) < 1e-6, "Kp mismatch"
        assert abs(self.Ki - 34.56) < 1e-6, "Ki mismatch"
        assert abs(self.Kd - 49.92) < 1e-6, "Kd mismatch"
        print("✓ All PID gains match documentation")
        
        # Check sensor gain
        print("\n--- Sensor Gain ---")
        print(f"Ks = {self.Ks} (expected: 0.01)")
        assert abs(self.Ks - 0.01) < 1e-6, "Ks mismatch"
        print("✓ Sensor gain matches documentation")
        
        # Print matrices
        print("\n--- A_cl Matrix (5x5) ---")
        print(self.A_cl)
        
        print("\n--- B_ref Matrix (5x1) ---")
        print(self.B_ref.T)  # Transpose for better display
        
        print("\n--- C_cl Matrix (1x5) ---")
        print(self.C_cl)
        
        # Structural checks
        print("\n--- Structural Checks ---")
        print(f"C_cl extracts pressure (state 3): C_cl[0,3] = {self.C_cl[0,3]} (expected: 1.0)")
        assert abs(self.C_cl[0, 3] - 1.0) < 1e-6, "Output matrix doesn't extract pressure correctly"
        print("✓ Output matrix correctly extracts pressure")
        
        print(f"Integral state equation: A_cl[4,3] = {self.A_cl[4,3]} (expected: -1.0)")
        assert abs(self.A_cl[4, 3] - (-1.0)) < 1e-6, "Integral state equation incorrect"
        print("✓ Integral state equation correct")
        
        print(f"Reference to integral: B_ref[4,0] = {self.B_ref[4,0]} (expected: 1.0)")
        assert abs(self.B_ref[4, 0] - 1.0) < 1e-6, "Reference input to integral incorrect"
        print("✓ Reference input to integral correct")
        
        print("\n" + "=" * 70)
        print("✓ CLOSED-LOOP SYSTEM VALIDATED")
        print("=" * 70)


if __name__ == "__main__":
    # Test closed-loop system construction
    cl_system = ClosedLoopSystem()
    cl_system.validate_against_documentation()
