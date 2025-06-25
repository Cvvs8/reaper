"""
Main agent class for processing security events
"""
import sys
from typing import Dict, Any

import yaml

from .modules import SaaSAccessReaper, S3VisibilityReaper
from .utils.audit import AuditTrailManager


class ReaperAgent:
    """Enhanced agent with audit trail and dry run capabilities."""
    
    def __init__(self, modules_map: Dict[str, Any], config: Dict[str, Any]):
        self.modules_map = modules_map
        self.config = config
        self.settings = config.get('settings', {})
        self.dry_run_mode = self.settings.get('dry_run_mode', False)
        self.audit_manager = AuditTrailManager(config)
        
        mode_text = "DRY RUN" if self.dry_run_mode else "LIVE"
        print(f"[Reaper] Modular API Agent initialized in {mode_text} mode.")
        print("[Reaper] Listening for events at http://127.0.0.1:5001/event")

    def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a security event through appropriate module"""
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
    
    def toggle_dry_run_mode(self) -> bool:
        """Toggle dry run mode on/off"""
        self.dry_run_mode = not self.dry_run_mode
        mode_text = "DRY RUN" if self.dry_run_mode else "LIVE"
        print(f"[Reaper] Mode switched to {mode_text}")
        return self.dry_run_mode


def load_module_map_from_config(config_path: str = 'config.yaml') -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load module configuration from YAML file and map event types to module classes.
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

    # Map of available module classes
    available_modules = {
        'SaaSAccessReaper': SaaSAccessReaper,
        'S3VisibilityReaper': S3VisibilityReaper
    }

    module_map = {}
    for event_type, module_info in config.get('modules', {}).items():
        class_name = module_info.get('class')
        if class_name in available_modules:
            module_map[event_type] = available_modules[class_name]
            print(f"  -> Mapped event '{event_type}' to module '{class_name}'")
        else:
            print(f"[Reaper Config] WARNING: Class '{class_name}' for event '{event_type}' not found. Skipping.")
    
    # Print configuration settings
    settings = config.get('settings', {})
    print(f"[Reaper Config] Dry run mode: {settings.get('dry_run_mode', False)}")
    print(f"[Reaper Config] Audit format: {settings.get('audit_format', 'markdown')}")
    print(f"[Reaper Config] Audit file: {settings.get('audit_file', 'logs/audit_trail.md')}")
    
    return module_map, config
