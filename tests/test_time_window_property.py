"""
Property-Based Test: Time Window Management

Tests Property 1: Data Point Time Window Management
Validates: Requirements 1.4

This test verifies that after adding data points and removing old ones,
all remaining points are within 15 seconds of the most recent timestamp.
"""

import pytest
from hypothesis import given, strategies as st, assume


# Constants
TIME_WINDOW = 15.0  # seconds


@st.composite
def data_point_sequence_strategy(draw):
    """
    Generate a sequence of data points with increasing timestamps.
    
    Returns a list of (timestamp, value) tuples where timestamps are
    monotonically increasing.
    """
    # Generate number of data points (between 5 and 100)
    num_points = draw(st.integers(min_value=5, max_value=100))
    
    # Generate starting timestamp
    start_time = draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    
    # Generate time deltas (positive increments)
    time_deltas = draw(st.lists(
        st.floats(min_value=0.01, max_value=2.0, allow_nan=False, allow_infinity=False),
        min_size=num_points - 1,
        max_size=num_points - 1
    ))
    
    # Build timestamps by accumulating deltas
    timestamps = [start_time]
    current_time = start_time
    for delta in time_deltas:
        current_time += delta
        timestamps.append(current_time)
    
    # Generate random values for each timestamp
    values = draw(st.lists(
        st.floats(min_value=0.0, max_value=700.0, allow_nan=False, allow_infinity=False),
        min_size=num_points,
        max_size=num_points
    ))
    
    return list(zip(timestamps, values))


def simulate_time_window_management(data_points):
    """
    Simulate the time window management logic.
    
    This mimics the Qt GUI behavior:
    1. Add new data point
    2. Remove points older than TIME_WINDOW seconds from the latest timestamp
    
    Args:
        data_points: List of (timestamp, value) tuples
        
    Returns:
        List of (timestamp, value) tuples within the time window
    """
    if not data_points:
        return []
    
    # Get the latest timestamp
    latest_timestamp = data_points[-1][0]
    
    # Filter points to keep only those within TIME_WINDOW
    filtered_points = [
        (ts, val) for ts, val in data_points
        if ts >= latest_timestamp - TIME_WINDOW
    ]
    
    return filtered_points


@given(data_points=data_point_sequence_strategy())
def test_time_window_management_property(data_points):
    """
    **Validates: Requirements 1.4**
    
    Property 1: Data Point Time Window Management
    
    For any sequence of data points with timestamps, after adding a new point
    and removing old points, all remaining points in the plot should have
    timestamps within 15 seconds of the most recent timestamp.
    """
    # Ensure we have at least one data point
    assume(len(data_points) > 0)
    
    # Simulate the time window management
    filtered_points = simulate_time_window_management(data_points)
    
    # Verify we have at least one point (the latest one should always remain)
    assert len(filtered_points) > 0, "At least the latest point should remain"
    
    # Get the latest timestamp
    latest_timestamp = data_points[-1][0]
    
    # Verify all remaining points are within TIME_WINDOW of the latest timestamp
    for timestamp, value in filtered_points:
        time_diff = latest_timestamp - timestamp
        assert time_diff >= 0, f"Timestamp {timestamp} is after latest {latest_timestamp}"
        assert time_diff <= TIME_WINDOW, \
            f"Point at {timestamp} is {time_diff:.2f}s before latest {latest_timestamp}, exceeds {TIME_WINDOW}s window"
    
    # Verify the latest point is always included
    assert filtered_points[-1][0] == latest_timestamp, "Latest point must be included"
    
    # Verify no points were incorrectly removed (all points within window are kept)
    expected_count = sum(1 for ts, _ in data_points if ts >= latest_timestamp - TIME_WINDOW)
    assert len(filtered_points) == expected_count, \
        f"Expected {expected_count} points within window, got {len(filtered_points)}"


def test_time_window_edge_cases():
    """Test specific edge cases for time window management."""
    
    # Test 1: Single data point
    data = [(10.0, 500.0)]
    filtered = simulate_time_window_management(data)
    assert len(filtered) == 1
    assert filtered[0] == (10.0, 500.0)
    
    # Test 2: All points within window
    data = [
        (0.0, 100.0),
        (5.0, 200.0),
        (10.0, 300.0),
        (14.0, 400.0)
    ]
    filtered = simulate_time_window_management(data)
    assert len(filtered) == 4  # All points within 15s of latest (14.0)
    
    # Test 3: Some points outside window
    data = [
        (0.0, 100.0),   # 20s before latest, should be removed
        (5.0, 200.0),   # 15s before latest, should be kept (exactly at boundary)
        (10.0, 300.0),  # 10s before latest, should be kept
        (20.0, 400.0)   # Latest point
    ]
    filtered = simulate_time_window_management(data)
    assert len(filtered) == 3  # First point should be removed
    assert filtered[0][0] == 5.0  # Oldest remaining point
    assert filtered[-1][0] == 20.0  # Latest point
    
    # Test 4: Boundary case - exactly 15 seconds
    data = [
        (0.0, 100.0),
        (15.0, 200.0)
    ]
    filtered = simulate_time_window_management(data)
    assert len(filtered) == 2  # Both points should be kept (0.0 is exactly 15s before 15.0)
    
    # Test 5: Boundary case - just over 15 seconds
    data = [
        (0.0, 100.0),
        (15.01, 200.0)
    ]
    filtered = simulate_time_window_management(data)
    assert len(filtered) == 1  # First point should be removed (15.01s difference)
    assert filtered[0][0] == 15.01
    
    # Test 6: Many points, only recent ones kept
    data = [(float(i), float(i * 10)) for i in range(100)]
    filtered = simulate_time_window_management(data)
    latest = data[-1][0]  # 99.0
    expected_oldest = latest - TIME_WINDOW  # 84.0
    assert all(ts >= expected_oldest for ts, _ in filtered)
    assert filtered[-1][0] == latest
    
    # Test 7: Points with same timestamp
    data = [
        (10.0, 100.0),
        (10.0, 200.0),
        (10.0, 300.0)
    ]
    filtered = simulate_time_window_management(data)
    assert len(filtered) == 3  # All points at same time should be kept


def test_time_window_incremental_simulation():
    """
    Test simulating incremental data point addition as would happen in real GUI.
    """
    plot_data = []
    
    # Simulate adding points over time
    for i in range(200):
        timestamp = i * 0.1  # 100ms intervals
        value = 500.0 + (i % 50)  # Some varying value
        
        # Add new point
        plot_data.append((timestamp, value))
        
        # Apply time window management
        plot_data = simulate_time_window_management(plot_data)
        
        # Verify invariant: all points within TIME_WINDOW
        latest = plot_data[-1][0]
        for ts, _ in plot_data:
            assert latest - ts <= TIME_WINDOW, \
                f"Point at {ts} exceeds window from latest {latest}"
        
        # Verify we don't accumulate too many points
        # At 10 Hz (0.1s intervals), 15s window should have at most 150 points
        assert len(plot_data) <= 151, \
            f"Too many points accumulated: {len(plot_data)}"


if __name__ == "__main__":
    # Run the property test manually
    test_time_window_management_property()
    test_time_window_edge_cases()
    test_time_window_incremental_simulation()
    print("All time window management tests passed!")
