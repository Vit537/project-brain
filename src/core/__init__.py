"""
Core module for JARVIS modular architecture
Based on OpenClaw patterns
"""

from .base_module import BaseModule
from .module_manager import ModuleManager
from .shared_resources import SharedResources
from .intent_router import IntentRouter

__all__ = ['BaseModule', 'ModuleManager', 'SharedResources', 'IntentRouter']
