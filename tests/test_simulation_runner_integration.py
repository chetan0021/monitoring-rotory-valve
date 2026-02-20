"""
Integration tests for simulation_runner.py

Tests actual JSON output to stdout and gain updates via stdin.
"""

import subprocess
import json
import time
import sys
import os


def test_json_output_format():
    """Test that simulation_runner outputs valid JSON with correct fields."""
    # Start the simulation process
    proc = subprocess.Popen(
        [sys.executable, 'simulation_runner.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Read first line of output (should be JSON)
        line = proc.stdout.readline()
        
        # Parse JSON
        data = json.loads(line)
        
        # Verify all required fields
        assert "pressure" in data
        assert "valve_angle" in data
        assert "motor_current" in data
        assert "setpoint" in data
        assert "timestamp" in data
        
        # Verify types
        assert isinstance(data["pressure"], (int, float))
        assert isinstance(data["valve_angle"], (int, float))
        assert isinstance(data["motor_current"], (int, float))
        assert isinstance(data["setpoint"], (int, float))
        assert isinstance(data["timestamp"], (int, float))
        
        # Verify setpoint is 500.0 (default)
        assert data["setpoint"] == 500.0
        
        print(f"✓ First JSON output: {data}")
        
    finally:
        # Terminate process
        proc.terminate()
        proc.wait(timeout=2)


def test_gain_update_via_stdin():
    """Test that simulation_runner accepts gain updates via stdin."""
    # Start the simulation process
    proc = subprocess.Popen(
        [sys.executable, 'simulation_runner.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Read first output to ensure process is running
        line1 = proc.stdout.readline()
        data1 = json.loads(line1)
        print(f"✓ Initial output: timestamp={data1['timestamp']:.2f}s")
        
        # Send gain update
        gain_update = {"Kp": 200.0, "Ki": 50.0, "Kd": 75.0}
        proc.stdin.write(json.dumps(gain_update) + '\n')
        proc.stdin.flush()
        print(f"✓ Sent gain update: {gain_update}")
        
        # Read a few more outputs to verify process continues
        for i in range(3):
            line = proc.stdout.readline()
            data = json.loads(line)
            print(f"✓ Output after gain update: timestamp={data['timestamp']:.2f}s")
        
        # If we got here, the process handled the gain update correctly
        print("✓ Process continued after gain update")
        
    finally:
        # Terminate process
        proc.terminate()
        proc.wait(timeout=2)


def test_output_timing():
    """Test that outputs occur at approximately 100ms intervals."""
    # Start the simulation process
    proc = subprocess.Popen(
        [sys.executable, 'simulation_runner.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        timestamps = []
        
        # Read 5 outputs
        for i in range(5):
            line = proc.stdout.readline()
            data = json.loads(line)
            timestamps.append(data['timestamp'])
        
        # Calculate intervals
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        print(f"✓ Timestamps: {timestamps}")
        print(f"✓ Intervals: {intervals}")
        
        # Verify intervals are approximately 0.1s (100ms)
        for interval in intervals:
            assert 0.08 <= interval <= 0.12, f"Interval {interval} not close to 0.1s"
        
        print("✓ Output timing is correct (~100ms intervals)")
        
    finally:
        # Terminate process
        proc.terminate()
        proc.wait(timeout=2)


if __name__ == '__main__':
    print("Running integration tests for simulation_runner.py\n")
    
    print("Test 1: JSON output format")
    test_json_output_format()
    print()
    
    print("Test 2: Gain update via stdin")
    test_gain_update_via_stdin()
    print()
    
    print("Test 3: Output timing")
    test_output_timing()
    print()
    
    print("All integration tests passed! ✓")
