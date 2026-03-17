---
name: Refactoring Policy
description: This file defines the allowed scope, verification depth, documentation expectations, and review boundaries for no-behavior-change refactors.
---

This file defines the required refactoring rules for behavior-preserving changes, including scope limits, verification expectations, documentation impact, and when refactors must be split from other work.

### 1. Definition of a Pure Refactor
- A pure refactor changes structure, readability, maintainability, or internal design without intentionally changing externally observable behavior
- Pure refactors may reorganize code, rename internal symbols, extract helpers, simplify control flow, or improve type structure without changing public contracts
- A change is not a pure refactor if it alters outputs, side effects, persistence behavior, timing guarantees, public APIs, schema semantics, or operational workflows
- If behavior change is intended or even likely, classify the work as a functional change rather than a refactor

### 2. Allowed Scope for Pure Refactors
- Keep pure refactors narrowly scoped to one logical area, subsystem, or maintenance objective
- Prefer local refactors that improve clarity or remove duplication over broad codebase churn
- Internal renames, helper extraction, dead code removal, import cleanup, module reshaping, and type clarifications are allowed when behavior remains stable
- Refactors may improve test structure when the tests still validate the same product behavior
- Avoid mixing opportunistic cleanup across unrelated modules into the same refactor

### 3. Prohibited or High-Risk Refactor Patterns
- Do not bundle behavior changes, feature work, fixes, dependency upgrades, or schema changes into a refactor-only change
- Do not relabel risky architectural rewrites as refactors just because the intended behavior is unchanged
- Do not change public API contracts, auth rules, persistence semantics, or deployment behavior without treating the work as more than a pure refactor
- Do not remove tests, logging, safeguards, or validation logic unless their removal is proven behavior-preserving and covered by verification
- If rollback or review becomes materially harder because of the change size, the refactor is too broad

### 4. Verification Depth
- Pure refactors still require real verification; no-behavior-change claims must be proven, not assumed
- Run the relevant lint, format, type-check, and automated test suite for the affected area at minimum
- For Python projects, this normally includes `ruff check`, `ruff format --check`, `mypy`, and the relevant `pytest` coverage for the changed surface
- Increase verification depth when the refactor touches persistence, async flows, concurrency, public interfaces, or shared libraries
- Compare before-and-after behavior when the refactor touches logic that is difficult to reason about from tests alone

### 5. Testing Expectations for Refactors
- Existing tests must continue to pass after the refactor
- Add or update tests only when doing so is necessary to prove behavior preservation, stabilize weak coverage, or support safe restructuring
- If the refactor exposes missing regression or integration coverage in the affected area, strengthen the tests before or alongside the refactor
- Test cleanups are allowed when they improve clarity and keep the same behavioral assertions intact
- Never use a refactor as a reason to weaken meaningful coverage

### 6. Documentation Requirements for Refactors
- Documentation changes are only required when the refactor changes public names, developer workflows, repository structure, or other documented navigation paths
- Internal-only refactors usually do not require user-facing documentation updates
- If module paths, exported symbols, or examples change, update the relevant docs, references, or internal guides
- Keep commit messages and PR descriptions explicit that the change is intended to preserve behavior

### 7. Conditions That Require Splitting Into Separate PRs
- Split the work when refactoring and behavior changes are both present
- Split the work when a dependency upgrade, schema migration, infra change, or public API change is involved
- Split the work when mechanical renames or formatting churn would hide a smaller logic change
- Split the work when reviewers would need different expertise for different parts of the change
- Split the work when rollback needs to remain simple and low risk

### 8. Review Expectations for Refactors
- Reviews should focus on whether behavior is truly preserved, whether the design is genuinely improved, and whether the verification depth matches the risk
- Refactor PRs should explain the motivation, scope, non-goals, and evidence that behavior is unchanged
- Reviewers should challenge large or ambiguous refactors that combine too many concerns
- If a refactor makes the code harder to follow, harder to test, or harder to roll back, it should not be approved as an improvement

### 9. Safety and Escalation Boundaries
- Ask first before refactors that touch production configuration, database structure, public contracts, or security-sensitive flows
- Escalate when it becomes clear that the refactor cannot be proven behavior-preserving with the available validation surface
- If the refactor reveals an unrelated bug or design flaw, document it and decide explicitly whether it belongs in a separate change
- When in doubt, reduce scope rather than broadening the refactor under the same label

### 10. Completion Standard
- A refactor is not complete until required verification passes and the no-behavior-change claim is supported by evidence
- The final summary must state that the change was a refactor, what scope it covered, and how behavior preservation was verified
- If any area could not be validated adequately, the refactor should not be presented as low risk without clearly stating the gap
