---
name: Python Development Standards
description: This file defines the required Python style, typing, modeling, documentation, and linting standards for code written in this project.
---

This file defines the required Python coding standards for structure, typing, documentation, error handling, packaging, and mandatory `ruff` and `mypy` verification.

### 1. Formatting, Linting, and Type Checking
- All Python code must pass `ruff check`, `ruff format --check`, and `mypy` before work is considered complete
- Use `ruff format` as the formatting authority and `ruff check` as the primary lint gate
- Treat `mypy` as mandatory, not optional, for validating the typed public and internal code paths you change
- If a project defines wrapper commands such as `uv run ruff check .` or `uv run mypy .`, use those project-standard commands consistently
- Do not suppress `ruff` or `mypy` warnings unless the suppression is necessary, narrowly scoped, and justified in code

### 2. Style and Structure
- Write compact, readable code that prioritizes clarity over cleverness
- Follow PEP 8 with 4-space indentation and an 88-character line length compatible with Ruff formatting
- Group imports in the order stdlib, third-party, then local modules
- Keep modules focused and cohesive rather than mixing unrelated responsibilities
- Extract repeated logic into helpers instead of copying behavior across modules

### 3. Naming and Module Organization
- Use descriptive names for modules, functions, classes, methods, and variables
- Prefer nouns for data structures and verbs for operations
- Keep public module names stable and easy to understand for downstream users
- Use `__all__` to declare the intended public API for modules that expose reusable interfaces
- Split large files when they stop representing a single coherent responsibility

### 4. Type System
- Add type hints to all function signatures, parameters, return values, and significant variables
- Use modern built-in generics such as `list[str]` and `dict[str, int]`
- Use `X | None` instead of `Optional[X]`
- Use `Literal[...]` for small fixed string choices and enums for reusable closed sets of values
- Avoid `Any` unless it is truly unavoidable and the reason is explicit in code
- Write code that is understandable to both readers and static type checkers rather than relying on dynamic tricks

### 5. Data Modeling
- Use `pydantic.BaseModel` for data that crosses boundaries such as API I/O, configuration, LLM outputs, parsing, and inter-service contracts
- Use `pydantic.dataclasses.dataclass` for lightweight internal structures that still need validation
- Use stdlib `@dataclass` only for internal structures that do not need validation and benefit from simplicity or performance
- Use `Field(...)` for constraints, defaults, aliases, and descriptions on Pydantic models
- Prefer immutable value objects where appropriate, such as `model_config = ConfigDict(frozen=True)`
- Use validators for cross-field or field-level validation instead of scattering validation logic across callers

### 6. Enums and Constants
- Use `enum.Enum` or `enum.StrEnum` whenever a value is restricted to a fixed named set
- Prefer `StrEnum` when values must serialize naturally as strings in APIs, storage, or logs
- Reference enum members by name in logic rather than comparing raw string literals throughout the codebase
- Use module-level constants only for true constants, not as a substitute for structured types

### 7. Documentation
- Document every public function, class, and method with a Google-style docstring
- Include a one-line summary and add `Args`, `Returns`, and `Raises` sections when they apply
- Keep docstrings factual and concise; describe what the code guarantees, not line-by-line implementation detail
- Let type hints carry type information instead of duplicating it noisily in docstrings
- Internal helpers need docstrings when they are complex, reused, or easy to misuse

### 8. Error Handling
- Use `try` and `except` only when there is a clear recovery path, translation boundary, or cleanup requirement
- Catch specific exception types and never use bare `except:`
- Raise descriptive exceptions with enough context to debug the failure quickly
- Fail fast on invalid state instead of silently coercing bad inputs or hiding errors
- Keep exception handling close to the boundary where the error can be handled meaningfully

### 9. Functions and Logic
- Keep functions single-purpose and reasonably short
- Prefer pure functions when possible and isolate side effects at clear boundaries
- Use `pathlib.Path` instead of `os.path` for filesystem logic
- Use f-strings for string formatting
- Add inline comments only when intent would otherwise be non-obvious to a careful reader

### 10. Async and Concurrency Conventions
- Use `async def` only when the full call path and dependency model support asynchronous execution
- Do not mix blocking I/O into async code without an explicit boundary or offloading strategy
- Keep concurrency primitives localized and well named so ownership and lifecycle are obvious
- Prefer straightforward synchronous code when async or concurrency does not provide a real benefit
- Document concurrency assumptions where ordering, retries, idempotency, or cancellation matter

### 11. Project and Packaging Standards
- Assume `uv` as the default package manager and use `uv add <package>` for dependency changes unless the project defines a different wrapper command
- Declare dependencies in `pyproject.toml`
- Keep runtime and development dependencies clearly separated
- Avoid hidden import side effects in package initialization files
- Expose package-level APIs intentionally rather than by accident

### 12. Code Quality Bar
- Code is not done until formatting, linting, and type checks pass with `ruff` and `mypy`
- Remove debug `print()` statements before completion; use the `logging` module when runtime output is needed
- Keep comments, names, and types aligned so the code reads cleanly without extra explanation
- Prefer the simplest implementation that satisfies correctness, maintainability, and typing requirements

