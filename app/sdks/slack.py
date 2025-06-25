"""
Mock Slack API for testing SaaS access revocation
"""
import random
from datetime import datetime
from typing import Dict, Any

from .base import BaseSDK


class MockSlackAPI(BaseSDK):
    """Mock Slack API for testing SaaS access revocation"""
    
    def is_available(self) -> bool:
        """Check if SDK is available"""
        return True
    
    def get_name(self) -> str:
        """Return SDK name"""
        return "MockSlackAPI"
    
    @staticmethod
    def revoke_user_access(user: str, workspace: str) -> Dict[str, Any]:
        """Simulate revoking user access from Slack workspace"""
        # Simulate network/API exceptions
        if "exception" in user.lower():
            raise ConnectionError(f"Network error connecting to Slack API for workspace {workspace}")
        
        if "timeout" in user.lower():
            raise TimeoutError(f"Timeout while calling Slack API for user {user}")
        
        if "unauthorized" in user.lower():
            raise PermissionError(f"Insufficient permissions to revoke access for {user}")
        
        # Simulate API failures (return error response)
        if "fail" in user or random.random() < 0.2:  # 20% chance of failure
            return {
                "success": False,
                "message": f"Failed to revoke access for {user} in workspace {workspace}",
                "timestamp": datetime.now().isoformat(),
                "api_call": "slack.admin.users.remove",
                "error_code": "PERMISSION_DENIED"
            }
        
        return {
            "success": True,
            "message": f"Access revoked for {user} in workspace {workspace}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "slack.admin.users.remove"
        }
