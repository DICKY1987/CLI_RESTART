# Architecture Boundaries

This document outlines the architectural boundaries and rules for the CLI Orchestrator project. These rules are enforced by the architecture tests in `tests/test_architecture.py`.

## 1. Layered Architecture

The project follows a layered architecture with the following key layers:

- **Domain Layer**: Contains the core business logic and domain models. This layer is the heart of the application and should be independent of any specific technology or framework.
- **Adapters Layer**: Contains the infrastructure code that connects the domain layer to the outside world (e.g., databases, APIs, file system).
- **Application Layer**: Coordinates the interaction between the domain and adapter layers.

## 2. Dependency Rule

The golden rule of our architecture is:

**Dependencies can only point inwards.**

This means:

- The **Domain Layer** must NOT depend on any other layer.
- The **Adapters Layer** can depend on the **Domain Layer**, but not on other adapters.
- The **Application Layer** can depend on both the **Domain** and **Adapters** layers.

### Allowed Imports

- `adapters` can import from `domain`
- `app` can import from `domain` and `adapters`

### Forbidden Imports

- `domain` **cannot** import from `adapters`
- `domain` **cannot** import from `app`
- `adapters` **cannot** import from `app`

## 3. Module Boundaries

- **`src/cli_multi_rapid/domain`**: This is the domain layer. It should contain only pure business logic and have no knowledge of the outside world.
- **`src/cli_multi_rapid/adapters`**: This is the adapters layer. It contains all the code that interacts with external systems.

## 4. File Size Limits

To promote single responsibility and maintainability, all Python files in the `src/cli_multi_rapid` directory should be under **400 lines of code**.

## 5. Circular Dependencies

Circular dependencies between modules are strictly forbidden. The `test_no_circular_imports` test enforces this rule.
