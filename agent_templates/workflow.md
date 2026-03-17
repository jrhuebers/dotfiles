---
name: Workflow Orchestration
description: This file defines the required workflow for planning, subagent use, self-correction verification, and autonomous bug fixing before work can be considered complete.
---

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Re-plan when scope changes, a core assumption fails, validation contradicts the plan, or the fix requires broader impact than expected
- Do not start implementation until success criteria and verification steps are explicit

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution
- Require subagents for broad codebase exploration, parallel fact gathering, or isolated research threads that would otherwise clutter the main task flow
- Treat subagent output as input to verify, not as final truth; confirm critical findings before acting on them

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project
- Record only reusable lessons that change future behavior; avoid noisy task-specific notes

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness
- Capture the exact commands, checks, and artifacts used to verify the change
- If validation cannot be completed, do not mark the task done without explicitly stating the gap, reason, and residual risk

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it
- Split refactors from behavior changes when combining them would make review or rollback harder

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Start from the failing symptom, identify the root cause, add or update regression coverage, then verify against the original failure mode
- Escalate only when requirements conflict, the environment blocks verification, or the fix would require an unapproved scope change