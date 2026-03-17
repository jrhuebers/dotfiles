---
name: Git and PR Rules
description: This file defines branch naming, commit format, pull request, review, merge, and release rules for work that follows Conventional Commits.
---

### 1. Branch Naming
- Branches must follow the pattern `<type>/<short-kebab-description>`
- Allowed branch types are `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, and `revert`
- Keep branch names short, specific, and scoped to one logical change
- Example branch names:
  - `feat/user-authentication`
  - `fix/login-redirect-loop`
  - `chore/update-dependencies`
  - `docs/api-reference`

### 2. Commit Message Format
- Every commit must follow the Conventional Commits structure `<type>[optional scope]: <description>`
- A commit body may follow after one blank line when additional context is needed
- Footers may follow after one blank line using formats such as `Refs: #42` or `BREAKING CHANGE: <description>`
- The description must be short, imperative, and must not end with a period
- A scope may be added in parentheses, for example `fix(auth): handle token expiry`
- Breaking changes must be marked with `!` before the colon, a `BREAKING CHANGE:` footer, or both
- `BREAKING CHANGE` must be uppercase when used as a footer token
- Use `feat` for new functionality, `fix` for bug fixes, and the remaining allowed types only when they accurately describe the change

### 3. Commit Examples
```text
feat(auth): add OAuth2 login flow

fix: prevent race condition in request queue

Introduce a request id and reference to the latest request.

Refs: #42

docs: update setup guide for Windows

feat(api)!: remove deprecated v1 routes

BREAKING CHANGE: all /v1/* endpoints have been removed; migrate to /v2/*
```

### 4. Pull Request Requirements
- The PR title must follow Conventional Commits format because it becomes the squash-merge commit on protected branches
- All commits in the PR must comply with the same format
- Breaking changes must be clearly flagged in the commit history and documented in the PR description
- Relevant tests must be added or updated
- Documentation must be updated when public APIs, user-facing behavior, setup, or operational guidance changes
- A PR must contain one logical change only and should not bundle unrelated work
- Required CI checks must pass before review is considered complete
- If the PR targets a release branch, changelog impact must be noted

### 5. Review and Approval Expectations
- At least one approving review is required before merge
- Two approving reviews are required for changes targeting `main`, release branches, or any PR marked as breaking
- Reviewers must verify that commit types and scopes accurately describe the change
- Reviewers must verify that breaking-change markers and footers are present and descriptive when applicable
- Authors must resolve all blocking review comments before merge
- Non-blocking comments may be addressed before or after merge at maintainer discretion
- Stale PRs with no activity for 14 days may be closed with a `stale` label

### 6. Merge Strategy
- Use squash merge for `main`; the final squash commit message must comply with Conventional Commits
- Use merge commits for `develop` when preserving integration history is valuable
- Use cherry-pick for release fixes and limit those changes to `fix` or `revert` commits
- Revert commits should use the `revert` type and should include a `Refs:` footer pointing to the reverted SHA values

### 7. Release Tagging and Versioning
- Releases must follow Semantic Versioning and use tags in the format `vMAJOR.MINOR.PATCH`
- A breaking change indicated by `!` or `BREAKING CHANGE:` triggers a major version bump
- A `feat` commit triggers a minor version bump
- A `fix`, `perf`, or other non-breaking change triggers a patch version bump
- Each tagged release must include a `CHANGELOG.md` entry generated manually or by release tooling such as `conventional-changelog` or `release-please`
- Pre-release tags may use suffixes such as `v1.0.0-alpha.1` or `v2.0.0-rc.2`

### 8. Maintainer Checks Before Merge
- Confirm the branch and PR title follow the required naming conventions
- Confirm the PR contains one logical change with no unrelated commits
- Confirm tests, CI, and required documentation updates are complete
- Confirm release notes or changelog impact are addressed when relevant
- Confirm the final merge method preserves the intended history and commit semantics