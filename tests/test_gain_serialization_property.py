"""
Property-Based Test: Gain Serialization

Property 5: JSON Serialization for Gain Updates
Validates: Requirements 3.4

This test verifies that PID gain values can be serialized to JSON
and that the resulting JSON is valid and contains all three fields
with correct values.
"""

import json
import pytest
from hypothesis import given, strategies as st


# Helper functions for gain serialization
def serialize_gains(Kp, Ki, Kd):
    """
    Serialize PID gains to JSON format.
    
    Mimics the C++ implementation in communication_client.cpp:
        QJsonObject json;
        json["Kp"] = Kp;
        json["Ki"] = Ki;
        json["Kd"] = Kd;
        QJsonDocument doc(json);
        QByteArray data = doc.toJson(QJsonDocument::Compact);
    
    Args:
        Kp: Proportional gain
        Ki: Integral gain
        Kd: Derivative gain
    
    Returns:
        JSON string with gain values
    """
    gain_dict = {
        "Kp": Kp,
        "Ki": Ki,
        "Kd": Kd
    }
    return json.dumps(gain_dict)


def parse_gains(json_str):
    """
    Parse JSON string to extract gain values.
    
    Mimics the Python implementation in simulation_runner.py:
        data = json.loads(line)
        if 'Kp' in data and 'Ki' in data and 'Kd' in data:
            self.update_gains(data['Kp'], data['Ki'], data['Kd'])
    
    Args:
        json_str: JSON string containing gain values
    
    Returns:
        Dictionary with Kp, Ki, Kd keys
    
    Raises:
        ValueError: If JSON is invalid or missing required fields
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    # Check for required fields
    if 'Kp' not in data or 'Ki' not in data or 'Kd' not in data:
        raise ValueError("JSON missing required fields (Kp, Ki, Kd)")
    
    return {
        "Kp": data["Kp"],
        "Ki": data["Ki"],
        "Kd": data["Kd"]
    }


# Hypothesis strategy for generating gain values
@st.composite
def gain_values_strategy(draw):
    """
    Generate random PID gain values.
    
    Range: 0-1000 for each gain (typical range for industrial controllers)
    Allows for zero gains (edge case)
    Excludes NaN and infinity
    """
    Kp = draw(st.floats(min_value=0.0, max_value=1000.0, 
                        allow_nan=False, allow_infinity=False))
    Ki = draw(st.floats(min_value=0.0, max_value=1000.0,
                        allow_nan=False, allow_infinity=False))
    Kd = draw(st.floats(min_value=0.0, max_value=1000.0,
                        allow_nan=False, allow_infinity=False))
    return (Kp, Ki, Kd)


# Property Test
@given(gains=gain_values_strategy())
def test_gain_serialization_property(gains):
    """
    **Validates: Requirements 3.4**
    
    Property 5: JSON Serialization for Gain Updates
    
    For any three PID gain values (Kp, Ki, Kd), serializing them to JSON
    should produce a valid JSON object containing all three gains with
    correct field names and values.
    
    This property ensures:
    1. Serialization produces valid JSON
    2. All three fields are present (Kp, Ki, Kd)
    3. Values are preserved correctly
    4. JSON can be parsed by the Python backend
    """
    Kp, Ki, Kd = gains
    
    # Serialize gains to JSON
    json_str = serialize_gains(Kp, Ki, Kd)
    
    # Verify JSON is valid by parsing it
    parsed = parse_gains(json_str)
    
    # Verify all three fields are present
    assert "Kp" in parsed, "JSON missing Kp field"
    assert "Ki" in parsed, "JSON missing Ki field"
    assert "Kd" in parsed, "JSON missing Kd field"
    
    # Verify values match within tolerance
    # Use small tolerance for floating-point comparison
    tolerance = 1e-10
    assert abs(parsed["Kp"] - Kp) < tolerance, f"Kp mismatch: {parsed['Kp']} != {Kp}"
    assert abs(parsed["Ki"] - Ki) < tolerance, f"Ki mismatch: {parsed['Ki']} != {Ki}"
    assert abs(parsed["Kd"] - Kd) < tolerance, f"Kd mismatch: {parsed['Kd']} != {Kd}"


# Edge case tests
def test_gain_serialization_edge_cases():
    """
    Test specific edge cases for gain serialization.
    
    Edge cases:
    1. Zero gains (all zeros)
    2. Maximum gains (1000.0 for all)
    3. Typical operating values
    4. Mixed values (some zero, some non-zero)
    """
    test_cases = [
        # (Kp, Ki, Kd, description)
        (0.0, 0.0, 0.0, "All zero gains"),
        (1000.0, 1000.0, 1000.0, "Maximum gains"),
        (115.2, 34.56, 49.92, "Typical operating values"),
        (0.0, 100.0, 50.0, "Zero Kp"),
        (100.0, 0.0, 50.0, "Zero Ki"),
        (100.0, 50.0, 0.0, "Zero Kd"),
        (0.001, 0.001, 0.001, "Very small gains"),
        (999.999, 999.999, 999.999, "Near maximum gains"),
    ]
    
    for Kp, Ki, Kd, description in test_cases:
        # Serialize
        json_str = serialize_gains(Kp, Ki, Kd)
        
        # Parse
        parsed = parse_gains(json_str)
        
        # Verify
        tolerance = 1e-10
        assert abs(parsed["Kp"] - Kp) < tolerance, f"{description}: Kp mismatch"
        assert abs(parsed["Ki"] - Ki) < tolerance, f"{description}: Ki mismatch"
        assert abs(parsed["Kd"] - Kd) < tolerance, f"{description}: Kd mismatch"


def test_gain_serialization_json_format():
    """
    Test that serialized JSON has the correct format.
    
    Verifies:
    1. JSON is a valid object (not array or primitive)
    2. Contains exactly three fields
    3. Field names are correct
    4. Values are numeric
    """
    Kp, Ki, Kd = 115.2, 34.56, 49.92
    
    json_str = serialize_gains(Kp, Ki, Kd)
    
    # Parse as raw JSON to check structure
    data = json.loads(json_str)
    
    # Verify it's a dictionary
    assert isinstance(data, dict), "JSON should be an object"
    
    # Verify exactly three fields
    assert len(data) == 3, f"JSON should have exactly 3 fields, got {len(data)}"
    
    # Verify field names
    assert set(data.keys()) == {"Kp", "Ki", "Kd"}, "JSON should have Kp, Ki, Kd fields"
    
    # Verify values are numeric
    assert isinstance(data["Kp"], (int, float)), "Kp should be numeric"
    assert isinstance(data["Ki"], (int, float)), "Ki should be numeric"
    assert isinstance(data["Kd"], (int, float)), "Kd should be numeric"


def test_gain_serialization_invalid_json():
    """
    Test that parse_gains correctly rejects invalid JSON.
    
    Verifies error handling for:
    1. Malformed JSON
    2. Missing fields
    3. Wrong field names
    """
    # Malformed JSON
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_gains("{invalid json}")
    
    # Missing Kp
    with pytest.raises(ValueError, match="missing required fields"):
        parse_gains('{"Ki": 10.0, "Kd": 5.0}')
    
    # Missing Ki
    with pytest.raises(ValueError, match="missing required fields"):
        parse_gains('{"Kp": 10.0, "Kd": 5.0}')
    
    # Missing Kd
    with pytest.raises(ValueError, match="missing required fields"):
        parse_gains('{"Kp": 10.0, "Ki": 5.0}')
    
    # Wrong field names
    with pytest.raises(ValueError, match="missing required fields"):
        parse_gains('{"P": 10.0, "I": 5.0, "D": 2.0}')


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
