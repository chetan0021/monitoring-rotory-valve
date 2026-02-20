"""
State-Space Model Unit Tests

Validates full state-space model implementation against documentation.
References:
- docs/numerical_state_space_and_simulation_specification.md (Section 4)
- docs/industrial_pressure_control_system_design.md (Section 2.7)
"""

import unittest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.full_state_space_model import FullStateSpaceModel
from config.system_parameters import params


class TestStateSpaceModel(unittest.TestCase):
    """
    Unit tests for FullStateSpaceModel class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.model = FullStateSpaceModel()
    
    def test_total_inertia_computation(self):
        """
        Test total inertia computation.
        
        Equation: J_total = Jm + J_ref
        where J_ref = J_valve/(η*N^2)
        
        Expected from corrected parameters:
        J_ref = 6.125 / (0.85 * 40^2) = 0.004503676
        J_total = 0.02 + 0.004503676 = 0.024503676 kg·m²
        """
        # Compute expected values
        expected_J_ref = params.J_valve / (params.eta * params.N**2)
        expected_J_total = params.J_m + expected_J_ref
        
        tolerance = 1e-6
        
        self.assertAlmostEqual(self.model.J_ref, expected_J_ref, delta=tolerance,
                              msg=f"J_ref mismatch: got {self.model.J_ref}, expected {expected_J_ref}")
        self.assertAlmostEqual(self.model.J_total, expected_J_total, delta=tolerance,
                              msg=f"J_total mismatch: got {self.model.J_total}, expected {expected_J_total}")
        
        print(f"✓ J_ref = {self.model.J_ref:.9f} kg·m²")
        print(f"✓ J_total = {self.model.J_total:.9f} kg·m²")
    
    def test_A_matrix_structure(self):
        """
        Test A matrix structure and dimensions.
        
        Expected: 4x4 matrix with structure defined in Section 4
        """
        self.assertEqual(self.model.A.shape, (4, 4), "A matrix should be 4x4")
        
        # Test specific elements with corrected parameters
        # A[0,0] = -R/L = -1.2/0.005 = -240
        expected_A00 = -params.R / params.L
        self.assertAlmostEqual(self.model.A[0, 0], expected_A00, places=6)
        
        # A[0,1] = -Ke/L = -0.8/0.005 = -160
        expected_A01 = -params.Ke / params.L
        self.assertAlmostEqual(self.model.A[0, 1], expected_A01, places=6)
        
        # A[1,0] = Kt/J_total = 0.8/0.024503676 ≈ 32.648
        expected_A10 = params.Kt / self.model.J_total
        self.assertAlmostEqual(self.model.A[1, 0], expected_A10, places=6)
        
        # A[2,1] = 1.0
        self.assertAlmostEqual(self.model.A[2, 1], 1.0, places=6)
        
        # A[3,2] = Kp_pressure/(N*τp) = 150/(40*0.5) = 7.5
        expected_A32 = params.Kp_pressure / (params.N * params.tau_p)
        self.assertAlmostEqual(self.model.A[3, 2], expected_A32, places=6)
        
        # A[3,3] = -1/τp = -1/0.5 = -2.0
        expected_A33 = -1.0 / params.tau_p
        self.assertAlmostEqual(self.model.A[3, 3], expected_A33, places=6)
        
        print("✓ A matrix structure validated")
        print(f"  A[0,0] = -R/L = {self.model.A[0,0]:.6f}")
        print(f"  A[0,1] = -Ke/L = {self.model.A[0,1]:.6f}")
        print(f"  A[1,0] = Kt/J_total = {self.model.A[1,0]:.6f}")
        print(f"  A[3,2] = Kp/(N*τp) = {self.model.A[3,2]:.6f}")
        print(f"  A[3,3] = -1/τp = {self.model.A[3,3]:.6f}")
    
    def test_B_matrix_structure(self):
        """
        Test B matrix structure and dimensions.
        
        Expected: 4x1 vector [1/L, 0, 0, 0]^T
        """
        self.assertEqual(self.model.B.shape, (4, 1), "B matrix should be 4x1")
        
        # B[0,0] = 1/L = 1/0.005 = 200
        expected_B00 = 1.0 / params.L
        self.assertAlmostEqual(self.model.B[0, 0], expected_B00, places=6)
        
        # Rest should be zero
        self.assertAlmostEqual(self.model.B[1, 0], 0.0, places=6)
        self.assertAlmostEqual(self.model.B[2, 0], 0.0, places=6)
        self.assertAlmostEqual(self.model.B[3, 0], 0.0, places=6)
        
        print("✓ B matrix structure validated")
        print(f"  B[0,0] = 1/L = {self.model.B[0,0]:.6f}")
    
    def test_C_matrix_structure(self):
        """
        Test C matrix structure and dimensions.
        
        Expected: 1x4 vector [0, 0, 0, Ks]
        """
        self.assertEqual(self.model.C.shape, (1, 4), "C matrix should be 1x4")
        
        # First three elements should be zero
        self.assertAlmostEqual(self.model.C[0, 0], 0.0, places=6)
        self.assertAlmostEqual(self.model.C[0, 1], 0.0, places=6)
        self.assertAlmostEqual(self.model.C[0, 2], 0.0, places=6)
        
        # C[0,3] = Ks
        self.assertAlmostEqual(self.model.C[0, 3], params.Ks, places=6)
        
        print("✓ C matrix structure validated")
    
    def test_D_matrix_structure(self):
        """
        Test D matrix (feedthrough).
        
        Expected: D = 0
        """
        self.assertEqual(self.model.D.shape, (1, 1), "D should be 1x1")
        self.assertAlmostEqual(self.model.D[0, 0], 0.0, places=6)
        
        print("✓ D matrix validated (zero feedthrough)")
    
    def test_state_derivative_computation(self):
        """
        Test state derivative computation.
        
        Equation: dX/dt = A*X + B*U
        """
        # Test state
        X = np.array([1.0, 2.0, 3.0, 100.0])  # [i, ω, θm, P]
        U = 10.0  # Voltage
        t = 0.0
        
        # Compute derivative
        dX_dt = self.model.state_derivative(t, X, U)
        
        # Manually compute expected
        X_col = X.reshape(-1, 1)
        U_col = np.array([[U]])
        expected_dX_dt = (self.model.A @ X_col + self.model.B @ U_col).flatten()
        
        # Compare
        np.testing.assert_array_almost_equal(dX_dt, expected_dX_dt, decimal=6)
        
        print("✓ State derivative computation validated")
    
    def test_output_computation(self):
        """
        Test output computation.
        
        Equation: Y = C*X + D*U
        """
        # Test state
        X = np.array([1.0, 2.0, 3.0, 100.0])  # [i, ω, θm, P]
        
        # Compute output
        Y = self.model.output(X)
        
        # Expected: Y = Ks * P = 0.01 * 100 = 1.0
        expected_Y = params.Ks * X[3]
        
        self.assertAlmostEqual(Y, expected_Y, places=6)
        
        print("✓ Output computation validated")


if __name__ == '__main__':
    unittest.main(verbosity=2)
