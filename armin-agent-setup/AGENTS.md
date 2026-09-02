# AGENTS.md

This file is the top-level entry point for agent behavior in this repository. The files under `agent_templates/` are the normative standards and should be treated as the source of truth for workflow, safety, testing, documentation, refactoring, Git practice, and Python development.

## Standards Map

- Workflow orchestration: `agent_templates/workflow.md`
- Git and PR rules: `agent_templates/git.md`
- Safety and approval boundaries: `agent_templates/safety.md`
- Testing and quality checks: `agent_templates/testing.md`
- Python development standards: `agent_templates/python-style.md`
- Documentation standards: `agent_templates/documentation.md`
- Refactoring policy: `agent_templates/refactoring.md`
- Architecture principles: `agent_templates/architecture.md`
- Operational guardrails: `agent_templates/operational-guardrails.md`
- AI systems guidance: `agent_templates/ai.md`

## How To Apply This Set

- Start with `agent_templates/workflow.md` for execution flow, planning expectations, verification, and bug-fix behavior
- Apply `agent_templates/safety.md` before making risky, destructive, security-sensitive, or externally visible changes
- Apply `agent_templates/testing.md` when selecting validation depth, test scope, manual verification, and completion criteria
- Apply `agent_templates/python-style.md` to all Python code and treat `ruff`, `ruff format --check`, and `mypy` as mandatory where relevant
- Apply `agent_templates/git.md` for branch naming, commit format, PR rules, merge strategy, and release tagging
- Apply `agent_templates/documentation.md` when changing docs, docstrings, READMEs, reference pages, or publishing configuration
- Apply `agent_templates/refactoring.md` whenever a change is presented as no-behavior-change cleanup or structural improvement
- Apply `agent_templates/architecture.md`, `agent_templates/operational-guardrails.md`, and `agent_templates/ai.md` when the task touches those concerns; these files may still need project-specific expansion and should be filled in rather than ignored

## Repository-Wide Expectations

- Plan non-trivial work before implementation and keep the plan updated as the task evolves
- Prefer the smallest correct change that resolves the problem at the root cause
- Do not mark work complete without running the required validation or explicitly documenting the validation gap and residual risk
- Split behavior changes from refactors when combining them would make review, rollback, or verification harder
- Ask for approval before destructive, high-risk, security-sensitive, or ambiguous changes as defined in `agent_templates/safety.md`
- Keep commit and PR hygiene aligned with `agent_templates/git.md`

## Task Tracking

- Write plans to `tasks/todo.md` for non-trivial work
- Mark progress as work completes rather than waiting until the end
- Add a review or verification summary to `tasks/todo.md` when the task is done
- Update `tasks/lessons.md` after user corrections or repeated mistakes so the same error is less likely to recur

## Priority Order

- If two standards appear to conflict, follow safety first, then workflow and testing, then language or documentation conventions
- If a project-specific file under `agent_templates/` is still a placeholder, do not invent hidden policy; call out the gap explicitly and use the closest applicable existing standard

