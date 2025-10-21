#!/usr/bin/env python3
"""
OpenAPI specification generator for CLI Orchestrator API.

Generates OpenAPI 3.x specification from Pydantic models and route definitions.
Supports both FastAPI-based and manual route definitions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from pydantic import BaseModel
except ImportError:
    print("Warning: pydantic not installed, using basic type hints")
    BaseModel = object  # type: ignore


class OpenAPIGenerator:
    """Generate OpenAPI specification for CLI Orchestrator API."""

    def __init__(self, title: str = "CLI Orchestrator API", version: str = "1.0.0"):
        self.spec: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {
                "title": title,
                "version": version,
                "description": "Schema-driven CLI orchestrator for deterministic workflows and AI integration",
                "contact": {
                    "name": "CLI Orchestrator",
                    "url": "https://github.com/DICKY1987/CLI_RESTART",
                },
                "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Development server"},
                {"url": "http://localhost:5055", "description": "Local stack server"},
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key for authentication",
                    },
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT bearer token authentication",
                    },
                },
            },
            "tags": [
                {
                    "name": "workflows",
                    "description": "Workflow execution and management",
                },
                {"name": "adapters", "description": "Adapter operations and queries"},
                {"name": "schemas", "description": "Schema validation and management"},
                {"name": "cost", "description": "Cost tracking and budget management"},
                {"name": "artifacts", "description": "Artifact storage and retrieval"},
                {"name": "health", "description": "Health checks and system status"},
            ],
        }

    def add_workflow_endpoints(self) -> None:
        """Add workflow-related API endpoints."""
        self.spec["paths"]["/api/v1/workflows"] = {
            "get": {
                "tags": ["workflows"],
                "summary": "List workflows",
                "description": "Get list of available workflow definitions",
                "operationId": "listWorkflows",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/WorkflowInfo"},
                                }
                            }
                        },
                    }
                },
                "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
            },
            "post": {
                "tags": ["workflows"],
                "summary": "Execute workflow",
                "description": "Start a new workflow execution",
                "operationId": "executeWorkflow",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/WorkflowRequest"}
                        }
                    },
                },
                "responses": {
                    "202": {
                        "description": "Workflow execution started",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WorkflowExecution"
                                }
                            }
                        },
                    },
                    "400": {"description": "Invalid workflow definition"},
                    "401": {"description": "Unauthorized"},
                },
                "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
            },
        }

        self.spec["paths"]["/api/v1/workflows/{workflow_id}"] = {
            "get": {
                "tags": ["workflows"],
                "summary": "Get workflow status",
                "description": "Get the current status of a workflow execution",
                "operationId": "getWorkflowStatus",
                "parameters": [
                    {
                        "name": "workflow_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                        "description": "Workflow execution ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Workflow status",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WorkflowExecution"
                                }
                            }
                        },
                    },
                    "404": {"description": "Workflow not found"},
                },
                "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
            },
            "delete": {
                "tags": ["workflows"],
                "summary": "Cancel workflow",
                "description": "Cancel a running workflow execution",
                "operationId": "cancelWorkflow",
                "parameters": [
                    {
                        "name": "workflow_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    }
                ],
                "responses": {
                    "200": {"description": "Workflow cancelled successfully"},
                    "404": {"description": "Workflow not found"},
                    "409": {"description": "Workflow already completed"},
                },
                "security": [{"ApiKeyAuth": []}, {"BearerAuth": []}],
            },
        }

    def add_adapter_endpoints(self) -> None:
        """Add adapter-related API endpoints."""
        self.spec["paths"]["/api/v1/adapters"] = {
            "get": {
                "tags": ["adapters"],
                "summary": "List adapters",
                "description": "Get list of available adapters",
                "operationId": "listAdapters",
                "responses": {
                    "200": {
                        "description": "List of adapters",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/AdapterInfo"},
                                }
                            }
                        },
                    }
                },
            }
        }

    def add_health_endpoints(self) -> None:
        """Add health check endpoints."""
        self.spec["paths"]["/health"] = {
            "get": {
                "tags": ["health"],
                "summary": "Health check",
                "description": "Check API health status",
                "operationId": "healthCheck",
                "responses": {
                    "200": {
                        "description": "Healthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthStatus"}
                            }
                        },
                    }
                },
            }
        }

    def add_schema_definitions(self) -> None:
        """Add common schema definitions."""
        self.spec["components"]["schemas"].update(
            {
                "WorkflowInfo": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "path": {"type": "string"},
                        "description": {"type": "string"},
                        "version": {"type": "string"},
                    },
                    "required": ["name", "path"],
                },
                "WorkflowRequest": {
                    "type": "object",
                    "properties": {
                        "workflow_path": {
                            "type": "string",
                            "description": "Path to workflow YAML file",
                        },
                        "inputs": {
                            "type": "object",
                            "description": "Workflow input parameters",
                        },
                        "dry_run": {
                            "type": "boolean",
                            "default": False,
                            "description": "Run in dry-run mode",
                        },
                    },
                    "required": ["workflow_path"],
                },
                "WorkflowExecution": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "workflow_name": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "running", "completed", "failed", "cancelled"],
                        },
                        "started_at": {"type": "string", "format": "date-time"},
                        "completed_at": {
                            "type": "string",
                            "format": "date-time",
                            "nullable": True,
                        },
                        "current_step": {"type": "string"},
                        "total_steps": {"type": "integer"},
                        "artifacts": {"type": "array", "items": {"type": "string"}},
                        "cost": {"$ref": "#/components/schemas/CostSummary"},
                    },
                    "required": ["id", "workflow_name", "status"],
                },
                "AdapterInfo": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "CostSummary": {
                    "type": "object",
                    "properties": {
                        "total_tokens": {"type": "integer"},
                        "total_cost": {"type": "number", "format": "float"},
                        "currency": {"type": "string", "default": "USD"},
                    },
                },
                "HealthStatus": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
                        "version": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                },
            }
        )

    def generate(self) -> dict[str, Any]:
        """Generate the complete OpenAPI specification."""
        self.add_workflow_endpoints()
        self.add_adapter_endpoints()
        self.add_health_endpoints()
        self.add_schema_definitions()
        return self.spec

    def save_to_file(self, output_path: Path) -> None:
        """Save the OpenAPI specification to a JSON file."""
        spec = self.generate()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        print(f"OpenAPI specification saved to: {output_path}")


def main() -> int:
    """Main entry point."""
    root = Path(__file__).resolve().parents[2]
    output_path = root / "specs" / "openapi" / "cli-orchestrator-api.json"

    generator = OpenAPIGenerator(title="CLI Orchestrator API", version="1.0.0")
    generator.save_to_file(output_path)

    # Also save as YAML if PyYAML is available
    try:
        import yaml

        yaml_path = output_path.with_suffix(".yaml")
        spec = generator.generate()
        with yaml_path.open("w", encoding="utf-8") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        print(f"OpenAPI specification also saved as: {yaml_path}")
    except ImportError:
        print("PyYAML not installed, skipping YAML output")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
