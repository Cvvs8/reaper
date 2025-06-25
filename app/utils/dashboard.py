"""
Simple dashboard for viewing Reaper Agent status and logs
"""
import json
import os
from datetime import datetime
from flask import render_template_string
from typing import List, Dict, Any


class DashboardGenerator:
    """Generates HTML dashboard for agent monitoring"""
    
    DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reaper Agent Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }
        .status-card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .status-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .mode-live { color: #28a745; }
        .mode-dry { color: #ffc107; }
        .severity-critical { color: #dc3545; }
        .severity-high { color: #fd7e14; }
        .severity-medium { color: #ffc107; }
        .severity-low { color: #28a745; }
        .logs-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .log-entry {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .log-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 14px;
            color: #6c757d;
        }
        .log-content {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            background: white;
            padding: 10px;
            border-radius: 3px;
            border: 1px solid #e9ecef;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .api-docs {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .endpoint {
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-family: monospace;
        }
        .method-get { border-left: 5px solid #28a745; }
        .method-post { border-left: 5px solid #007bff; }
    </style>
    <script>
        function refreshPage() {
            window.location.reload();
        }
        
        function toggleDryRun() {
            fetch('/toggle-dry-run', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshPage();
                })
                .catch(error => alert('Error: ' + error));
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshPage, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Reaper Agent Dashboard</h1>
            <p>Security Automation Agent Monitoring</p>
            <small>Last updated: {{ timestamp }}</small>
        </div>
        
        <button class="refresh-btn" onclick="refreshPage()">🔄 Refresh</button>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>Agent Status</h3>
                <div class="status-value">{{ status.status }}</div>
            </div>
            <div class="status-card">
                <h3>Operating Mode</h3>
                <div class="status-value {{ 'mode-dry' if status.mode == 'DRY RUN' else 'mode-live' }}">
                    {{ status.mode }}
                </div>
                <button onclick="toggleDryRun()" style="margin-top: 10px; padding: 5px 10px; background: #6c757d; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    Toggle Mode
                </button>
            </div>
            <div class="status-card">
                <h3>Active Modules</h3>
                <div class="status-value">{{ status.modules|length }}</div>
                <small>{{ ', '.join(status.modules) }}</small>
            </div>
            <div class="status-card">
                <h3>Recent Events</h3>
                <div class="status-value">{{ events_count }}</div>
                <small>Last 24 hours</small>
            </div>
        </div>
        
        {% if recent_events %}
        <div class="logs-section">
            <h2>📊 Recent Security Events</h2>
            {% for event in recent_events %}
            <div class="log-entry">
                <div class="log-meta">
                    <span><strong>Event ID:</strong> {{ event.event_id }}</span>
                    <span><strong>Type:</strong> {{ event.type }}</span>
                    <span class="severity-{{ event.severity }}"><strong>Severity:</strong> {{ event.severity }}</span>
                    <span>{{ event.timestamp }}</span>
                </div>
                <div class="log-content">{{ event.summary }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="api-docs">
            <h2>🔌 API Endpoints</h2>
            <div class="endpoint method-get">GET /</div>
            <div class="endpoint method-get">GET /config</div>
            <div class="endpoint method-get">GET /audit</div>
            <div class="endpoint method-get">GET /openapi.json</div>
            <div class="endpoint method-post">POST /event</div>
            <div class="endpoint method-post">POST /toggle-dry-run</div>
            <p style="margin-top: 15px;">
                <a href="/openapi.json" target="_blank">📄 View OpenAPI Specification</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def generate_dashboard_data(agent, audit_manager) -> Dict[str, Any]:
        """Generate data for dashboard"""
        try:
            # Get recent events from audit trail
            recent_events = []
            events_count = 0
            
            if audit_manager.audit_format == 'json':
                entries = audit_manager.get_recent_entries(5)
                for entry in entries:
                    recent_events.append({
                        'event_id': entry.get('event_id', 'Unknown'),
                        'type': entry.get('event_type', 'Unknown'),
                        'severity': entry.get('event_data', {}).get('severity', 'medium'),
                        'timestamp': entry.get('timestamp', ''),
                        'summary': f"Status: {entry.get('status', 'unknown')} | Mode: {entry.get('mode', 'unknown')}"
                    })
                events_count = len(entries)
            else:
                # For markdown format, provide basic info
                file_info = audit_manager.get_file_info()
                if file_info.get('exists'):
                    recent_events.append({
                        'event_id': 'See audit file',
                        'type': 'Multiple',
                        'severity': 'info',
                        'timestamp': file_info.get('last_modified', ''),
                        'summary': f"View {audit_manager.audit_file} for detailed audit trail"
                    })
                    events_count = file_info.get('size', 0) // 1000  # Rough estimate
            
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'status': {
                    'status': 'healthy',
                    'mode': 'DRY RUN' if agent.dry_run_mode else 'LIVE',
                    'modules': list(agent.modules_map.keys())
                },
                'recent_events': recent_events,
                'events_count': events_count
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'status': {
                    'status': 'error',
                    'mode': 'unknown',
                    'modules': []
                },
                'recent_events': [],
                'events_count': 0,
                'error': str(e)
            }
    
    @classmethod
    def render_dashboard(cls, agent, audit_manager) -> str:
        """Render HTML dashboard"""
        data = cls.generate_dashboard_data(agent, audit_manager)
        return render_template_string(cls.DASHBOARD_TEMPLATE, **data)
