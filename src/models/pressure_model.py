"""
Pressure Dynamics Model Module

Implements first-order pressure process dynamics.
All parameters and equations are defined in:
- docs/industrial_pressure_control_system_design.md (Section 2.5)
- docs/numerical_state_space_and_simulation_specification.md (Section 3)

Physical Parameters (from documentation):
- Operating range: 250–700 bar
- Setpoint: 500 bar
- Sensor gain: Ks = 0.01 V/bar
- Pressure gain: Kp_pressure = 250 bar/rad
- Pressure time constant: τp = 0.8 s

Equation:
- First-order dynamics: τp * (dP/dt) + P = Kp_pressure * θv
- State-space form: dP/dt = (1/τp) * [Kp_pressure * (θm/N) - P]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.system_parameters import params


class PressureModel:
    """
    First-order pressure process model.
    
    References:
    - industrial_pressure_control_system_design.md: Section 2.5
    - numerical_state_space_and_simulation_specification.md: Section 3
    """
    
    def __init__(self):
        """
        Initialize pressure system parameters from centralized parameter authority.
        All values loaded from config.system_parameters.
        """
        # Operating parameters
        self.P_min = params.P_min  # Minimum pressure (bar)
        self.P_max = params.P_max  # Maximum pressure (bar)
        self.P_setpoint = params.P_setpoint  # Setpoint pressure (bar)
        
        # Model parameters
        self.Kp_pressure = params.Kp_pressure  # Pressure gain (bar/rad)
        self.tau_p = params.tau_p  # Pressure time constant (s)
        
        # Sensor parameters
        self.Ks = params.Ks  # Sensor gain (V/bar)
        
        # Gearbox ratio (needed for valve angle conversion)
        self.N = params.N
    
    def pressure_dynamics(self, P, theta_valve):
        """
        Compute dP/dt from first-order pressure equation.
        
        Equation: dP/dt = (1/τp) * [Kp_pressure * θv - P]
        Reference: Section 3 of numerical_state_space_and_simulation_specification.md
        
        Args:
            P: Current pressure (bar)
            theta_valve: Valve angular position (rad)
        
        Returns:
            dP_dt: Rate of change of pressure (bar/s)
        """
        dP_dt = (1.0 / self.tau_p) * (self.Kp_pressure * theta_valve - P)
        return dP_dt
    
    def pressure_dynamics_from_motor_angle(self, P, theta_motor):
        """
        Compute dP/dt using motor angle (converts to valve angle internally).
        
        Equation: dP/dt = (1/τp) * [Kp_pressure * (θm/N) - P]
        Reference: Section 3 of numerical_state_space_and_simulation_specification.md
        
        Args:
            P: Current pressure (bar)
            theta_motor: Motor angular position (rad)
        
        Returns:
            dP_dt: Rate of change of pressure (bar/s)
        """
        theta_valve = theta_motor / self.N
        return self.pressure_dynamics(P, theta_valve)
    
    def sensor_output(self, P):
        """
        Compute sensor voltage output from pressure.
        
        Equation: V_sensor = Ks * P
        Reference: Section 2 of numerical_state_space_and_simulation_specification.md
        
        Args:
            P: Pressure (bar)
        
        Returns:
            V_sensor: Sensor voltage output (V)
        """
        return self.Ks * P
    
    def validate_parameters(self):
        """
        Validate that loaded parameters match documentation values.
        Cross-reference with numerical_state_space_and_simulation_specification.md
        """
        print("\n--- Pressure Model Parameter Validation ---")
        print(f"Operating range: {self.P_min}-{self.P_max} bar")
        print(f"Setpoint: {self.P_setpoint} bar")
        print(f"Kp_pressure = {self.Kp_pressure} bar/rad (expected: 150)")
        print(f"τp = {self.tau_p} s (expected: 0.5)")
        print(f"Ks = {self.Ks} V/bar (expected: 0.01)")
        
        # Check if values match expected
        assert abs(self.Kp_pressure - 150.0) < 1e-6, "Kp_pressure mismatch"
        assert abs(self.tau_p - 0.5) < 1e-6, "tau_p mismatch"
        assert abs(self.Ks - 0.01) < 1e-6, "Ks mismatch"
        
        print("✓ All pressure model parameters validated")


if __name__ == "__main__":
    pressure = PressureModel()
    pressure.validate_parameters()
