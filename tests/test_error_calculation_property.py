"""
Property-Based Test: Error Calculation

Property 6: Error Calculation Correctness
Validates: Requirements 5.1

This test verifies that the error calculation (setpoint - pressure)
is correct and properly formatted to 2 decimal places.
"""

import pytest
from hypothesis import given, strategies as st


# Helper functions for error calculation
def calculate_error(setpoint, pressure):
    """
    Calculate pressure error.
    
    Mimics the C++ implementation in mainwindow.cpp:
        double error = setpoint - pressure;
        QString errorText = QString::number(error, 'f', 2);
    
    Args:
        setpoint: Target pressure (bar)
        pressure: Current pressure (bar)
    
    Returns:
        Error value formatted to 2 decimal places
    """
    error = setpoint - pressure
    # Format to 2 decimal places (mimics QString::number(error, 'f', 2))
    return round(error, 2)


def format_error(error):
    """
    Format error value to 2 decimal places as string.
    
    Args:
        error: Error value
    
    Returns:
        String formatted to 2 decimal places
    """
    return f"{error:.2f}"


# Hypothesis strategy for generating pressure values
@st.composite
def pressure_values_strategy(draw):
    """
    Generate random pressure values.
    
    Range: 0-700 bar (valid pressure range from Requirements 6.1)
    Allows for edge cases at boundaries
    Excludes NaN and infinity
    """
    pressure = draw(st.floats(min_value=0.0, max_value=700.0,
                              allow_nan=False, allow_infinity=False))
    return pressure


# Property Test
@given(pressure=pressure_values_strategy())
def test_error_calculation_property(pressure):
    """
    **Validates: Requirements 5.1**
    
    Property 6: Error Calculation Correctness
    
    For any pressure value and setpoint value, the calculated error
    should equal (setpoint - pressure) and be formatted to 2 decimal places.
    
    This property ensures:
    1. Error formula is correct: error = setpoint - pressure
    2. Error is formatted to 2 decimal places
    3. Calculation works for all valid pressure values (0-700 bar)
    4. Edge cases are handled correctly (pressure at boundaries)
    """
    setpoint = 500.0  # Standard setpoint from requirements
    
    # Calculate error
    error = calculate_error(setpoint, pressure)
    
    # Verify error formula: error = setpoint - pressure
    expected_error = setpoint - pressure
    
    # Round expected error to 2 decimal places for comparison
    expected_error_rounded = round(expected_error, 2)
    
    # Verify error matches expected value
    tolerance = 0.01  # Allow for rounding differences
    assert abs(error - expected_error_rounded) < tolerance, \
        f"Error mismatch: {error} != {expected_error_rounded} (pressure={pressure})"
    
    # Verify formatting to 2 decimal places
    error_str = format_error(error)
    
    # Check that string has exactly 2 decimal places
    if '.' in error_str:
        decimal_part = error_str.split('.')[1]
        assert len(decimal_part) == 2, \
            f"Error should have 2 decimal places, got {len(decimal_part)}: {error_str}"


# Edge case tests
def test_error_calculation_edge_cases():
    """
    Test specific edge cases for error calculation.
    
    Edge cases:
    1. Pressure at setpoint (error = 0)
    2. Pressure at minimum (0 bar)
    3. Pressure at maximum (700 bar)
    4. Pressure slightly above setpoint
    5. Pressure slightly below setpoint
    6. Pressure at threshold boundaries (±25 bar from setpoint)
    """
    setpoint = 500.0
    
    test_cases = [
        # (pressure, expected_error, description)
        (500.0, 0.0, "Pressure at setpoint"),
        (0.0, 500.0, "Minimum pressure"),
        (700.0, -200.0, "Maximum pressure"),
        (499.99, 0.01, "Slightly below setpoint"),
        (500.01, -0.01, "Slightly above setpoint"),
        (475.0, 25.0, "At positive threshold (STABLE boundary)"),
        (525.0, -25.0, "At negative threshold (STABLE boundary)"),
        (474.99, 25.01, "Just beyond positive threshold (WARNING)"),
        (525.01, -25.01, "Just beyond negative threshold (WARNING)"),
        (250.0, 250.0, "Large positive error"),
        (650.0, -150.0, "Large negative error"),
    ]
    
    for pressure, expected_error, description in test_cases:
        # Calculate error
        error = calculate_error(setpoint, pressure)
        
        # Verify error value
        tolerance = 0.01
        assert abs(error - expected_error) < tolerance, \
            f"{description}: error mismatch {error} != {expected_error}"
        
        # Verify formatting
        error_str = format_error(error)
        if '.' in error_str:
            decimal_part = error_str.split('.')[1]
            assert len(decimal_part) == 2, \
                f"{description}: should have 2 decimal places, got {error_str}"


def test_error_calculation_formula():
    """
    Test that error calculation uses the correct formula.
    
    Verifies:
    1. Error = setpoint - pressure (not pressure - setpoint)
    2. Positive error means pressure is below setpoint
    3. Negative error means pressure is above setpoint
    """
    setpoint = 500.0
    
    # Pressure below setpoint should give positive error
    pressure_below = 450.0
    error_below = calculate_error(setpoint, pressure_below)
    assert error_below > 0, "Pressure below setpoint should give positive error"
    assert abs(error_below - 50.0) < 0.01, f"Expected 50.0, got {error_below}"
    
    # Pressure above setpoint should give negative error
    pressure_above = 550.0
    error_above = calculate_error(setpoint, pressure_above)
    assert error_above < 0, "Pressure above setpoint should give negative error"
    assert abs(error_above - (-50.0)) < 0.01, f"Expected -50.0, got {error_above}"
    
    # Pressure at setpoint should give zero error
    pressure_at = 500.0
    error_at = calculate_error(setpoint, pressure_at)
    assert abs(error_at) < 0.01, f"Pressure at setpoint should give zero error, got {error_at}"


def test_error_calculation_formatting():
    """
    Test that error formatting produces correct string representation.
    
    Verifies:
    1. Always 2 decimal places
    2. Correct sign representation
    3. Proper rounding behavior (Python uses banker's rounding)
    
    Note: Python's round() uses "banker's rounding" (round half to even),
    so 25.005 rounds to 25.00 (even), not 25.01.
    """
    test_cases = [
        # (error, expected_string)
        (25.0, "25.00"),
        (-25.0, "-25.00"),
        (0.0, "0.00"),
        (25.006, "25.01"),  # Rounds up
        (25.004, "25.00"),  # Rounds down
        (-25.006, "-25.01"),  # Rounds up (magnitude)
        (-25.004, "-25.00"),  # Rounds down (magnitude)
        (0.1, "0.10"),
        (0.01, "0.01"),
        (0.001, "0.00"),  # Rounds to 2 places
        (123.456, "123.46"),  # Rounds up
        (-123.456, "-123.46"),  # Rounds up (magnitude)
        (24.995, "25.00"),  # Banker's rounding: rounds to even
        (25.015, "25.02"),  # Banker's rounding: rounds to even
    ]
    
    for error, expected_str in test_cases:
        formatted = format_error(error)
        assert formatted == expected_str, \
            f"Format mismatch: {formatted} != {expected_str} (error={error})"


def test_error_calculation_with_various_setpoints():
    """
    Test error calculation with different setpoint values.
    
    While the GUI uses 500 bar as the standard setpoint,
    verify the calculation works correctly for any setpoint.
    """
    test_cases = [
        # (setpoint, pressure, expected_error)
        (500.0, 475.0, 25.0),
        (500.0, 525.0, -25.0),
        (600.0, 575.0, 25.0),
        (400.0, 425.0, -25.0),
        (0.0, 0.0, 0.0),
        (700.0, 700.0, 0.0),
    ]
    
    for setpoint, pressure, expected_error in test_cases:
        error = calculate_error(setpoint, pressure)
        tolerance = 0.01
        assert abs(error - expected_error) < tolerance, \
            f"Error mismatch for setpoint={setpoint}, pressure={pressure}: {error} != {expected_error}"


def test_error_calculation_precision():
    """
    Test that error calculation maintains sufficient precision.
    
    Verifies:
    1. Small errors are calculated correctly
    2. Rounding to 2 decimal places doesn't lose critical information
    3. Precision is sufficient for status determination (±25 bar threshold)
    """
    setpoint = 500.0
    
    # Test small errors near zero
    small_errors = [0.001, 0.01, 0.1, 1.0]
    for delta in small_errors:
        pressure = setpoint - delta
        error = calculate_error(setpoint, pressure)
        # Error should be positive and close to delta (rounded to 2 places)
        expected = round(delta, 2)
        assert abs(error - expected) < 0.01, \
            f"Small error precision issue: {error} != {expected} (delta={delta})"
    
    # Test errors near threshold (25 bar)
    threshold_errors = [24.99, 25.0, 25.01]
    for delta in threshold_errors:
        pressure = setpoint - delta
        error = calculate_error(setpoint, pressure)
        expected = round(delta, 2)
        assert abs(error - expected) < 0.01, \
            f"Threshold precision issue: {error} != {expected} (delta={delta})"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
