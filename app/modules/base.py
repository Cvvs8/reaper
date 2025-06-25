"""
Base class for all remediation modules
"""
from abc import ABC, abstractmethod
from typing import List


class BaseReaperModule(ABC):
    """Abstract Base Class for all remediation modules."""
    
    def __init__(self, event, dry_run_mode: bool = False):
        self.event = event
        self.dry_run_mode = dry_run_mode
        self.api_responses = []
        self.log_prefix = f"--- Event ID: {event.get('event_id')} | Module: {self.__class__.__name__} | Mode: {'DRY RUN' if dry_run_mode else 'LIVE'} ---"
    
    @abstractmethod
    def validate(self) -> str:
        """Validate event data"""
        pass
    
    @abstractmethod
    def execute(self) -> str:
        """Execute remediation action"""
        pass
    
    @abstractmethod
    def report(self) -> str:
        """Generate execution report"""
        pass
    
    def get_api_responses(self) -> List:
        """Return collected API responses for audit trail"""
        return self.api_responses
