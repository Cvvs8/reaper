"""
Mock SDK implementations for testing
"""

from .slack import MockSlackAPI
from .aws import MockAWSS3

__all__ = ['MockSlackAPI', 'MockAWSS3']
