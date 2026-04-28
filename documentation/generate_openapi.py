import json
import re
from pathlib import Path

from app.main import app


OUTPUT_PATH = Path("documentation/openapi.json")


def flask_path_to_openapi(path: str) -> str:
    # /users/<int:user_id> -> /users/{user_id}
    path = re.sub(r"<(?:[^:<>]+:)?([^<>]+)>", r"{\1}", path)
    return path


def infer_tag(rule: str) -> str:
    parts = [p for p in rule.split("/") if p]
    if not parts:
        return "default"
    return parts[0]


def make_operation(method: str, path: str, endpoint: str) -> dict:
    operation = {
        "tags": [infer_tag(path)],
        "summary": f"{method} {path}",
        "operationId": endpoint.replace(".", "_") + "_" + method.lower(),
        "responses": {
            "200": {"description": "Success"},
            "400": {"description": "Bad request"},
            "401": {"description": "Unauthorized"},
            "403": {"description": "Forbidden"},
            "404": {"description": "Not found"},
            "500": {"description": "Server error"},
        },
    }

    if method in {"POST", "PUT", "PATCH"}:
        operation["parameters"] = [
            {
                "name": "body",
                "in": "body",
                "required": False,
                "schema": {
                    "type": "object",
                    "additionalProperties": True,
                },
            }
        ]

    return operation


def main():
    spec = {
        "swagger": "2.0",
        "info": {
            "title": "BetaFit Backend API",
            "description": "Auto-generated API documentation from Flask routes.",
            "version": "1.0.0",
        },
        "host": "localhost:8080",
        "basePath": "/",
        "schemes": ["http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {},
        "definitions": {},
    }

    ignored_endpoints = {
        "static",
        "flasgger.static",
        "flasgger.apidocs",
        "flasgger.apispec_1",
        "flasgger.oauth_redirect",
    }

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if rule.endpoint in ignored_endpoints:
            continue

        methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
        if not methods:
            continue

        openapi_path = flask_path_to_openapi(rule.rule)

        if openapi_path not in spec["paths"]:
            spec["paths"][openapi_path] = {}

        for method in methods:
            spec["paths"][openapi_path][method.lower()] = make_operation(
                method=method,
                path=openapi_path,
                endpoint=rule.endpoint,
            )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    print(f"Wrote {OUTPUT_PATH}")
    print(f"Documented {len(spec['paths'])} paths")


if __name__ == "__main__":
    main()