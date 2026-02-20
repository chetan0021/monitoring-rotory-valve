"""
Motor Model Module

Implements the electrical and mechanical dynamics of the DC motor.
All parameters and equations are defined in:
- docs/industrial_pressure_control_system_design.md (Section 2.1, 2.2)
- docs/numerical_state_space_and_simulation_specification.md (Section 3)

Physical Parameters (from documentation):
- Armature resistance R = 1.2 Ω
- Armature inductance L = 0.02 H
- Torque constant Kt = 0.8 Nm/A
- Back EMF constant Ke = 0.8 V·s/rad
- Motor inertia Jm = 0.002 kg·m²
- Supply voltage = 36 V

State Variables:
- Armature current i (A)
- Motor angular velocity ω (rad/s)
- Motor angular position θm (rad)

Equations:
- Electrical: di/dt = (1/L)[V - R*i - Ke*ω]
- Mechanical: dω/dt = (1/J_total)[Kt*i - T_load]
- Position: dθm/dt = ω
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.system_parameters import params


class MotorModel:
    """
    DC Motor electrical and mechanical model.
    
    References:
    - industrial_pressure_control_system_design.md: Section 2.1, 2.2
    - numerical_state_space_and_simulation_specification.md: Section 3
    """
    
    def __init__(self):
        """
        Initialize motor parameters from centralized parameter authority.
        All values loaded from config.system_parameters.
        """
        # Electrical parameters
        self.R = params.R  # Armature resistance (Ω)
        self.L = params.L  # Armature inductance (H)
        self.Kt = params.Kt  # Torque constant (Nm/A)
        self.Ke = params.Ke  # Back EMF constant (V·s/rad)
        
        # Mechanical parameters
        self.Jm = params.J_m  # Motor inertia (kg·m²)
        
        # Supply
        self.V_supply = params.V_supply  # Supply voltage (V)
    
    def electrical_dynamics(self, i, omega, V):
        """
        Compute di/dt from electrical equation.
        
        Equation: di/dt = (1/L)[V - R*i - Ke*ω]
        Reference: Section 3 of numerical_state_space_and_simulation_specification.md
        
        Args:
            i: Armature current (A)
            omega: Motor angular velocity (rad/s)
            V: Applied voltage (V)
        
        Returns:
            di_dt: Rate of change of current (A/s)
        """
        di_dt = (1.0 / self.L) * (V - self.R * i - self.Ke * omega)
        return di_dt
    
    def mechanical_dynamics(self, i, T_load, J_total):
        """
        Compute dω/dt from mechanical equation.
        
        Equation: dω/dt = (1/J_total)[Kt*i - T_load]
        Reference: Section 3 of numerical_state_space_and_simulation_specification.md
        
        Args:
            i: Armature current (A)
            T_load: Load torque reflected to motor shaft (Nm)
            J_total: Total inertia at motor shaft (kg·m²)
        
        Returns:
            domega_dt: Angular acceleration (rad/s²)
        """
        domega_dt = (1.0 / J_total) * (self.Kt * i - T_load)
        return domega_dt
    
    def validate_parameters(self):
        """
        Validate that loaded parameters match documentation values.
        Cross-reference with numerical_state_space_and_simulation_specification.md
        """
        print("\n--- Motor Model Parameter Validation ---")
        print(f"R = {self.R} Ω (expected: 1.2)")
        print(f"L = {self.L} H (expected: 0.005)")
        print(f"Kt = {self.Kt} Nm/A (expected: 0.8)")
        print(f"Ke = {self.Ke} V·s/rad (expected: 0.8)")
        print(f"Jm = {self.Jm} kg·m² (expected: 0.02)")
        
        # Check if values match expected
        assert abs(self.R - 1.2) < 1e-6, "R mismatch"
        assert abs(self.L - 0.005) < 1e-6, "L mismatch"
        assert abs(self.Kt - 0.8) < 1e-6, "Kt mismatch"
        assert abs(self.Ke - 0.8) < 1e-6, "Ke mismatch"
        assert abs(self.Jm - 0.02) < 1e-6, "Jm mismatch"
        
        print("✓ All motor parameters validated")


if __name__ == "__main__":
    motor = MotorModel()
    motor.validate_parameters()
