"""
Module to handle unauthorized access to SaaS applications
"""
from datetime import datetime

from .base import BaseReaperModule
from ..sdks.slack import MockSlackAPI


class SaaSAccessReaper(BaseReaperModule):
    """Module to handle unauthorized access to SaaS applications."""
    
    def validate(self) -> str:
        """Validate required fields for SaaS access event"""
        if self.event.get("user") and self.event.get("source"):
            return "[Validate] SUCCESS: Required fields 'user' and 'source' are present."
        return "[Validate] FAILED: Event is missing 'user' or 'source'."
    
    def execute(self) -> str:
        """Execute SaaS access revocation"""
        user = self.event.get('user')
        source = self.event.get('source')
        
        if self.dry_run_mode:
            # Simulate API call without actually executing
            mock_response = {
                "dry_run": True,
                "action": "revoke_access",
                "user": user,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "would_execute": f"slack.admin.users.remove for {user}"
            }
            self.api_responses.append(mock_response)
            return f"[Execute]  DRY RUN: Would revoke access for user '{user}' to '{source}'."
        else:
            # Execute actual API call (using mock for demo)
            api_response = MockSlackAPI.revoke_user_access(user, source)
            self.api_responses.append(api_response)
            
            if api_response.get('success'):
                return f"[Execute]  ACTION: Successfully revoked access for user '{user}' to '{source}'."
            else:
                return f"[Execute]  ERROR: Failed to revoke access for user '{user}' to '{source}': {api_response.get('message')}"
    
    def report(self) -> str:
        """Generate execution report"""
        mode = "DRY RUN" if self.dry_run_mode else "LIVE"
        user = self.event.get('user')
        
        # Check if there were any failures in API responses
        if not self.dry_run_mode and self.api_responses:
            last_response = self.api_responses[-1]
            if not last_response.get('success'):
                return f"[Report]   {mode}: FAILED - Remediation failed for user '{user}'"
        
        return f"[Report]   {mode}: Remediation policy applied for user '{user}'"
