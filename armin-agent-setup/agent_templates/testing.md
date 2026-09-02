---
name: Testing and Quality Checks
description: This file defines the required test levels, quality gates, validation commands, and pre-merge expectations for changes made in this project.
---

This file defines the required testing and quality standards for linting, type checking, automated tests, pre-merge validation, and flaky test handling.

### 1. Canonical Validation Commands
- Run the project-standard lint, format-check, type-check, and test commands for every meaningful code change
- For Python projects, default validation includes `ruff check`, `ruff format --check`, `mypy`, and the relevant `pytest` command unless the repository defines stricter wrappers
- Prefer the repository’s canonical wrapper commands, such as `uv run ruff check .`, `uv run mypy .`, and `uv run pytest`, over ad hoc equivalents
- Use the narrowest command that still validates the change honestly during iteration, then run the broader required checks before completion
- Record the exact commands used when summarizing verification

### 2. Unit, Integration, and End-to-End Expectations
- Add or update unit tests for logic that can be validated in isolation
- Add or update integration tests when the change crosses module, service, database, filesystem, or network boundaries
- Add or update end-to-end tests for user-visible workflows, cross-service behavior, or release-critical paths when such tests exist in the repository
- Bug fixes should include regression coverage whenever the failure can be reproduced in a test
- New features should ship with tests that validate the intended behavior, not just the happy path implementation details

### 3. Test Scope Selection
- Choose the smallest meaningful test scope first, then add broader coverage when the risk profile requires it
- Prefer fast unit coverage for pure logic, but do not pretend unit tests are sufficient when the bug lives at an integration boundary
- When a change affects persistence, schema behavior, async flows, background jobs, or API contracts, integration coverage is usually required
- When a change affects onboarding, deployment, CLI behavior, or visible workflows, include manual verification steps if automated end-to-end coverage is missing
- If a change is too risky to validate with the available test surface, call out the gap explicitly and do not overclaim confidence

### 4. AI Evaluation Requirements
- If the project includes LLM, ranking, recommendation, search, or model-driven behavior, run the repository’s defined eval suite when prompts, models, retrieval logic, or decision thresholds change
- Treat eval regressions as real regressions even when unit tests still pass
- Document which prompts, datasets, metrics, or benchmark slices were used for validation
- If formal eval infrastructure does not exist, use representative fixtures or benchmark prompts and state the limitation clearly
- Do not claim model quality improvements without evidence from repeatable evaluation

### 5. Minimum Pre-Merge Gates
- Linting must pass
- Formatting checks must pass
- Type checking must pass
- Relevant automated tests must pass
- Required manual verification must be completed for user-visible or operationally sensitive changes
- New or changed behavior must be covered by tests or an explicit justification must be provided for why coverage is not feasible
- Documentation must be updated when behavior, setup, or operations change

### 6. Regression Testing Policy
- Reproduce bugs before fixing them whenever possible
- Add a regression test that fails before the fix and passes after the fix whenever the bug is testable
- Verify that the fix does not break adjacent behaviors, not just the reported symptom
- When the original bug is not directly testable, add the closest stable automated check and document the remaining manual validation
- Prefer stable regression coverage at the boundary where the bug actually occurred

### 7. Manual Verification Standards
- Use manual verification for UI changes, environment-specific behavior, deployment flows, and scenarios that are not realistically covered by automation
- Write manual verification steps in a way another engineer could repeat them
- Record what was checked, where it was checked, and what the observed result was
- Do not substitute vague statements like "tested locally" for actual verification detail
- If manual validation could not be completed, state that explicitly with the reason and residual risk

### 8. Flaky Test Handling
- Do not ignore flaky tests or treat intermittent failures as noise
- If a test is flaky, identify whether the issue is timing, shared state, data coupling, environment drift, or a real product bug
- Stabilize the test before relying on it as a gate whenever feasible
- If a flaky test must be quarantined temporarily, document the reason, owner, and exit criteria for restoring it
- Never use a flaky test as proof of correctness without addressing its instability

### 9. Quality of Test Code
- Keep test code readable, deterministic, and focused on behavior rather than implementation trivia
- Prefer explicit fixtures and setup over hidden magic in shared helpers
- Use representative test data and name cases so failures are easy to interpret
- Avoid overly brittle assertions that block refactoring without protecting real behavior
- Keep tests fast where possible, but do not sacrifice meaningful coverage for speed alone

### 10. Completion Standard
- Work is not complete until the required lint, type-check, and test gates have passed or any validation gap has been explicitly documented
- The final summary must include what was validated, what could not be validated, and any remaining risks
- If verification results conflict with the intended change, stop and resolve the discrepancy before marking the task done
