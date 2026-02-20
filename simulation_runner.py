"""
Simulation Runner - Python stdout bridge for Qt GUI

Runs closed-loop pressure control simulation and outputs JSON to stdout.
Qt GUI reads this output via QProcess and updates plots in real-time.

Communication Protocol:
- Output: JSON lines to stdout (one per 100ms)
- Input: JSON lines from stdin for gain updates
"""

import sys
import os
import json
import time
import argparse
import select
import numpy as np
from scipy.integrate import odeint

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.system_parameters import params
from models.full_state_space_model import FullStateSpaceModel


class SimulationRunner:
    """Real-time closed-loop simulation with stdout communication."""
    
    def __init__(self, setpoint=500.0):
        """Initialize simulation with setpoint."""
        self.setpoint = setpoint
        
        # Load plant model
        self.plant = FullStateSpaceModel()
        A = self.plant.A  # 4x4
        B = self.plant.B  # 4x1
        C = self.plant.C  # 1x4
        
        # PID gains (can be updated via stdin)
        self.Kp = params.Kp
        self.Ki = params.Ki
        self.Kd = params.Kd
        
        # Build closed-loop system (5 states: [i, ω, θ, P, x_int])
        self.A = A
        self.B = B
        self.C = C
        self.rebuild_closed_loop()
        
        # Initial state: [i_a, ω_m, θ_m, P, x_int] all zero
        self.state = np.zeros(5)
        
        # Simulation time
        self.t = 0.0
        self.dt = 0.01  # 10ms integration step
        self.output_interval = 0.1  # 100ms output interval
        self.last_output_time = 0.0
    
    def rebuild_closed_loop(self):
        """Rebuild closed-loop A matrix with current PID gains."""
        A = self.A
        B = self.B
        C = self.C
        
        # Compute feedback gains
        CxB = (C @ B)[0, 0]
        denom = 1.0 + self.Kd * CxB
        
        K_state = -(self.Kp * C + self.Kd * C @ A) / denom  # 1x4
        K_int = self.Ki / denom
        K_ref = self.Kp / denom
        
        # Build 5x5 closed-loop A matrix
        self.A_cl = np.zeros((5, 5))
        self.A_cl[0:4, 0:4] = A + B @ K_state
        self.A_cl[0:4, 4] = (B * K_int).flatten()
        self.A_cl[4, 0:4] = -C.flatten()
        self.A_cl[4, 4] = 0.0
        
        # Build 5x1 reference input matrix
        self.B_ref = np.zeros(5)
        self.B_ref[0:4] = (B * K_ref).flatten()
        self.B_ref[4] = 1.0
    
    def dynamics(self, state, t):
        """
        Closed-loop dynamics for integration.
        
        state: [i_a, ω_m, θ_m, P, x_int]
        returns: state_dot
        """
        state_dot = self.A_cl @ state + self.B_ref * self.setpoint
        return state_dot
    
    def step(self):
        """Advance simulation by dt using odeint."""
        t_span = [self.t, self.t + self.dt]
        result = odeint(self.dynamics, self.state, t_span)
        self.state = result[-1]
        
        # Apply state saturation to prevent numerical instability
        self.state[0] = np.clip(self.state[0], -25, 25)  # Current: -25 to 25 A
        self.state[2] = np.clip(self.state[2], -100, 100)  # Motor angle: reasonable range
        self.state[3] = np.clip(self.state[3], 0, 700)  # Pressure: 0-700 bar
        
        self.t += self.dt
    
    def get_output_data(self):
        """
        Extract current simulation data for JSON output.
        
        Returns dict with:
        - pressure: current pressure (bar)
        - valve_angle: valve angle (degrees)
        - motor_current: motor current (A)
        - setpoint: pressure setpoint (bar)
        - timestamp: simulation time (s)
        """
        # Extract states
        i_a = self.state[0]      # Armature current (A)
        omega_m = self.state[1]  # Motor velocity (rad/s)
        theta_m = self.state[2]  # Motor position (rad)
        P = self.state[3]        # Pressure (bar)
        
        # Convert motor position to valve angle
        # Valve angle = motor angle / gear ratio
        theta_valve = theta_m / params.N  # rad
        valve_angle_deg = np.degrees(theta_valve)
        
        # Apply saturation limits to prevent display issues
        P = np.clip(P, 0, 700)  # Pressure: 0-700 bar
        valve_angle_deg = np.clip(valve_angle_deg, 0, 180)  # Valve: 0-180 degrees
        i_a = np.clip(i_a, 0, 25)  # Current: 0-25 A
        
        return {
            "pressure": float(P),
            "valve_angle": float(valve_angle_deg),
            "motor_current": float(i_a),
            "setpoint": float(self.setpoint),
            "timestamp": float(self.t)
        }
    
    def update_gains(self, Kp, Ki, Kd):
        """Update PID gains and rebuild closed-loop system."""
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.rebuild_closed_loop()
    
    def check_stdin(self):
        """Check for gain updates from stdin (non-blocking)."""
        # Check if stdin has data available (non-blocking)
        if sys.platform == 'win32':
            # Windows doesn't support select on stdin
            # Use a simple try-except approach
            import msvcrt
            if msvcrt.kbhit():
                line = sys.stdin.readline().strip()
                if line:
                    try:
                        data = json.loads(line)
                        if 'Kp' in data and 'Ki' in data and 'Kd' in data:
                            self.update_gains(data['Kp'], data['Ki'], data['Kd'])
                    except json.JSONDecodeError:
                        pass
        else:
            # Unix-like systems
            if select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline().strip()
                if line:
                    try:
                        data = json.loads(line)
                        if 'Kp' in data and 'Ki' in data and 'Kd' in data:
                            self.update_gains(data['Kp'], data['Ki'], data['Kd'])
                    except json.JSONDecodeError:
                        pass
    
    def run(self):
        """Main simulation loop - outputs JSON to stdout every 100ms."""
        while True:
            # Step simulation forward
            self.step()
            
            # Check for gain updates from stdin
            self.check_stdin()
            
            # Output data every 100ms
            if self.t - self.last_output_time >= self.output_interval:
                data = self.get_output_data()
                # CRITICAL: flush=True ensures Qt receives data immediately
                print(json.dumps(data), flush=True)
                self.last_output_time = self.t
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.001)


def main():
    """Entry point for simulation runner."""
    parser = argparse.ArgumentParser(description='Pressure Control Simulation Runner')
    parser.add_argument('--setpoint', type=float, default=500.0,
                        help='Pressure setpoint in bar (default: 500.0)')
    args = parser.parse_args()
    
    # Create and run simulation
    sim = SimulationRunner(setpoint=args.setpoint)
    
    try:
        sim.run()
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass


if __name__ == '__main__':
    main()
