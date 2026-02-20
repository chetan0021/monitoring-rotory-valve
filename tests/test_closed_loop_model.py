"""
Closed-Loop Model Unit Tests

Validates closed-loop augmented state-space model implementation.
References:
- docs/industrial_pressure_control_system_design.md (Section 3)
- docs/numerical_state_space_and_simulation_specification.md (Section 5)
"""

import unittest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.closed_loop_model import ClosedLoopSystem
from config.system_parameters import params


class TestClosedLoopModel(unittest.TestCase):
    """
    Unit tests for ClosedLoopSystem class.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.cl_system = ClosedLoopSystem()
    
    def test_matrix_dimensions(self):
        """
        Test that all matrices have correct dimensions.
        
        Expected:
        - A_cl: 5x5 (augmented with integral state)
        - B_ref: 5x1 (reference input)
        - C_cl: 1x5 (pressure output)
        """
        self.assertEqual(self.cl_system.A_cl.shape, (5, 5), 
                        "A_cl should be 5x5")
        self.assertEqual(self.cl_system.B_ref.shape, (5, 1), 
                        "B_ref should be 5x1")
        self.assertEqual(self.cl_system.C_cl.shape, (1, 5), 
                        "C_cl should be 1x5")
        
        print("✓ All matrix dimensions correct")
    
    def test_pid_gains_frozen(self):
        """
        Test that PID gains match frozen documentation values.
        
        CRITICAL: These values must NEVER change.
        Expected from industrial_pressure_control_system_design.md Section 3.6:
        - Kp = 115.2
        - Ki = 34.56
        - Kd = 49.92
        """
        self.assertAlmostEqual(self.cl_system.Kp, 115.2, places=6,
                              msg="Kp must be 115.2 (FROZEN)")
        self.assertAlmostEqual(self.cl_system.Ki, 34.56, places=6,
                              msg="Ki must be 34.56 (FROZEN)")
        self.assertAlmostEqual(self.cl_system.Kd, 49.92, places=6,
                              msg="Kd must be 49.92 (FROZEN)")
        
        print("✓ PID gains match frozen documentation values")
        print(f"  Kp = {self.cl_system.Kp}")
        print(f"  Ki = {self.cl_system.Ki}")
        print(f"  Kd = {self.cl_system.Kd}")
    
    def test_sensor_gain_consistency(self):
        """
        Test that sensor gain matches documentation.
        
        Expected: Ks = 0.01 V/bar
        """
        self.assertAlmostEqual(self.cl_system.Ks, 0.01, places=6,
                              msg="Sensor gain must be 0.01")
        
        print("✓ Sensor gain matches documentation")
    
    def test_output_matrix_structure(self):
        """
        Test that C_cl correctly extracts pressure state.
        
        Pressure is state x[3] (4th state, index 3).
        C_cl should be [0, 0, 0, 1, 0] to extract pressure.
        """
        expected_C_cl = np.array([[0.0, 0.0, 0.0, 1.0, 0.0]])
        
        np.testing.assert_array_almost_equal(self.cl_system.C_cl, expected_C_cl,
                                            decimal=6,
                                            err_msg="C_cl must extract pressure state")
        
        print("✓ Output matrix correctly extracts pressure")
    
    def test_integral_state_equation(self):
        """
        Test that integral state equation is correct.
        
        Integral state dynamics: ė_int = P_ref - P
        In matrix form: ė_int = -x[3] + P_ref
        
        This means:
        - A_cl[4, 3] = -1.0 (negative pressure feedback)
        - B_ref[4, 0] = 1.0 (positive reference)
        """
        # Check integral state row in A_cl
        self.assertAlmostEqual(self.cl_system.A_cl[4, 3], -1.0, places=6,
                              msg="Integral state must have -P term")
        
        # Check that other plant states don't directly affect integral
        self.assertAlmostEqual(self.cl_system.A_cl[4, 0], 0.0, places=6)
        self.assertAlmostEqual(self.cl_system.A_cl[4, 1], 0.0, places=6)
        self.assertAlmostEqual(self.cl_system.A_cl[4, 2], 0.0, places=6)
        
        # Check integral state doesn't feed back to itself
        self.assertAlmostEqual(self.cl_system.A_cl[4, 4], 0.0, places=6)
        
        # Check reference input to integral
        self.assertAlmostEqual(self.cl_system.B_ref[4, 0], 1.0, places=6,
                              msg="Integral state must have +P_ref term")
        
        print("✓ Integral state equation correct")
        print(f"  A_cl[4,3] = {self.cl_system.A_cl[4,3]} (error feedback)")
        print(f"  B_ref[4,0] = {self.cl_system.B_ref[4,0]} (reference)")
    
    def test_plant_parameters_no_drift(self):
        """
        Test that plant parameters haven't drifted from Step 2.
        
        This ensures closed-loop construction used correct plant model.
        """
        # Check plant matrix dimensions
        self.assertEqual(self.cl_system.A_plant.shape, (4, 4))
        self.assertEqual(self.cl_system.B_plant.shape, (4, 1))
        self.assertEqual(self.cl_system.C_plant.shape, (1, 4))
        
        # Check key plant parameters
        self.assertAlmostEqual(self.cl_system.plant.R, params.R, places=6)
        self.assertAlmostEqual(self.cl_system.plant.L, params.L, places=6)
        self.assertAlmostEqual(self.cl_system.plant.Kt, params.Kt, places=6)
        self.assertAlmostEqual(self.cl_system.plant.Ke, params.Ke, places=6)
        
        print("✓ Plant parameters consistent with Step 2")
    
    def test_state_derivative_computation(self):
        """
        Test state derivative computation.
        
        Ẋ_aug = A_cl * X_aug + B_ref * P_ref
        """
        # Test state
        X_aug = np.array([1.0, 2.0, 3.0, 100.0, 5.0])  # [i, ω, θm, P, e_int]
        P_ref = 500.0  # Reference pressure
        t = 0.0
        
        # Compute derivative
        dX_aug_dt = self.cl_system.state_derivative(t, X_aug, P_ref)
        
        # Manually compute expected
        X_aug_col = X_aug.reshape(-1, 1)
        P_ref_col = np.array([[P_ref]])
        expected_dX_aug_dt = (self.cl_system.A_cl @ X_aug_col + 
                             self.cl_system.B_ref @ P_ref_col).flatten()
        
        # Compare
        np.testing.assert_array_almost_equal(dX_aug_dt, expected_dX_aug_dt, 
                                            decimal=6)
        
        print("✓ State derivative computation validated")
    
    def test_output_computation(self):
        """
        Test output computation.
        
        Y = C_cl * X_aug (should extract pressure)
        """
        # Test state
        X_aug = np.array([1.0, 2.0, 3.0, 100.0, 5.0])  # [i, ω, θm, P, e_int]
        
        # Compute output
        Y = self.cl_system.output(X_aug)
        
        # Expected: Y = P = 100.0
        expected_Y = X_aug[3]
        
        self.assertAlmostEqual(Y, expected_Y, places=6)
        
        print("✓ Output computation validated")
    
    def test_zero_steady_state_error_structure(self):
        """
        Test structural property for zero steady-state error.
        
        The system has integral action (Type-1 system for pressure tracking).
        This is a structural check, not a simulation.
        
        Structural requirement:
        - Integral state exists (dimension 5)
        - Integral state integrates error: ė_int = P_ref - P
        - Integral state feeds back to control: u includes Ki*e_int
        """
        # Check augmented system has 5 states (includes integral)
        self.assertEqual(self.cl_system.A_cl.shape[0], 5,
                        "System must have integral state for zero SS error")
        
        # Check integral state equation structure
        # Row 4 (index 4) should be: [0, 0, 0, -1, 0] for A_cl
        integral_row = self.cl_system.A_cl[4, :]
        expected_integral_row = np.array([0.0, 0.0, 0.0, -1.0, 0.0])
        np.testing.assert_array_almost_equal(integral_row, expected_integral_row,
                                            decimal=6,
                                            err_msg="Integral state structure incorrect")
        
        # Check integral state has non-zero feedback to plant
        # Column 4 (index 4) of A_cl should have non-zero entry in row 0
        # (integral feeds back through control input to current)
        integral_feedback = self.cl_system.A_cl[0, 4]
        self.assertNotAlmostEqual(integral_feedback, 0.0, places=2,
                                 msg="Integral state must feed back to plant")
        
        print("✓ Zero steady-state error structure validated")
        print(f"  Integral feedback gain: {integral_feedback}")
    
    def test_matrix_numerical_consistency(self):
        """
        Test that closed-loop matrices are numerically consistent.
        
        Recompute key elements and verify they match.
        """
        # Extract plant matrices
        A = self.cl_system.A_plant
        B = self.cl_system.B_plant
        
        # Extract pressure dynamics row
        A_pressure_row = A[3, :]
        B_pressure = B[3, 0]
        
        # Compute PID denominator
        denom = 1.0 + self.cl_system.Kd * B_pressure
        
        # Verify denominator is positive (stability requirement)
        self.assertGreater(denom, 0.0, "PID denominator must be positive")
        
        # Compute expected feedback gains
        K_feedback_expected = np.zeros(4)
        K_feedback_expected[0] = -self.cl_system.Kd * A_pressure_row[0] / denom
        K_feedback_expected[1] = -self.cl_system.Kd * A_pressure_row[1] / denom
        K_feedback_expected[2] = -self.cl_system.Kd * A_pressure_row[2] / denom
        K_feedback_expected[3] = (-self.cl_system.Kp - self.cl_system.Kd * A_pressure_row[3]) / denom
        
        # Compute expected A_cl upper-left block
        A_cl_plant_expected = A + B @ K_feedback_expected.reshape(1, -1)
        
        # Compare with actual
        np.testing.assert_array_almost_equal(
            self.cl_system.A_cl[0:4, 0:4], 
            A_cl_plant_expected,
            decimal=6,
            err_msg="A_cl plant block doesn't match recomputed values"
        )
        
        print("✓ Matrix numerical consistency validated")
        print(f"  PID denominator: {denom}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
