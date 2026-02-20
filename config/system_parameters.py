"""
System Parameters - Centralized Parameter Authority

This module contains ALL physical constants and parameters defined in documentation.
All values are extracted from:
- docs/industrial_pressure_control_system_design.md
- docs/numerical_state_space_and_simulation_specification.md

NO VALUES ARE INVENTED OR ASSUMED.
All derived quantities are computed programmatically using documented formulas.

References are provided inline for each parameter.
"""

import numpy as np


class SystemParameters:
    """
    Centralized repository for all system parameters.
    
    All values are extracted directly from documentation.
    Derived quantities are computed using documented formulas.
    """
    
    def __init__(self):
        """
        Initialize all system parameters from documentation.
        """
        # ===================================================================
        # VALVE PARAMETERS
        # Reference: industrial_pressure_control_system_design.md Section 1.1
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.1
        # ===================================================================
        self.m_valve = 100.0  # Valve mass (kg)
        self.r_valve = 0.35  # Valve radius (m)
        self.tau_friction = 120.0  # Static friction torque (Nm)
        self.g = 9.81  # Gravitational acceleration (m/s²)
        
        # Computed valve parameters
        # Formula: J_valve = (1/2) * m * r^2
        # Reference: industrial_pressure_control_system_design.md Section 1.1
        self.J_valve = 0.5 * self.m_valve * self.r_valve**2  # Expected: 6.125 kg·m²
        
        # Formula: τ_g = m * g * r
        # Reference: industrial_pressure_control_system_design.md Section 1.2
        self.tau_gravity = self.m_valve * self.g * self.r_valve  # Expected: 343.35 Nm
        
        # Formula: τ_load = τ_g + τ_f
        # Reference: industrial_pressure_control_system_design.md Section 1.2
        self.tau_load_total = self.tau_gravity + self.tau_friction  # Expected: 463.35 Nm
        
        # ===================================================================
        # GEARBOX PARAMETERS
        # Reference: industrial_pressure_control_system_design.md Section 1.3
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.1
        # ===================================================================
        self.N = 40  # Gear ratio
        self.eta = 0.85  # Gear efficiency
        
        # ===================================================================
        # MOTOR ELECTRICAL PARAMETERS
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.2
        # ===================================================================
        self.R = 1.2  # Armature resistance (Ω)
        self.L = 0.005  # Armature inductance (H) - 5 mH explicitly modeled
        self.Kt = 0.8  # Torque constant (Nm/A)
        self.Ke = 0.8  # Back EMF constant (V·s/rad) - Note: Ke = Kb in docs
        self.V_supply = 36.0  # Supply voltage (V)
        
        # ===================================================================
        # MOTOR MECHANICAL PARAMETERS
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.1
        # ===================================================================
        self.J_m = 0.02  # Motor inertia (kg·m²)
        
        # Computed inertia parameters
        # Formula: J_ref = J_valve / (η * N^2)
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.1
        self.J_ref = self.J_valve / (self.eta * self.N**2)
        
        # Formula: J_total = J_m + J_ref
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.1
        self.J_total = self.J_m + self.J_ref
        
        # ===================================================================
        # PRESSURE SYSTEM PARAMETERS
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.3
        # ===================================================================
        self.P_min = 250.0  # Minimum pressure (bar)
        self.P_max = 700.0  # Maximum pressure (bar)
        self.P_setpoint = 500.0  # Setpoint pressure (bar)
        
        self.Kp_pressure = 150.0  # Pressure gain (bar/rad) - linearized around operating point
        self.tau_p = 0.5  # Pressure time constant (s)
        
        # ===================================================================
        # SENSOR PARAMETERS
        # Reference: industrial_pressure_control_system_design.md Section 3.1
        # Reference: numerical_state_space_and_simulation_specification.md Section 1.3
        # ===================================================================
        self.Ks = 0.01  # Sensor gain (V/bar) = 1 V / 100 bar
        
        # ===================================================================
        # PID CONTROLLER GAINS (FROZEN - DO NOT MODIFY)
        # Reference: industrial_pressure_control_system_design.md Section 3.6
        # ===================================================================
        self.Kp = 115.2  # Proportional gain
        self.Ki = 34.56  # Integral gain
        self.Kd = 49.92  # Derivative gain
        
    def print_summary(self):
        """
        Print summary of all parameters for verification.
        """
        print("=" * 70)
        print("SYSTEM PARAMETERS SUMMARY")
        print("=" * 70)
        
        print("\n--- VALVE PARAMETERS ---")
        print(f"Mass: {self.m_valve} kg")
        print(f"Radius: {self.r_valve} m")
        print(f"Moment of inertia: {self.J_valve} kg·m²")
        print(f"Gravitational torque: {self.tau_gravity} Nm")
        print(f"Static friction torque: {self.tau_friction} Nm")
        print(f"Total load torque: {self.tau_load_total} Nm")
        
        print("\n--- GEARBOX PARAMETERS ---")
        print(f"Gear ratio: {self.N}")
        print(f"Gear efficiency: {self.eta}")
        
        print("\n--- MOTOR ELECTRICAL PARAMETERS ---")
        print(f"Armature resistance: {self.R} Ω")
        print(f"Armature inductance: {self.L} H ({self.L*1000} mH)")
        print(f"Torque constant: {self.Kt} Nm/A")
        print(f"Back EMF constant: {self.Ke} V·s/rad")
        print(f"Supply voltage: {self.V_supply} V")
        
        print("\n--- MOTOR MECHANICAL PARAMETERS ---")
        print(f"Motor inertia: {self.J_m} kg·m²")
        print(f"Reflected valve inertia: {self.J_ref} kg·m²")
        print(f"Total inertia at motor shaft: {self.J_total} kg·m²")
        
        print("\n--- PRESSURE SYSTEM PARAMETERS ---")
        print(f"Operating range: {self.P_min}-{self.P_max} bar")
        print(f"Setpoint: {self.P_setpoint} bar")
        print(f"Pressure gain: {self.Kp_pressure} bar/rad")
        print(f"Pressure time constant: {self.tau_p} s")
        
        print("\n--- SENSOR PARAMETERS ---")
        print(f"Sensor gain: {self.Ks} V/bar")
        
        print("\n--- PID CONTROLLER GAINS (FROZEN) ---")
        print(f"Kp: {self.Kp}")
        print(f"Ki: {self.Ki}")
        print(f"Kd: {self.Kd}")
        
        print("=" * 70)
    
    def validate_derived_values(self):
        """
        Validate that computed values match documentation.
        
        Expected values from industrial_pressure_control_system_design.md:
        - J_valve = 6.125 kg·m²
        - τ_g = 343.35 Nm
        - τ_load = 463.35 Nm
        """
        print("\n" + "=" * 70)
        print("VALIDATION AGAINST DOCUMENTATION")
        print("=" * 70)
        
        # Expected values from docs
        expected_J_valve = 6.125
        expected_tau_gravity = 343.35
        expected_tau_load = 463.35
        
        # Tolerance for floating point comparison
        tol = 1e-6
        
        # Validate J_valve
        if abs(self.J_valve - expected_J_valve) < tol:
            print(f"✓ J_valve: {self.J_valve} kg·m² (matches documentation)")
        else:
            print(f"✗ J_valve: {self.J_valve} kg·m² (expected {expected_J_valve})")
        
        # Validate tau_gravity
        if abs(self.tau_gravity - expected_tau_gravity) < tol:
            print(f"✓ τ_gravity: {self.tau_gravity} Nm (matches documentation)")
        else:
            print(f"✗ τ_gravity: {self.tau_gravity} Nm (expected {expected_tau_gravity})")
        
        # Validate tau_load_total
        if abs(self.tau_load_total - expected_tau_load) < tol:
            print(f"✓ τ_load_total: {self.tau_load_total} Nm (matches documentation)")
        else:
            print(f"✗ τ_load_total: {self.tau_load_total} Nm (expected {expected_tau_load})")
        
        print("=" * 70)


# Create global instance for easy import
params = SystemParameters()


if __name__ == "__main__":
    # Test parameter loading
    params.print_summary()
    params.validate_derived_values()
