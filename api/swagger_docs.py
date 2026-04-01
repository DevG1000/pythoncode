#!/usr/bin/env python3
"""
Swagger/OpenAPI Documentation for PythonCode API
Provides API documentation and interactive API explorer
"""

from flask_swagger_ui import get_swaggerui_blueprint
import json
import os

# Swagger configuration
SWAGGER_URL = '/api/docs'  # URL for accessing Swagger UI
API_URL = '/api/swagger.json'  # URL for Swagger JSON

# Swagger UI Blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "PythonCode API",
        'docExpansion': 'none',
        'operationsSorter': 'method'
    }
)

# Swagger/OpenAPI specification
SWAGGER_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "PythonCode API",
        "description": """
        PythonCode Project API Documentation
        
        This API provides services for:
        - User registration and email verification
        - System monitoring and health checks
        - Command execution and task management
        - Business card generation
        
        ## Authentication
        Currently using simple API key authentication (in development).
        
        ## Rate Limiting
        - 100 requests per minute per IP address
        - 1000 requests per hour per API key
        
        ## Error Codes
        - 400: Bad Request
        - 401: Unauthorized
        - 403: Forbidden
        - 404: Not Found
        - 422: Unprocessable Entity
        - 429: Too Many Requests
        - 500: Internal Server Error
        
        ## Contact
        - Project: https://github.com/yourusername/pythoncode
        - Issues: https://github.com/yourusername/pythoncode/issues
        """,
        "version": "1.0.0",
        "contact": {
            "name": "PythonCode Team",
            "url": "https://github.com/yourusername/pythoncode",
            "email": "team@pythoncode.example.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000",
            "description": "Development server"
        },
        {
            "url": "https://api.pythoncode.example.com",
            "description": "Production server"
        }
    ],
    "tags": [
        {
            "name": "health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "users",
            "description": "User registration and management"
        },
        {
            "name": "email",
            "description": "Email verification services"
        },
        {
            "name": "system",
            "description": "System monitoring and metrics"
        },
        {
            "name": "commands",
            "description": "Command execution and task management"
        }
    ],
    "paths": {
        "/health": {
            "get": {
                "tags": ["health"],
                "summary": "Health check",
                "description": "Check if the API is running and healthy",
                "responses": {
                    "200": {
                        "description": "API is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HealthResponse"
                                },
                                "example": {
                                    "status": "healthy",
                                    "timestamp": "2024-01-01T12:00:00Z",
                                    "version": "1.0.0",
                                    "services": {
                                        "database": "connected",
                                        "email": "ready",
                                        "memory": "normal"
                                    }
                                }
                            }
                        }
                    },
                    "503": {
                        "description": "API is unhealthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/register": {
            "post": {
                "tags": ["users"],
                "summary": "Register a new user",
                "description": "Register a new user with email verification",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserRegistration"
                            },
                            "example": {
                                "username": "john_doe",
                                "email": "john@example.com",
                                "password": "secure_password_123"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User registered successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/RegistrationResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "409": {
                        "description": "User already exists",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/verify-email/{token}": {
            "get": {
                "tags": ["email"],
                "summary": "Verify email address",
                "description": "Verify user's email address using verification token",
                "parameters": [
                    {
                        "name": "token",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        },
                        "description": "Email verification token"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Email verified successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/VerificationResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid or expired token",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Token not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/system/metrics": {
            "get": {
                "tags": ["system"],
                "summary": "Get system metrics",
                "description": "Get current system metrics (CPU, memory, disk, etc.)",
                "responses": {
                    "200": {
                        "description": "System metrics retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SystemMetrics"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized - API key required",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                },
                "security": [{"apiKey": []}]
            }
        },
        "/api/commands/execute": {
            "post": {
                "tags": ["commands"],
                "summary": "Execute a command",
                "description": "Execute a system command asynchronously",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CommandExecution"
                            },
                            "example": {
                                "command": "echo Hello World",
                                "timeout": 30,
                                "working_dir": "/tmp"
                            }
                        }
                    }
                },
                "responses": {
                    "202": {
                        "description": "Command accepted for execution",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CommandResponse"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid command or parameters",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized - API key required",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                },
                "security": [{"apiKey": []}]
            }
        },
        "/api/commands/tasks/{task_id}": {
            "get": {
                "tags": ["commands"],
                "summary": "Get task status",
                "description": "Get status of an asynchronous command execution task",
                "parameters": [
                    {
                        "name": "task_id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        },
                        "description": "Task ID"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Task status retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TaskStatus"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Task not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["healthy", "degraded", "unhealthy"],
                        "description": "Overall health status"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Current timestamp"
                    },
                    "version": {
                        "type": "string",
                        "description": "API version"
                    },
                    "services": {
                        "type": "object",
                        "description": "Status of individual services",
                        "additionalProperties": {
                            "type": "string"
                        }
                    }
                },
                "required": ["status", "timestamp", "version"]
            },
            "UserRegistration": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 50,
                        "description": "Username (3-50 characters)"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Email address"
                    },
                    "password": {
                        "type": "string",
                        "minLength": 8,
                        "description": "Password (minimum 8 characters)"
                    }
                },
                "required": ["username", "email", "password"]
            },
            "RegistrationResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Success message"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "User ID"
                    },
                    "verification_sent": {
                        "type": "boolean",
                        "description": "Whether verification email was sent"
                    },
                    "verification_token": {
                        "type": "string",
                        "description": "Email verification token (for testing)"
                    }
                },
                "required": ["message", "user_id"]
            },
            "VerificationResponse": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Success message"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "User ID"
                    },
                    "email": {
                        "type": "string",
                        "description": "Verified email address"
                    },
                    "verified_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Verification timestamp"
                    }
                },
                "required": ["message", "user_id", "email"]
            },
            "SystemMetrics": {
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Metrics timestamp"
                    },
                    "cpu_percent": {
                        "type": "number",
                        "format": "float",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "CPU usage percentage"
                    },
                    "memory_percent": {
                        "type": "number",
                        "format": "float",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Memory usage percentage"
                    },
                    "disk_percent": {
                        "type": "number",
                        "format": "float",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Disk usage percentage"
                    },
                    "network_sent_mb": {
                        "type": "number",
                        "format": "float",
                        "description": "Network data sent (MB)"
                    },
                    "network_recv_mb": {
                        "type": "number",
                        "format": "float",
                        "description": "Network data received (MB)"
                    },
                    "processes_running": {
                        "type": "integer",
                        "description": "Number of running processes"
                    },
                    "system_uptime_seconds": {
                        "type": "number",
                        "format": "float",
                        "description": "System uptime in seconds"
                    }
                },
                "required": ["timestamp", "cpu_percent", "memory_percent", "disk_percent"]
            },
            "CommandExecution": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3600,
                        "default": 30,
                        "description": "Timeout in seconds (1-3600)"
                    },
                    "working_dir": {
                        "type": "string",
                        "default": ".",
                        "description": "Working directory for command execution"
                    },
                    "async": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to execute asynchronously"
                    }
                },
                "required": ["command"]
            },
            "CommandResponse": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID for tracking execution"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["accepted", "queued", "running"],
                        "description": "Initial task status"
                    },
                    "message": {
                        "type": "string",
                        "description": "Status message"
                    },
                    "estimated_completion": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Estimated completion time"
                    }
                },
                "required": ["task_id", "status", "message"]
            },
            "TaskStatus": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID"
                    },
                    "command": {
                        "type": "string",
                        "description": "Executed command"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "running", "completed", "failed", "timeout"],
                        "description": "Current task status"
                    },
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Task start time"
                    },
                    "end_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Task end time (if completed)"
                    },
                    "output": {
                        "type": "string",
                        "description": "Command output (if completed)"
                    },
                    "return_code": {
                        "type": "integer",
                        "description": "Command return code (if completed)"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message (if failed)"
                    }
                },
                "required": ["task_id", "command", "status", "start_time"]
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "code": {
                        "type": "string",
                        "description": "Error code"
                    },
                    "details": {
                        "type": "object",
                        "description": "Additional error details"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Error timestamp"
                    }
                },
                "required": ["error", "code", "timestamp"]
            }
        },
        "securitySchemes": {
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API key for authentication"
            }
        }
    },
    "externalDocs": {
        "description": "PythonCode Project Documentation",
        "url": "https://github.com/yourusername/pythoncode/wiki"
    }
}

def setup_swagger(app):
    """
    Setup Swagger/OpenAPI documentation for Flask app
    
    Args:
        app: Flask application instance
    """
    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Add Swagger JSON endpoint
    @app.route(API_URL)
    def swagger_json():
        return json.dumps(SWAGGER_SPEC, indent=2)
    
    # Add Swagger UI redirect
    @app.route('/docs')
    @app.route('/api')
    def redirect_to_swagger():
        from flask import redirect
        return redirect(SWAGGER_URL)
    
    print(f"Swagger UI available at: http://localhost:5000{SWAGGER_URL}")
    print(f"OpenAPI spec available at: http://localhost:5000{API_URL}")

def generate_openapi_spec(output_file="openapi.json"):
    """
    Generate OpenAPI specification file
    
    Args:
        output_file: Output file path
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(SWAGGER_SPEC, f, indent=2, ensure_ascii=False)
    
    print(f"OpenAPI specification saved to: {output_file}")
    return output_file

def validate_openapi_spec():
    """
    Validate OpenAPI specification
    """
    try:
        # Try to import openapi-spec-validator
        from openapi_spec_validator import validate_spec
        
        validate_spec(SWAGGER_SPEC)
        print("OpenAPI specification is valid!")
        return True
        
    except ImportError:
        print("openapi-spec-validator not installed. Skipping validation.")
        print("Install with: pip install openapi-spec-validator")
        return None
    except Exception as e:
        print(f"OpenAPI specification validation failed: {e}")
        return False

if __name__ == "__main__":
    # Generate OpenAPI spec file
    spec_file = generate_openapi_spec()
    
    # Validate the spec
    validate_openapi_spec()
    
    print(f"\nOpenAPI documentation generated successfully!")
    print(f"File: {spec_file}")
    print(f"Use with Flask: from api.swagger_docs import setup_swagger")
    print(f"Then call: setup_swagger(app)")