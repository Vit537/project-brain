"""
Base Module Class - OpenClaw Pattern
All JARVIS modules inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseModule(ABC):
    """Base class for all JARVIS modules (inspired by OpenClaw)"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.description = ""
        
    @abstractmethod
    async def can_handle(self, intent: Dict[str, Any]) -> bool:
        """
        Check if this module can handle the given intent
        
        Args:
            intent: Dictionary with 'type', 'text', 'action', etc.
            
        Returns:
            bool: True if module can handle this intent
        """
        pass
    
    @abstractmethod
    async def execute(self, intent: Dict[str, Any], shared) -> str:
        """
        Execute module action with access to shared resources
        
        Args:
            intent: Dictionary with action details
            shared: SharedResources instance
            
        Returns:
            str: Response message
        """
        pass
    
    async def initialize(self):
        """Called once when module first loads (lazy init)"""
        print(f"✓ Module '{self.name}' initialized")
    
    async def cleanup(self):
        """Called on shutdown"""
        print(f"✓ Module '{self.name}' cleaned up")
    
    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"<Module: {self.name} ({status})>"
