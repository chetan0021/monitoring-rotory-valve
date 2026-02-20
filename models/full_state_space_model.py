"""
Full State-Space Model Module

Implements the complete 4-state system model combining:
- Motor electrical dynamics
- Motor mechanical dynamics
- Gearbox coupling
- Pressure process dynamics

All equations and matrices are defined in:
- docs/numerical_state_space_and_simulation_specification.md (Section 3, 4)

State Vector:
X = [i, ω, θm, P]^T

where:
- i: Armature current (A)
- ω: Motor angular velocity (rad/s)
- θm: Motor angular position (rad)
- P: Tube pressure (bar)

State-Space Form:
dX/dt = A*X + B*U
Y = C*X + D*U

where:
- U = V (applied voltage)
- Y = Ks*P (sensor output voltage)

A Matrix (4x4):
A = [
 -R/L        -Ke/L       0               0
  Kt/J_total  0          0               0
  0           1          0               0
  0           0    Kp_pressure/(N*τp)   -1/τp
]

B Vector (4x1):
B = [1/L, 0, 0, 0]^T

C Vector (1x4):
C = [0, 0, 0, Ks]

D Scalar:
D = 0
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.system_parameters import params
from models.motor_model import MotorModel
from models.pressure_model import PressureModel


class FullStateSpaceModel:
    """
    Complete 4-state system model.
    
    References:
    - numerical_state_space_and_simulation_specification.md: Section 3, 4
    """
    
    def __init__(self):
        """
        Initialize full state-space model from centralized parameters.
        """
        # Load parameters
        self.R = params.R
        self.L = params.L
        self.Kt = params.Kt
        self.Ke = params.Ke
        self.J_m = params.J_m
        self.J_ref = params.J_ref
        self.N = params.N
        self.Kp_pressure = params.Kp_pressure
        self.tau_p = params.tau_p
        self.Ks = params.Ks
        
        # Compute total inertia
        self.J_total = self.compute_total_inertia()
        
        # State-space matrices (to be computed)
        self.A = None  # 4x4 system matrix
        self.B = None  # 4x1 input matrix
        self.C = None  # 1x4 output matrix
        self.D = None  # Scalar feedthrough
        
        # Build matrices
        self.build_state_space_matrices()
    
    def compute_total_inertia(self):
        """
        Compute total inertia at motor shaft.
        
        Equation: J_total = Jm + J_ref
        where J_ref = J_valve/N^2
        Reference: Section 1.1 of numerical_state_space_and_simulation_specification.md
        
        Returns:
            J_total: Total inertia (kg·m²)
        """
        J_total = self.J_m + self.J_ref
        return J_total
    
    def build_state_space_matrices(self):
        """
        Construct A, B, C, D matrices from component parameters.
        
        Matrix definitions from Section 4 of numerical_state_space_and_simulation_specification.md
        
        A = [
         -R/L        -Ke/L       0               0
          Kt/J_total  0          0               0
          0           1          0               0
          0           0    Kp_pressure/(N*τp)   -1/τp
        ]
        
        B = [1/L, 0, 0, 0]^T
        C = [0, 0, 0, Ks]
        D = 0
        
        Returns:
            A, B, C, D: State-space matrices
        """
        # Build A matrix (4x4)
        self.A = np.array([
            [-self.R / self.L,  -self.Ke / self.L,  0.0,  0.0],
            [self.Kt / self.J_total,  0.0,  0.0,  0.0],
            [0.0,  1.0,  0.0,  0.0],
            [0.0,  0.0,  self.Kp_pressure / (self.N * self.tau_p),  -1.0 / self.tau_p]
        ])
        
        # Build B matrix (4x1)
        self.B = np.array([
            [1.0 / self.L],
            [0.0],
            [0.0],
            [0.0]
        ])
        
        # Build C matrix (1x4)
        self.C = np.array([[0.0, 0.0, 0.0, self.Ks]])
        
        # Build D scalar
        self.D = np.array([[0.0]])
        
        return self.A, self.B, self.C, self.D
    
    def state_derivative(self, t, X, U):
        """
        Compute state derivative dX/dt = A*X + B*U
        
        Args:
            t: Time (s)
            X: State vector [i, ω, θm, P]
            U: Input voltage (V)
        
        Returns:
            dX_dt: State derivative vector
        """
        X = np.array(X).reshape(-1, 1)  # Ensure column vector
        U_vec = np.array([[U]])  # Scalar to array
        
        dX_dt = self.A @ X + self.B @ U_vec
        
        return dX_dt.flatten()  # Return as 1D array for ODE solver
    
    def output(self, X):
        """
        Compute output Y = C*X + D*U
        
        Args:
            X: State vector [i, ω, θm, P]
        
        Returns:
            Y: Sensor output voltage (V)
        """
        X = np.array(X).reshape(-1, 1)  # Ensure column vector
        Y = self.C @ X + self.D
        return Y[0, 0]  # Return scalar
    
    def validate_matrices(self):
        """
        Validate that state-space matrices are correctly formed.
        Check dimensions and numerical values against documentation.
        """
        print("\n" + "=" * 70)
        print("STATE-SPACE MATRICES VALIDATION")
        print("=" * 70)
        
        # Check dimensions
        print("\n--- Matrix Dimensions ---")
        print(f"A: {self.A.shape} (expected: (4, 4))")
        print(f"B: {self.B.shape} (expected: (4, 1))")
        print(f"C: {self.C.shape} (expected: (1, 4))")
        print(f"D: {self.D.shape} (expected: (1, 1))")
        
        assert self.A.shape == (4, 4), "A matrix dimension mismatch"
        assert self.B.shape == (4, 1), "B matrix dimension mismatch"
        assert self.C.shape == (1, 4), "C matrix dimension mismatch"
        assert self.D.shape == (1, 1), "D matrix dimension mismatch"
        print("✓ All matrix dimensions correct")
        
        # Print matrices
        print("\n--- A Matrix ---")
        print(self.A)
        
        print("\n--- B Matrix ---")
        print(self.B.T)  # Transpose for better display
        
        print("\n--- C Matrix ---")
        print(self.C)
        
        print("\n--- D Matrix ---")
        print(self.D)
        
        # Validate specific elements
        print("\n--- Key Matrix Elements ---")
        print(f"A[0,0] = -R/L = {self.A[0,0]:.6f} (expected: {-self.R/self.L:.6f})")
        print(f"A[0,1] = -Ke/L = {self.A[0,1]:.6f} (expected: {-self.Ke/self.L:.6f})")
        print(f"A[1,0] = Kt/J_total = {self.A[1,0]:.6f} (expected: {self.Kt/self.J_total:.6f})")
        print(f"A[2,1] = 1.0 = {self.A[2,1]:.6f}")
        print(f"A[3,2] = Kp/(N*τp) = {self.A[3,2]:.6f} (expected: {self.Kp_pressure/(self.N*self.tau_p):.6f})")
        print(f"A[3,3] = -1/τp = {self.A[3,3]:.6f} (expected: {-1.0/self.tau_p:.6f})")
        print(f"B[0,0] = 1/L = {self.B[0,0]:.6f} (expected: {1.0/self.L:.6f})")
        print(f"C[0,3] = Ks = {self.C[0,3]:.6f} (expected: {self.Ks:.6f})")
        
        print("\n--- Derived Parameters ---")
        print(f"J_ref = {self.J_ref:.9f} kg·m²")
        print(f"J_total = {self.J_total:.9f} kg·m²")
        
        print("=" * 70)


if __name__ == "__main__":
    model = FullStateSpaceModel()
    model.validate_matrices()
