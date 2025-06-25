import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional

import yaml
from flask import Flask, jsonify, request


# --- Mock SDK Classes ---
class MockSlackAPI:
    """Mock Slack API for testing SaaS access revocation"""
    
    @staticmethod
    def revoke_user_access(user: str, workspace: str) -> Dict[str, Any]:
        return {
            "success": True,
            "message": f"Access revoked for {user} in workspace {workspace}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "slack.admin.users.remove"
        }

class MockAWSS3:
    """Mock AWS S3 API for testing bucket policy changes"""
    
    @staticmethod
    def put_public_access_block(bucket_name: str, region: str) -> Dict[str, Any]:
        return {
            "success": True,
            "message": f"Public access block applied to bucket {bucket_name}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "s3.put_public_access_block",
            "bucket": bucket_name,
            "region": region
        }
    
    @staticmethod
    def put_bucket_policy(bucket_name: str, policy: Dict) -> Dict[str, Any]:
        return {
            "success": True,
            "message": f"Bucket policy updated for {bucket_name}",
            "timestamp": datetime.now().isoformat(),
            "api_call": "s3.put_bucket_policy",
            "bucket": bucket_name
        }


# --- Audit Trail Manager ---
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
                   api_responses: list = None, dry_run: bool = False):
        """Log an action to the audit trail"""
        if self.audit_format == 'markdown':
            self._log_markdown(event_data, result, api_responses, dry_run)
        else:
            self._log_json(event_data, result, api_responses, dry_run)
    
    def _log_markdown(self, event_data: Dict[str, Any], result: Dict[str, Any], 
                     api_responses: list = None, dry_run: bool = False):
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
                 api_responses: list = None, dry_run: bool = False):
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


# --- Part 5: Stateful Logging Setup ---
def setup_logging(log_file='logs/reaper_actions.log'):
    """
    Configures logging to a rotating file. This creates a persistent audit
    trail of all actions taken by the agent.
    """
    import os

    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    print(f"[Reaper Logging] Actions will be logged to '{log_file}'")
    logger = logging.getLogger('ReaperAgentLogger')
    logger.setLevel(logging.INFO)

    # Use a rotating file handler to prevent the log file from growing indefinitely.
    # It will create a new file when the current one reaches 5MB, keeping 5 old files.
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024*5, backupCount=5)
    
    # Define the format for the log entries.
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)
    return logger

# --- Modules (Unchanged) ---
# The individual response modules remain self-contained and require no changes.

class BaseReaperModule(ABC):
    """Abstract Base Class for all remediation modules."""
    def __init__(self, event, dry_run_mode: bool = False):
        self.event = event
        self.dry_run_mode = dry_run_mode
        self.api_responses = []
        self.log_prefix = f"--- Event ID: {event.get('event_id')} | Module: {self.__class__.__name__} | Mode: {'DRY RUN' if dry_run_mode else 'LIVE'} ---"
    
    @abstractmethod
    def validate(self): pass
    
    @abstractmethod
    def execute(self): pass
    
    @abstractmethod
    def report(self): pass
    
    def get_api_responses(self) -> list:
        """Return collected API responses for audit trail"""
        return self.api_responses

class SaaSAccessReaper(BaseReaperModule):
    """Module to handle unauthorized access to SaaS applications."""
    
    def validate(self):
        if self.event.get("user") and self.event.get("source"):
            return "[Validate] SUCCESS: Required fields 'user' and 'source' are present."
        return "[Validate] FAILED: Event is missing 'user' or 'source'."
    
    def execute(self):
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
            return f"[Execute]  ACTION: Revoked access for user '{user}' to '{source}'."
    
    def report(self):
        mode = "DRY RUN" if self.dry_run_mode else "LIVE"
        return f"[Report]   {mode}: Remediation policy applied for user '{self.event.get('user')}'."

class S3VisibilityReaper(BaseReaperModule):
    """Module to handle publicly exposed S3 buckets."""
    
    def validate(self):
        if self.event.get("bucket_name") and self.event.get("region"):
            return "[Validate] SUCCESS: Required fields 'bucket_name' and 'region' are present."
        return "[Validate] FAILED: Event is missing 'bucket_name' or 'region'."
    
    def execute(self):
        bucket = self.event.get('bucket_name')
        region = self.event.get('region')
        
        if self.dry_run_mode:
            # Simulate API calls without actually executing
            mock_response = {
                "dry_run": True,
                "action": "put_public_access_block",
                "bucket": bucket,
                "region": region,
                "timestamp": datetime.now().isoformat(),
                "would_execute": f"s3.put_public_access_block for {bucket}"
            }
            self.api_responses.append(mock_response)
            return f"[Execute]  DRY RUN: Would restrict public permissions on S3 bucket '{bucket}'."
        else:
            # Execute actual API calls (using mock for demo)
            api_response1 = MockAWSS3.put_public_access_block(bucket, region)
            self.api_responses.append(api_response1)
            
            # Also update bucket policy
            restrictive_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket}/*",
                    "Condition": {"Bool": {"aws:SecureTransport": "false"}}
                }]
            }
            api_response2 = MockAWSS3.put_bucket_policy(bucket, restrictive_policy)
            self.api_responses.append(api_response2)
            
            return f"[Execute]  ACTION: Restricted public permissions on S3 bucket '{bucket}'."
    
    def report(self):
        mode = "DRY RUN" if self.dry_run_mode else "LIVE"
        return f"[Report]   {mode}: Public access block applied to '{self.event.get('bucket_name')}'."

# --- Dynamic Module Loading from Config (Unchanged) ---

def load_module_map_from_config(config_path='config.yaml'):
    """
    Loads the module configuration from a YAML file and maps event types
    to their corresponding module classes.
    Returns both the module map and the full config.
    """
    print(f"[Reaper Config] Loading module map from '{config_path}'...")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[Reaper Config] FATAL: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[Reaper Config] FATAL: Error parsing YAML file: {e}")
        sys.exit(1)

    module_map = {}
    for event_type, module_info in config.get('modules', {}).items():
        class_name = module_info.get('class')
        if class_name in globals():
            module_map[event_type] = globals()[class_name]
            print(f"  -> Mapped event '{event_type}' to module '{class_name}'")
        else:
            print(f"[Reaper Config] WARNING: Class '{class_name}' for event '{event_type}' not found. Skipping.")
    
    # Print configuration settings
    settings = config.get('settings', {})
    print(f"[Reaper Config] Dry run mode: {settings.get('dry_run_mode', False)}")
    print(f"[Reaper Config] Audit format: {settings.get('audit_format', 'markdown')}")
    print(f"[Reaper Config] Audit file: {settings.get('audit_file', 'logs/audit_trail.md')}")
    
    return module_map, config

# --- Agent and API ---

class ReaperAgent:
    """Enhanced agent with audit trail and dry run capabilities."""
    
    def __init__(self, modules_map, config):
        self.modules_map = modules_map
        self.config = config
        self.settings = config.get('settings', {})
        self.dry_run_mode = self.settings.get('dry_run_mode', False)
        self.audit_manager = AuditTrailManager(config)
        
        mode_text = "DRY RUN" if self.dry_run_mode else "LIVE"
        print(f"[Reaper] Modular API Agent initialized in {mode_text} mode.")
        print("[Reaper] Listening for events at http://127.0.0.1:5001/event")

    def process_event(self, event_data):
        response_log = []
        event_type = event_data.get("type")
        
        if not event_type:
            result = {"status": "error", "log": ["Event is missing 'type' field."]}
            self.audit_manager.log_action(event_data, result, dry_run=self.dry_run_mode)
            return result
        
        ModuleClass = self.modules_map.get(event_type)
        if not ModuleClass:
            result = {"status": "ignored", "log": [f"No response module found for event type '{event_type}'."]}
            self.audit_manager.log_action(event_data, result, dry_run=self.dry_run_mode)
            return result
        
        # Create module instance with dry run mode
        module_instance = ModuleClass(event_data, self.dry_run_mode)
        response_log.append(module_instance.log_prefix)
        
        # Validate
        validation_result = module_instance.validate()
        response_log.append(validation_result)
        
        if "SUCCESS" in validation_result:
            # Execute
            response_log.append(module_instance.execute())
            response_log.append(module_instance.report())
            result = {"status": "processed", "log": response_log}
            
            # Log to audit trail with API responses
            self.audit_manager.log_action(
                event_data, 
                result, 
                module_instance.get_api_responses(),
                self.dry_run_mode
            )
            return result
        else:
            result = {"status": "validation_failed", "log": response_log}
            self.audit_manager.log_action(event_data, result, dry_run=self.dry_run_mode)
            return result
    
    def toggle_dry_run_mode(self):
        """Toggle dry run mode on/off"""
        self.dry_run_mode = not self.dry_run_mode
        mode_text = "DRY RUN" if self.dry_run_mode else "LIVE"
        print(f"[Reaper] Mode switched to {mode_text}")
        return self.dry_run_mode

# --- Application Setup ---
app = Flask(__name__)

# Initialize logging and the agent on startup
logger = setup_logging()
remediation_modules, config = load_module_map_from_config()
agent = ReaperAgent(remediation_modules, config)

@app.route('/', methods=['GET'])
def health_check():
    mode = "DRY_RUN" if agent.dry_run_mode else "LIVE"
    return jsonify({
        "status": "healthy", 
        "service": "reaper-agent", 
        "version": "1.0.0",
        "mode": mode,
        "audit_format": agent.settings.get('audit_format', 'markdown')
    }), 200

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration and status"""
    return jsonify({
        "dry_run_mode": agent.dry_run_mode,
        "audit_format": agent.settings.get('audit_format', 'markdown'),
        "audit_file": agent.settings.get('audit_file', 'logs/audit_trail.md'),
        "modules": list(agent.modules_map.keys())
    }), 200

@app.route('/toggle-dry-run', methods=['POST'])
def toggle_dry_run():
    """Toggle dry run mode"""
    new_mode = agent.toggle_dry_run_mode()
    return jsonify({
        "dry_run_mode": new_mode,
        "message": f"Dry run mode {'enabled' if new_mode else 'disabled'}"
    }), 200

@app.route('/audit', methods=['GET'])
def get_audit_trail():
    """Get recent audit trail entries"""
    try:
        audit_file = agent.settings.get('audit_file', 'logs/audit_trail.md')
        if agent.settings.get('audit_format') == 'json':
            with open(audit_file, 'r') as f:
                entries = json.load(f)
                # Return last 10 entries
                return jsonify({"entries": entries[-10:]}), 200
        else:
            # For markdown, return file info
            if os.path.exists(audit_file):
                stat = os.stat(audit_file)
                return jsonify({
                    "format": "markdown",
                    "file": audit_file,
                    "size_bytes": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "message": "Use file system to access markdown audit trail"
                }), 200
            else:
                return jsonify({"message": "Audit file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/event', methods=['POST'])
def handle_event():
    if not request.is_json:
        return jsonify({"status": "error", "log": ["Invalid request: Content-Type must be application/json."]}), 400
    
    event_data = request.get_json()
    result = agent.process_event(event_data)
    
    # Log to console for real-time monitoring
    print(json.dumps(result, indent=2))
    
    # Log the JSON result to the file for a persistent audit trail
    logger.info(json.dumps(result))
    
    return jsonify(result), 200

def main():
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    main()
