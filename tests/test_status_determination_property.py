"""
Property-Based Test: Status Determination

Property 7: Status Determination Based on Error Threshold
Validates: Requirements 5.2, 5.3

This test verifies that the status determination logic correctly
classifies errors as STABLE or WARNING based on the ±25 bar threshold.
"""

import pytest
from hypothesis import given, strategies as st


# Constants
ERROR_THRESHOLD = 25.0  # bar


# Helper functions for status determination
def determine_status(error):
    """
    Determine system status based on pressure error.
    
    Mimics the C++ implementation in mainwindow.cpp:
        if (abs(error) <= 25.0) {
            status = "STABLE" (green)
        } else {
            status = "WARNING" (red)
        }
    
    Args:
        error: Pressure error (setpoint - pressure) in bar
    
    Returns:
        Tuple of (status_text, status_color)
        - status_text: "STABLE" or "WARNING"
        - status_color: "green" or "red"
    """
    abs_error = abs(error)
    
    if abs_error <= ERROR_THRESHOLD:
        return ("STABLE", "green")
    else:
        return ("WARNING", "red")


# Hypothesis strategy for generating error values
@st.composite
def error_values_strategy(draw):
    """
    Generate random error values.
    
    Range: -100 to 100 bar (reasonable error range)
    Allows for edge cases at boundaries
    Excludes NaN and infinity
    """
    error = draw(st.floats(min_value=-100.0, max_value=100.0,
                           allow_nan=False, allow_infinity=False))
    return error


# Property Test
@given(error=error_values_strategy())
def test_status_determination_property(error):
    """
    **Validates: Requirements 5.2, 5.3**
    
    Property 7: Status Determination Based on Error Threshold
    
    For any pressure error value, the status should be "STABLE" (green)
    when the absolute error is ≤ 25 bar, and "WARNING" (red) when the
    absolute error > 25 bar.
    
    This property ensures:
    1. Status is STABLE when |error| ≤ 25 bar
    2. Status is WARNING when |error| > 25 bar
    3. Color is green for STABLE, red for WARNING
    4. Threshold is applied symmetrically (positive and negative errors)
    """
    # Determine status
    status_text, status_color = determine_status(error)
    
    # Calculate absolute error
    abs_error = abs(error)
    
    # Verify status determination logic
    if abs_error <= ERROR_THRESHOLD:
        assert status_text == "STABLE", \
            f"Error {error} (|{abs_error}|) should be STABLE, got {status_text}"
        assert status_color == "green", \
            f"STABLE status should be green, got {status_color}"
    else:
        assert status_text == "WARNING", \
            f"Error {error} (|{abs_error}|) should be WARNING, got {status_text}"
        assert status_color == "red", \
            f"WARNING status should be red, got {status_color}"


# Edge case tests
def test_status_determination_boundary_cases():
    """
    Test specific boundary cases for status determination.
    
    Critical boundary cases:
    1. Exactly at threshold (25.0)
    2. Just below threshold (24.99)
    3. Just above threshold (25.01)
    4. Negative threshold values (-25.0, -24.99, -25.01)
    5. Zero error
    """
    test_cases = [
        # (error, expected_status, expected_color, description)
        (0.0, "STABLE", "green", "Zero error"),
        (25.0, "STABLE", "green", "Exactly at positive threshold"),
        (-25.0, "STABLE", "green", "Exactly at negative threshold"),
        (24.99, "STABLE", "green", "Just below positive threshold"),
        (-24.99, "STABLE", "green", "Just below negative threshold (magnitude)"),
        (25.01, "WARNING", "red", "Just above positive threshold"),
        (-25.01, "WARNING", "red", "Just above negative threshold (magnitude)"),
        (0.01, "STABLE", "green", "Very small positive error"),
        (-0.01, "STABLE", "green", "Very small negative error"),
        (50.0, "WARNING", "red", "Large positive error"),
        (-50.0, "WARNING", "red", "Large negative error"),
        (100.0, "WARNING", "red", "Maximum positive error"),
        (-100.0, "WARNING", "red", "Maximum negative error"),
    ]
    
    for error, expected_status, expected_color, description in test_cases:
        status_text, status_color = determine_status(error)
        
        assert status_text == expected_status, \
            f"{description}: expected {expected_status}, got {status_text} (error={error})"
        assert status_color == expected_color, \
            f"{description}: expected {expected_color}, got {status_color} (error={error})"


def test_status_determination_symmetry():
    """
    Test that status determination is symmetric for positive and negative errors.
    
    Verifies:
    1. Same magnitude errors give same status regardless of sign
    2. Threshold applies equally to positive and negative errors
    """
    test_errors = [0.0, 10.0, 20.0, 25.0, 30.0, 50.0, 75.0, 100.0]
    
    for error_magnitude in test_errors:
        # Test positive error
        status_pos, color_pos = determine_status(error_magnitude)
        
        # Test negative error
        status_neg, color_neg = determine_status(-error_magnitude)
        
        # Verify symmetry
        assert status_pos == status_neg, \
            f"Status should be symmetric: +{error_magnitude} gave {status_pos}, -{error_magnitude} gave {status_neg}"
        assert color_pos == color_neg, \
            f"Color should be symmetric: +{error_magnitude} gave {color_pos}, -{error_magnitude} gave {color_neg}"


def test_status_determination_threshold_precision():
    """
    Test status determination with high precision near threshold.
    
    Verifies:
    1. Threshold is exactly 25.0 bar
    2. Values very close to threshold are classified correctly
    3. Floating point precision doesn't cause incorrect classification
    """
    # Test values very close to threshold
    test_cases = [
        (24.999, "STABLE"),
        (25.000, "STABLE"),
        (25.001, "WARNING"),
        (25.0001, "WARNING"),
        (24.9999, "STABLE"),
        (-24.999, "STABLE"),
        (-25.000, "STABLE"),
        (-25.001, "WARNING"),
        (-25.0001, "WARNING"),
        (-24.9999, "STABLE"),
    ]
    
    for error, expected_status in test_cases:
        status_text, _ = determine_status(error)
        assert status_text == expected_status, \
            f"Error {error} should be {expected_status}, got {status_text}"


def test_status_determination_with_calculated_errors():
    """
    Test status determination with errors calculated from pressure values.
    
    This simulates the real workflow:
    1. Calculate error from setpoint and pressure
    2. Determine status from error
    
    Verifies the complete pipeline works correctly.
    """
    setpoint = 500.0
    
    test_cases = [
        # (pressure, expected_status, description)
        (500.0, "STABLE", "At setpoint"),
        (475.0, "STABLE", "25 bar below setpoint (boundary)"),
        (525.0, "STABLE", "25 bar above setpoint (boundary)"),
        (474.99, "WARNING", "Just beyond lower boundary"),
        (525.01, "WARNING", "Just beyond upper boundary"),
        (450.0, "WARNING", "50 bar below setpoint"),
        (550.0, "WARNING", "50 bar above setpoint"),
        (250.0, "WARNING", "250 bar below setpoint"),
        (650.0, "WARNING", "150 bar above setpoint"),
        (499.0, "STABLE", "1 bar below setpoint"),
        (501.0, "STABLE", "1 bar above setpoint"),
    ]
    
    for pressure, expected_status, description in test_cases:
        # Calculate error (same as in error calculation test)
        error = setpoint - pressure
        
        # Determine status
        status_text, _ = determine_status(error)
        
        assert status_text == expected_status, \
            f"{description}: pressure={pressure}, error={error}, expected {expected_status}, got {status_text}"


def test_status_determination_color_mapping():
    """
    Test that status colors are correctly mapped.
    
    Verifies:
    1. STABLE always maps to green
    2. WARNING always maps to red
    3. No other color values are returned
    """
    # Test a range of errors
    test_errors = [-100, -50, -25.01, -25, -24.99, 0, 24.99, 25, 25.01, 50, 100]
    
    for error in test_errors:
        status_text, status_color = determine_status(error)
        
        # Verify color matches status
        if status_text == "STABLE":
            assert status_color == "green", \
                f"STABLE status should have green color, got {status_color} (error={error})"
        elif status_text == "WARNING":
            assert status_color == "red", \
                f"WARNING status should have red color, got {status_color} (error={error})"
        else:
            pytest.fail(f"Unexpected status text: {status_text} (error={error})")


def test_status_determination_requirements_compliance():
    """
    Test compliance with specific requirements.
    
    Requirements 5.2: WHEN the pressure error magnitude is less than or equal
    to 25 bar, THE Dashboard SHALL display "STABLE" status in green
    
    Requirements 5.3: WHEN the pressure error magnitude exceeds 25 bar,
    THE Dashboard SHALL display "WARNING" status in red
    """
    # Requirement 5.2: |error| <= 25 bar -> STABLE (green)
    stable_errors = [0.0, 10.0, 20.0, 25.0, -10.0, -20.0, -25.0]
    for error in stable_errors:
        status_text, status_color = determine_status(error)
        assert status_text == "STABLE", \
            f"Requirement 5.2 violation: |{error}| <= 25 should be STABLE, got {status_text}"
        assert status_color == "green", \
            f"Requirement 5.2 violation: STABLE should be green, got {status_color}"
    
    # Requirement 5.3: |error| > 25 bar -> WARNING (red)
    warning_errors = [25.01, 30.0, 50.0, 100.0, -25.01, -30.0, -50.0, -100.0]
    for error in warning_errors:
        status_text, status_color = determine_status(error)
        assert status_text == "WARNING", \
            f"Requirement 5.3 violation: |{error}| > 25 should be WARNING, got {status_text}"
        assert status_color == "red", \
            f"Requirement 5.3 violation: WARNING should be red, got {status_color}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
