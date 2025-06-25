"""
Flask application and API endpoints
"""
import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request

from .agent import ReaperAgent, load_module_map_from_config
from .utils.schema import APISchemaValidator
from .utils.dashboard import DashboardGenerator


def setup_logging(log_file: str = 'logs/reaper_actions.log') -> logging.Logger:
    """
    Configure logging to a rotating file for persistent audit trail.
    """
    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    print(f"[Reaper Logging] Actions will be logged to '{log_file}'")
    logger = logging.getLogger('ReaperAgentLogger')
    logger.setLevel(logging.INFO)

    # Use rotating file handler to prevent log file from growing indefinitely
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024*5, backupCount=5)
    
    # Define log entry format
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)
    return logger


def create_app() -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Initialize logging and agent on startup
    logger = setup_logging()
    remediation_modules, config = load_module_map_from_config()
    agent = ReaperAgent(remediation_modules, config)
    
    @app.route('/', methods=['GET'])
    def health_check():
        """Health check endpoint with system status"""
        mode = "DRY_RUN" if agent.dry_run_mode else "LIVE"
        return jsonify({
            "status": "healthy", 
            "service": "reaper-agent", 
            "version": "1.0.0",
            "mode": mode,
            "audit_format": agent.settings.get('audit_format', 'markdown'),
            "modules": list(agent.modules_map.keys())
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
            if agent.settings.get('audit_format') == 'json':
                entries = agent.audit_manager.get_recent_entries(10)
                return jsonify({"entries": entries}), 200
            else:
                # For markdown, return file info
                file_info = agent.audit_manager.get_file_info()
                if file_info['exists']:
                    return jsonify({
                        **file_info,
                        "message": "Use file system to access markdown audit trail"
                    }), 200
                else:
                    return jsonify({"message": "Audit file not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        """Visual dashboard for monitoring agent status"""
        try:
            return DashboardGenerator.render_dashboard(agent, agent.audit_manager)
        except Exception as e:
            return f"<h1>Dashboard Error</h1><p>{str(e)}</p>", 500

    @app.route('/openapi.json', methods=['GET'])
    def get_openapi_spec():
        """Get OpenAPI specification"""
        return jsonify(APISchemaValidator.get_openapi_spec()), 200

    @app.route('/event', methods=['POST'])
    def handle_event():
        """Process security event"""
        if not request.is_json:
            return jsonify({
                "status": "error", 
                "log": ["Invalid request: Content-Type must be application/json."]
            }), 400
        
        event_data = request.get_json()
        
        # Validate event data against schema
        is_valid, validation_message = APISchemaValidator.validate_event(event_data)
        if not is_valid:
            return jsonify({
                "status": "validation_error",
                "log": [f"Schema validation failed: {validation_message}"]
            }), 400
        
        result = agent.process_event(event_data)
        
        # Log to console for real-time monitoring
        print(json.dumps(result, indent=2))
        
        # Log to file for persistent audit trail
        logger.info(json.dumps(result))
        
        return jsonify(result), 200
    
    return app


def main():
    """Main entry point"""
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=False)


if __name__ == "__main__":
    main()
