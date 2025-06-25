"""
Audit trail management for security actions
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


class AuditTrailManager:
    """Manages audit trail generation in multiple formats"""
    
    def __init__(self, config: Dict[str, Any]):
        self.audit_format = config.get('settings', {}).get('audit_format', 'markdown')
        self.audit_file = config.get('settings', {}).get('audit_file', 'logs/audit_trail.md')
        self.ensure_audit_file_exists()
    
    def ensure_audit_file_exists(self):
        """Create audit file and directory if they don't exist"""
        audit_dir = os.path.dirname(self.audit_file)
        if audit_dir and not os.path.exists(audit_dir):
            os.makedirs(audit_dir)
        
        if not os.path.exists(self.audit_file):
            if self.audit_format == 'markdown':
                self._initialize_markdown_file()
            else:
                with open(self.audit_file, 'w') as f:
                    json.dump([], f)
    
    def _initialize_markdown_file(self):
        """Initialize markdown audit file with header"""
        with open(self.audit_file, 'w') as f:
            f.write("# Reaper Agent Audit Trail\n\n")
            f.write("This file contains a detailed audit trail of all security remediation actions.\n\n")
            f.write("---\n\n")
    
    def log_action(self, event_data: Dict[str, Any], result: Dict[str, Any], 
                   api_responses: Optional[List] = None, dry_run: bool = False):
        """Log an action to the audit trail"""
        if self.audit_format == 'markdown':
            self._log_markdown(event_data, result, api_responses, dry_run)
        else:
            self._log_json(event_data, result, api_responses, dry_run)
    
    def _log_markdown(self, event_data: Dict[str, Any], result: Dict[str, Any], 
                     api_responses: Optional[List] = None, dry_run: bool = False):
        """Log action in markdown format"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        mode = "DRY RUN" if dry_run else "LIVE"
        
        with open(self.audit_file, 'a') as f:
            f.write(f"## Action Report - {timestamp}\n\n")
            f.write(f"**Mode:** {mode}\n\n")
            f.write(f"**Event ID:** {event_data.get('event_id', 'N/A')}\n\n")
            f.write(f"**Event Type:** {event_data.get('type', 'N/A')}\n\n")
            f.write(f"**Status:** {result.get('status', 'Unknown')}\n\n")
            
            f.write("### Event Details\n")
            f.write("```json\n")
            f.write(json.dumps(event_data, indent=2))
            f.write("\n```\n\n")
            
            f.write("### Processing Log\n")
            for log_entry in result.get('log', []):
                f.write(f"- {log_entry}\n")
            f.write("\n")
            
            if api_responses:
                f.write("### API Responses\n")
                for response in api_responses:
                    f.write("```json\n")
                    f.write(json.dumps(response, indent=2))
                    f.write("\n```\n\n")
            
            f.write("---\n\n")
    
    def _log_json(self, event_data: Dict[str, Any], result: Dict[str, Any], 
                 api_responses: Optional[List] = None, dry_run: bool = False):
        """Log action in JSON format"""
        # Read existing entries
        try:
            with open(self.audit_file, 'r') as f:
                entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            entries = []
        
        # Create new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mode": "DRY_RUN" if dry_run else "LIVE",
            "event_data": event_data,
            "result": result,
            "api_responses": api_responses or []
        }
        
        entries.append(entry)
        
        # Write back to file
        with open(self.audit_file, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def get_recent_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent audit entries (for JSON format)"""
        if self.audit_format != 'json':
            return []
        
        try:
            with open(self.audit_file, 'r') as f:
                entries = json.load(f)
                return entries[-limit:]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get audit file information"""
        if os.path.exists(self.audit_file):
            stat = os.stat(self.audit_file)
            return {
                "format": self.audit_format,
                "file": self.audit_file,
                "size_bytes": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }
        else:
            return {
                "format": self.audit_format,
                "file": self.audit_file,
                "exists": False
            }
