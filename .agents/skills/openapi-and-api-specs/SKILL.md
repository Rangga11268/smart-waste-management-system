---
name: openapi-and-api-specs
description: OpenAPI 3.1 / Swagger specification design, API contract-first development, JSON Schema definitions, request/response validation, and client SDK generation. Use when writing API specs, designing REST interfaces, or enforcing API contract compliance.
---

# OpenAPI and API Specifications

Use this skill when defining contract-first API specifications (OpenAPI 3.0 / 3.1), designing endpoints, modeling reusable schemas, and maintaining API consistency.

## 1. Contract-First Philosophy
- **Single Source of Truth:** Write the OpenAPI specification before generating server stubs or client SDKs. The contract acts as the binding agreement between frontend, backend, and third-party consumers.
- **Specification Version:** Target OpenAPI 3.1.0 where possible to benefit from full JSON Schema 2020-12 alignment (including `type: ["string", "null"]`).

## 2. Resource & Path Design Conventions
- **RESTful Naming:**
  - Plural nouns for collections: `/api/v1/users`, `/api/v1/orders`.
  - Nested resources for natural relationships: `/api/v1/users/{userId}/addresses`.
  - Keep nesting depth $\le 2$. Use top-level endpoints with query filters for deeper relationships.
- **HTTP Methods:**
  - `GET`: Safe, idempotent read operations.
  - `POST`: Create a new resource or execute non-idempotent actions (`/checkout`).
  - `PUT`: Complete resource replacement (idempotent).
  - `PATCH`: Partial resource update.
  - `DELETE`: Resource removal (idempotent).

## 3. Reusable Components & Data Types
- **Avoid Inline Duplication:** Define domain models in `components.schemas` and reference them with `$ref: '#/components/schemas/UserResponse'`.
- **Consistent Error Structure:** Standardize on RFC 7807 (Problem Details for HTTP APIs) or a unified JSON envelope:
  ```yaml
  components:
    schemas:
      ApiError:
        type: object
        required: [code, message]
        properties:
          code:
            type: string
            example: "RESOURCE_NOT_FOUND"
          message:
            type: string
            example: "The requested item was not found."
          details:
            type: array
            items:
              type: string
  ```
- **Explicit Response Codes:** Always document standard responses: `200/201` for success, `400` for validation errors, `401/403` for authorization, `404` for not found, and `500` for server failures.

## 4. Linting and Validation
- Validate specs using standard linters (e.g., Spectral with `spectral:oas` ruleset).
- Ensure every path has descriptive `operationId`, `summary`, and tag assignments for clean generated SDK methods.
