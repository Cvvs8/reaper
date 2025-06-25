"""
API schema validation using JSON Schema
"""
import json
from typing import Dict, Any, Tuple
from jsonschema import validate, ValidationError, Draft7Validator


class APISchemaValidator:
    """Validates API requests against JSON schemas"""
    
    # Schema for SaaS access events
    SAAS_ACCESS_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["unauthorized_saas_access"]
            },
            "event_id": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9-_]+$",
                "minLength": 1
            },
            "user": {
                "type": "string",
                "format": "email",
                "minLength": 1
            },
            "source": {
                "type": "string",
                "enum": ["slack", "notion", "github", "jira", "confluence"]
            },
            "timestamp": {
                "type": "string",
                "format": "date-time"
            },
            "severity": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"]
            }
        },
        "required": ["type", "event_id", "user", "source", "timestamp"],
        "additionalProperties": True
    }
    
    # Schema for S3 bucket events
    S3_BUCKET_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["open_s3_bucket"]
            },
            "event_id": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9-_]+$",
                "minLength": 1
            },
            "bucket_name": {
                "type": "string",
                "pattern": "^[a-z0-9.-]+$",
                "minLength": 3,
                "maxLength": 63
            },
            "region": {
                "type": "string",
                "pattern": "^[a-z0-9-]+$"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time"
            },
            "severity": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"]
            }
        },
        "required": ["type", "event_id", "bucket_name", "region", "timestamp"],
        "additionalProperties": True
    }
    
    # Base event schema
    BASE_EVENT_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string"
            },
            "event_id": {
                "type": "string",
                "minLength": 1
            },
            "timestamp": {
                "type": "string"
            }
        },
        "required": ["type", "event_id"],
        "additionalProperties": True
    }
    
    @classmethod
    def validate_event(cls, event_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate event data against appropriate schema
        Returns (is_valid, error_message)
        """
        try:
            # First validate against base schema
            validator = Draft7Validator(cls.BASE_EVENT_SCHEMA)
            validator.validate(event_data)
            
            # Then validate against specific event type schema
            event_type = event_data.get("type")
            
            if event_type == "unauthorized_saas_access":
                validator = Draft7Validator(cls.SAAS_ACCESS_SCHEMA)
                validator.validate(event_data)
            elif event_type == "open_s3_bucket":
                validator = Draft7Validator(cls.S3_BUCKET_SCHEMA)
                validator.validate(event_data)
            else:
                return False, f"Unknown event type: {event_type}"
            
            return True, "Validation successful"
            
        except ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @classmethod
    def get_openapi_spec(cls) -> Dict[str, Any]:
        """Generate OpenAPI specification for the API"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Reaper Agent API",
                "description": "Security automation agent for processing security events",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "http://localhost:5001",
                    "description": "Development server"
                }
            ],
            "paths": {
                "/": {
                    "get": {
                        "summary": "Health check",
                        "description": "Get agent status and configuration",
                        "responses": {
                            "200": {
                                "description": "Agent status",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "service": {"type": "string"},
                                                "mode": {"type": "string"},
                                                "modules": {"type": "array"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/event": {
                    "post": {
                        "summary": "Process security event",
                        "description": "Submit a security event for processing",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "oneOf": [
                                            cls.SAAS_ACCESS_SCHEMA,
                                            cls.S3_BUCKET_SCHEMA
                                        ]
                                    },
                                    "examples": {
                                        "saas_access": {
                                            "value": {
                                                "type": "unauthorized_saas_access",
                                                "event_id": "evt-001",
                                                "user": "user@company.com",
                                                "source": "slack",
                                                "timestamp": "2024-01-01T12:00:00Z",
                                                "severity": "high"
                                            }
                                        },
                                        "s3_bucket": {
                                            "value": {
                                                "type": "open_s3_bucket",
                                                "event_id": "evt-002",
                                                "bucket_name": "my-bucket",
                                                "region": "us-east-1",
                                                "timestamp": "2024-01-01T12:00:00Z",
                                                "severity": "critical"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Event processed successfully"
                            },
                            "400": {
                                "description": "Invalid event data"
                            },
                            "500": {
                                "description": "Processing error"
                            }
                        }
                    }
                },
                "/config": {
                    "get": {
                        "summary": "Get configuration",
                        "description": "Retrieve current agent configuration",
                        "responses": {
                            "200": {
                                "description": "Configuration data"
                            }
                        }
                    }
                },
                "/toggle-dry-run": {
                    "post": {
                        "summary": "Toggle dry run mode",
                        "description": "Switch between live and dry run modes",
                        "responses": {
                            "200": {
                                "description": "Mode toggled successfully"
                            }
                        }
                    }
                },
                "/audit": {
                    "get": {
                        "summary": "Get audit trail",
                        "description": "Retrieve audit trail information",
                        "responses": {
                            "200": {
                                "description": "Audit trail data"
                            }
                        }
                    }
                },
                "/openapi.json": {
                    "get": {
                        "summary": "OpenAPI specification",
                        "description": "Get the OpenAPI specification for this API",
                        "responses": {
                            "200": {
                                "description": "OpenAPI spec",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
