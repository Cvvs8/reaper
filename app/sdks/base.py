"""
Base SDK class for standardized API interfaces
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSDK(ABC):
    """Abstract base class for all SDK implementations"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the SDK is properly configured and available"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the SDK"""
        pass
