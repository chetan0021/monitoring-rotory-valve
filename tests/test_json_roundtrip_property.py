"""
Property-Based Test for JSON Round-Trip

Tests Property 4: JSON Round-Trip for Data Points
Validates: Requirements 3.1, 3.2

This test verifies that data points can be serialized to JSON and parsed back
with all fields preserved within acceptable tolerance.
"""

import json
import pytest
from hypothesis import given, strategies as st


# Strategy for generating valid data points
@st.composite
def data_point_strategy(draw):
    """Generate random data points with valid ranges."""
    return {
        "pressure": draw(st.floats(min_value=0.0, max_value=700.0, allow_nan=False, allow_infinity=False)),
        "valve_angle": draw(st.floats(min_value=0.0, max_value=180.0, allow_nan=False, allow_infinity=False)),
        "motor_current": draw(st.floats(min_value=0.0, max_value=25.0, allow_nan=False, allow_infinity=False)),
        "setpoint": 500.0,  # Constant as per spec
        "timestamp": draw(st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    }


def serialize_data_point(data):
    """Serialize data point to JSON string (simulates Python backend output)."""
    return json.dumps(data)


def parse_data_point(json_str):
    """Parse JSON string to data point (simulates Qt GUI parsing)."""
    return json.loads(json_str)


@given(data_point=data_point_strategy())
def test_json_roundtrip_property(data_point):
    """
    **Validates: Requirements 3.1, 3.2**
    
    Property 4: JSON Round-Trip for Data Points
    
    For any valid simulation state (pressure, valve_angle, motor_current, 
    setpoint, timestamp), serializing to JSON and then parsing should recover 
    all five fields with their original values.
    """
    # Serialize to JSON
    json_str = serialize_data_point(data_point)
    
    # Verify it's valid JSON
    assert isinstance(json_str, str)
    assert len(json_str) > 0
    
    # Parse back
    parsed = parse_data_point(json_str)
    
    # Verify all five fields are present
    assert "pressure" in parsed
    assert "valve_angle" in parsed
    assert "motor_current" in parsed
    assert "setpoint" in parsed
    assert "timestamp" in parsed
    
    # Verify values match within tolerance (0.001)
    tolerance = 0.001
    assert abs(parsed["pressure"] - data_point["pressure"]) < tolerance
    assert abs(parsed["valve_angle"] - data_point["valve_angle"]) < tolerance
    assert abs(parsed["motor_current"] - data_point["motor_current"]) < tolerance
    assert abs(parsed["setpoint"] - data_point["setpoint"]) < tolerance
    assert abs(parsed["timestamp"] - data_point["timestamp"]) < tolerance


def test_json_roundtrip_edge_cases():
    """Test specific edge cases for JSON round-trip."""
    # Test with zero values
    data = {
        "pressure": 0.0,
        "valve_angle": 0.0,
        "motor_current": 0.0,
        "setpoint": 500.0,
        "timestamp": 0.0
    }
    json_str = serialize_data_point(data)
    parsed = parse_data_point(json_str)
    assert parsed == data
    
    # Test with maximum values
    data = {
        "pressure": 700.0,
        "valve_angle": 180.0,
        "motor_current": 25.0,
        "setpoint": 500.0,
        "timestamp": 1000.0
    }
    json_str = serialize_data_point(data)
    parsed = parse_data_point(json_str)
    assert parsed == data
    
    # Test with typical operating values
    data = {
        "pressure": 500.0,
        "valve_angle": 90.0,
        "motor_current": 12.5,
        "setpoint": 500.0,
        "timestamp": 15.5
    }
    json_str = serialize_data_point(data)
    parsed = parse_data_point(json_str)
    assert parsed == data


if __name__ == "__main__":
    # Run the property test manually
    test_json_roundtrip_property()
    test_json_roundtrip_edge_cases()
    print("All JSON round-trip tests passed!")
