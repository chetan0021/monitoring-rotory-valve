"""
Communication Protocol Definition Module

Defines the data structure and protocol for GUI communication.
Required by Section 8 of numerical_state_space_and_simulation_specification.md

Protocol: ZeroMQ (recommended for low-latency industrial control)

Data to be exchanged:
- Current pressure (bar)
- Valve angle (rad or deg)
- Motor current (A)
- Setpoint (bar)
- Controller gains (Kp, Ki, Kd)
- System status
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SystemState:
    """
    System state data structure for GUI communication.
    
    References:
    - numerical_state_space_and_simulation_specification.md: Section 8
    """
    timestamp: float  # Simulation time (s)
    pressure: float  # Current pressure (bar)
    valve_angle: float  # Valve angle (rad)
    motor_current: float  # Motor current (A)
    motor_velocity: float  # Motor angular velocity (rad/s)
    control_voltage: float  # Control voltage (V)
    setpoint: float  # Pressure setpoint (bar)
    
    def to_json(self):
        """
        Serialize to JSON string.
        
        Returns:
            json_string: JSON representation
        """
        pass
    
    @classmethod
    def from_json(cls, json_string):
        """
        Deserialize from JSON string.
        
        Args:
            json_string: JSON representation
        
        Returns:
            SystemState instance
        """
        pass


@dataclass
class ControllerParameters:
    """
    Controller parameters data structure.
    
    Note: Gains are FROZEN and should not be modified during operation.
    """
    Kp: float  # Proportional gain
    Ki: float  # Integral gain
    Kd: float  # Derivative gain
    
    def to_json(self):
        """
        Serialize to JSON string.
        
        Returns:
            json_string: JSON representation
        """
        pass
    
    @classmethod
    def from_json(cls, json_string):
        """
        Deserialize from JSON string.
        
        Args:
            json_string: JSON representation
        
        Returns:
            ControllerParameters instance
        """
        pass


@dataclass
class CommandMessage:
    """
    Command message from GUI to simulation.
    """
    command_type: str  # "set_setpoint", "start", "stop", "reset"
    value: Optional[float] = None  # Command value (if applicable)
    
    def to_json(self):
        """
        Serialize to JSON string.
        
        Returns:
            json_string: JSON representation
        """
        pass
    
    @classmethod
    def from_json(cls, json_string):
        """
        Deserialize from JSON string.
        
        Args:
            json_string: JSON representation
        
        Returns:
            CommandMessage instance
        """
        pass
