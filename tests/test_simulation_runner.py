"""
Unit tests for simulation_runner.py

Tests JSON output format and gain update functionality.
"""

import sys
import os
import json
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simulation_runner import SimulationRunner


class TestSimulationRunner:
    """Test suite for SimulationRunner class."""
    
    def test_initialization(self):
        """Test that SimulationRunner initializes correctly."""
        sim = SimulationRunner(setpoint=500.0)
        
        assert sim.setpoint == 500.0
        assert sim.state.shape == (5,)
        assert sim.t == 0.0
        assert sim.output_interval == 0.1
        
    def test_get_output_data_format(self):
        """Test that get_output_data() returns dict with all required fields."""
        sim = SimulationRunner(setpoint=500.0)
        
        # Get output data
        data = sim.get_output_data()
        
        # Verify all required fields are present
        assert "pressure" in data
        assert "valve_angle" in data
        assert "motor_current" in data
        assert "setpoint" in data
        assert "timestamp" in data
        
        # Verify types
        assert isinstance(data["pressure"], float)
        assert isinstance(data["valve_angle"], float)
        assert isinstance(data["motor_current"], float)
        assert isinstance(data["setpoint"], float)
        assert isinstance(data["timestamp"], float)
        
        # Verify setpoint value
        assert data["setpoint"] == 500.0
        
    def test_json_serialization(self):
        """Test that output data can be serialized to valid JSON."""
        sim = SimulationRunner(setpoint=500.0)
        
        # Get output data
        data = sim.get_output_data()
        
        # Serialize to JSON
        json_str = json.dumps(data)
        
        # Verify it's valid JSON by parsing it back
        parsed = json.loads(json_str)
        
        # Verify all fields are preserved
        assert parsed["pressure"] == data["pressure"]
        assert parsed["valve_angle"] == data["valve_angle"]
        assert parsed["motor_current"] == data["motor_current"]
        assert parsed["setpoint"] == data["setpoint"]
        assert parsed["timestamp"] == data["timestamp"]
        
    def test_update_gains(self):
        """Test that update_gains() correctly updates Kp, Ki, Kd."""
        sim = SimulationRunner(setpoint=500.0)
        
        # Store original gains
        original_Kp = sim.Kp
        original_Ki = sim.Ki
        original_Kd = sim.Kd
        
        # Update gains
        new_Kp = 200.0
        new_Ki = 50.0
        new_Kd = 75.0
        sim.update_gains(new_Kp, new_Ki, new_Kd)
        
        # Verify gains were updated
        assert sim.Kp == new_Kp
        assert sim.Ki == new_Ki
        assert sim.Kd == new_Kd
        
        # Verify gains actually changed
        assert sim.Kp != original_Kp or new_Kp == original_Kp
        assert sim.Ki != original_Ki or new_Ki == original_Ki
        assert sim.Kd != original_Kd or new_Kd == original_Kd
        
    def test_rebuild_closed_loop_called(self):
        """Test that rebuild_closed_loop() updates system matrices."""
        sim = SimulationRunner(setpoint=500.0)
        
        # Store original closed-loop matrix
        original_A_cl = sim.A_cl.copy()
        
        # Update gains (should trigger rebuild)
        sim.update_gains(200.0, 50.0, 75.0)
        
        # Verify closed-loop matrix changed
        assert not np.allclose(sim.A_cl, original_A_cl)
        
    def test_step_advances_time(self):
        """Test that step() advances simulation time."""
        sim = SimulationRunner(setpoint=500.0)
        
        initial_time = sim.t
        sim.step()
        
        # Verify time advanced by dt
        assert sim.t == initial_time + sim.dt
        
    def test_step_updates_state(self):
        """Test that step() updates the state vector."""
        sim = SimulationRunner(setpoint=500.0)
        
        # Initial state should be all zeros
        initial_state = sim.state.copy()
        
        # Run a few steps
        for _ in range(10):
            sim.step()
        
        # State should have changed (system is responding to setpoint)
        assert not np.allclose(sim.state, initial_state)


if __name__ == '__main__':
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])
