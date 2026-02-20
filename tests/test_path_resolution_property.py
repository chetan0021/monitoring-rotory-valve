"""
Property-Based Test: Path Resolution Correctness

Property 3: Path Resolution Correctness
Validates: Requirements 2.3

This test verifies that the path resolution logic correctly navigates
from the executable directory to find simulation_runner.py in the
project root.
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, assume


def resolve_simulation_runner_path(executable_dir):
    """
    Resolve the path to simulation_runner.py from the executable directory.
    
    Mimics the C++ implementation in mainwindow.cpp:
        QString appDir = QCoreApplication::applicationDirPath();
        QDir projectRoot(appDir);
        
        // Navigate from build directory to project root
        // Could be gui/build/ or gui/build/Release/
        projectRoot.cdUp();  // From build/ or Release/ to gui/ or build/
        if (projectRoot.dirName() == "build") {
            projectRoot.cdUp();  // From build/ to gui/
        }
        projectRoot.cdUp();  // From gui/ to project root
        
        QString scriptPath = projectRoot.absoluteFilePath("simulation_runner.py");
    
    Args:
        executable_dir: Absolute path to the directory containing the executable
    
    Returns:
        Absolute path to simulation_runner.py
    """
    project_root = Path(executable_dir)
    
    # Navigate up from build directory
    project_root = project_root.parent  # From build/ or Release/ to gui/ or build/
    
    # If we're in a build subdirectory (e.g., Release/), go up one more level
    if project_root.name == "build":
        project_root = project_root.parent  # From build/ to gui/
    
    # Go up from gui/ to project root
    project_root = project_root.parent
    
    # Construct path to simulation_runner.py
    script_path = project_root / "simulation_runner.py"
    
    return script_path.resolve()


# Hypothesis strategy for generating executable directory structures
@st.composite
def executable_dir_strategy(draw):
    """
    Generate various executable directory structures.
    
    Valid structures:
    1. project_root/gui/build/
    2. project_root/gui/build/Release/
    3. project_root/gui/build/Debug/
    4. project_root/gui/build/RelWithDebInfo/
    5. project_root/gui/build/MinSizeRel/
    
    Returns:
        Tuple of (temp_project_root, executable_dir_relative_path)
    """
    # Choose build configuration
    build_config = draw(st.sampled_from([
        "build",           # Unix-style: gui/build/
        "build/Release",   # Windows-style: gui/build/Release/
        "build/Debug",
        "build/RelWithDebInfo",
        "build/MinSizeRel",
    ]))
    
    return build_config


# Property Test
@given(build_config=executable_dir_strategy())
def test_path_resolution_property(build_config):
    """
    **Validates: Requirements 2.3**
    
    Property 3: Path Resolution Correctness
    
    For any valid executable directory structure following the project layout
    (gui/build/ or gui/build/Release/), navigating up two directories and
    appending "simulation_runner.py" should produce a valid absolute path
    to the script.
    
    This property ensures:
    1. Path resolution works for Unix-style builds (gui/build/)
    2. Path resolution works for Windows-style builds (gui/build/Release/)
    3. Resulting path is absolute
    4. Resulting path points to the correct location
    """
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Create directory structure
        gui_dir = project_root / "gui"
        build_dir = gui_dir / build_config
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create simulation_runner.py in project root
        script_path = project_root / "simulation_runner.py"
        script_path.write_text("# Simulation runner script\n")
        
        # Resolve path from executable directory
        resolved_path = resolve_simulation_runner_path(str(build_dir))
        
        # Verify path is absolute
        assert resolved_path.is_absolute(), \
            f"Resolved path should be absolute: {resolved_path}"
        
        # Verify path points to simulation_runner.py
        assert resolved_path.name == "simulation_runner.py", \
            f"Resolved path should point to simulation_runner.py: {resolved_path}"
        
        # Verify path exists
        assert resolved_path.exists(), \
            f"Resolved path should exist: {resolved_path}"
        
        # Verify path is in project root
        assert resolved_path.parent == project_root, \
            f"Resolved path should be in project root: {resolved_path.parent} != {project_root}"
        
        # Verify we can read the file
        content = resolved_path.read_text()
        assert "Simulation runner script" in content, \
            "Should be able to read simulation_runner.py"


# Edge case tests
def test_path_resolution_edge_cases():
    """
    Test specific edge cases for path resolution.
    
    Edge cases:
    1. Unix-style build directory (gui/build/)
    2. Windows Release build (gui/build/Release/)
    3. Windows Debug build (gui/build/Debug/)
    4. Deep nested structure
    """
    test_cases = [
        ("gui/build", "Unix-style build directory"),
        ("gui/build/Release", "Windows Release build"),
        ("gui/build/Debug", "Windows Debug build"),
        ("gui/build/RelWithDebInfo", "RelWithDebInfo build"),
        ("gui/build/MinSizeRel", "MinSizeRel build"),
    ]
    
    for build_path, description in test_cases:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create directory structure
            build_dir = project_root / build_path
            build_dir.mkdir(parents=True, exist_ok=True)
            
            # Create simulation_runner.py
            script_path = project_root / "simulation_runner.py"
            script_path.write_text(f"# Test: {description}\n")
            
            # Resolve path
            resolved_path = resolve_simulation_runner_path(str(build_dir))
            
            # Verify
            assert resolved_path.exists(), f"{description}: Path should exist"
            assert resolved_path.name == "simulation_runner.py", \
                f"{description}: Should resolve to simulation_runner.py"
            assert resolved_path.parent == project_root, \
                f"{description}: Should be in project root"


def test_path_resolution_absolute_path():
    """
    Test that resolved path is always absolute.
    
    Verifies:
    1. Path is absolute (not relative)
    2. Path can be used directly without further resolution
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        build_dir = project_root / "gui" / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = project_root / "simulation_runner.py"
        script_path.write_text("# Test script\n")
        
        # Resolve path
        resolved_path = resolve_simulation_runner_path(str(build_dir))
        
        # Verify it's absolute
        assert resolved_path.is_absolute(), "Path should be absolute"
        
        # Verify it doesn't contain relative components
        assert ".." not in str(resolved_path), "Path should not contain '..'"
        assert not str(resolved_path).startswith("."), "Path should not start with '.'"


def test_path_resolution_with_symlinks():
    """
    Test path resolution with symbolic links.
    
    Verifies that path resolution works correctly even when
    directories contain symbolic links.
    """
    # Skip on Windows where symlinks require admin privileges
    if os.name == 'nt':
        pytest.skip("Symlink test skipped on Windows")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Create actual directory structure
        actual_gui = project_root / "gui_actual"
        build_dir = actual_gui / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlink
        symlink_gui = project_root / "gui"
        symlink_gui.symlink_to(actual_gui)
        
        # Create simulation_runner.py
        script_path = project_root / "simulation_runner.py"
        script_path.write_text("# Test with symlinks\n")
        
        # Resolve path through symlink
        resolved_path = resolve_simulation_runner_path(str(symlink_gui / "build"))
        
        # Verify path exists and is correct
        assert resolved_path.exists(), "Path should exist"
        assert resolved_path.name == "simulation_runner.py", \
            "Should resolve to simulation_runner.py"


def test_path_resolution_current_project():
    """
    Test path resolution with the actual current project structure.
    
    This test verifies that the path resolution logic works with
    the real project directory structure.
    """
    # Get the actual project root (tests/ is in project root)
    current_file = Path(__file__)
    project_root = current_file.parent.parent  # Up from tests/ to project root
    
    # Check if we're in the expected structure
    if not (project_root / "gui").exists():
        pytest.skip("Not in expected project structure")
    
    # Simulate executable directories
    test_cases = [
        project_root / "gui" / "build",
        project_root / "gui" / "build" / "Release",
    ]
    
    for build_dir in test_cases:
        # Create the directory if it doesn't exist (for testing)
        build_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Resolve path
            resolved_path = resolve_simulation_runner_path(str(build_dir))
            
            # Verify it points to the correct location
            expected_path = project_root / "simulation_runner.py"
            assert resolved_path == expected_path, \
                f"Should resolve to {expected_path}, got {resolved_path}"
            
            # Verify the file exists
            if expected_path.exists():
                assert resolved_path.exists(), "Resolved path should exist"
        finally:
            # Clean up test directories if they were created
            if build_dir.exists() and not any(build_dir.iterdir()):
                build_dir.rmdir()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
