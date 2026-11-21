---
name: skill-improvement-audit
description: >-
  Run a clean-room Stages 1-7 EnvelopeFollower tutorial replay using
  tutorial-test-drive combined with read-only per-prompt /agy-customizations
  retrospectives to generate a verified, deduplicated SkillImprovementAuditReport.md.
  Use when asked to audit installed hardware skills across a tutorial run,
  collect per-prompt skill feedback, or produce a Skill Improvement Audit Report.
---

# Skill Improvement Audit (`tutorial-test-drive` + `/agy-customizations`)

Overlay read-only `/agy-customizations` skill retrospectives onto [`tutorial-test-drive`](../tutorial-test-drive/SKILL.md) (`Stages 1–7`) to collect per-prompt evidence and synthesize [`SkillImprovementAuditReport.md`](../../../SkillImprovementAuditReport.md) without modifying installed skills.

- Stage reset, `init-stage`, verbatim `docs/tutorial/` prompts, and deterministic stage gates: [`../tutorial-test-drive/SKILL.md`](../tutorial-test-drive/SKILL.md), [`../tutorial-test-drive/references/stage-gates.md`](../tutorial-test-drive/references/stage-gates.md), and [`../tutorial-test-drive/scripts/check_stage.py`](../tutorial-test-drive/scripts/check_stage.py)
- Subagent isolation overlay, verbatim `/agy-customizations` prompt, and scratch slug schedule: [`references/review-prompt-template.md`](./references/review-prompt-template.md)
- Report schema, finding IDs, severity rubric, and deduplication rules: [`references/report-format.md`](./references/report-format.md)
- Deterministic post-run report and zero-mutation verifier: [`scripts/verify_skill_audit.py`](./scripts/verify_skill_audit.py)

---

## 1. Pre-Flight & Subagent Isolation Overlay

1. Run the reset and clean-root guardrails from [`../tutorial-test-drive/SKILL.md`](../tutorial-test-drive/SKILL.md).
2. Define clean-room subagents (`tutorial-runner`, `clean-room-stage-2` … `clean-room-stage-7`) using the isolation rules in `tutorial-test-drive` plus the **Audit Overlay** in [`references/review-prompt-template.md`](./references/review-prompt-template.md):
   - Grant **read-only** access to `/Users/brett/.gemini/antigravity/builtin/skills/agy-customizations/` **only** during post-prompt review turns.
   - Forbid creating, editing, or deleting any file during review turns (zero mutations to `.agents/skills/` or stage outputs).
3. Before dispatching, clarify with the user whether any final `git commit` (if requested) should include `SkillImprovementAuditReport.md` alone or alongside updated `AuditReport.md` and regenerated `stages/stage-1/` … `stages/stage-7/`.

---

## 2. Per-Prompt Retrospective Workflow (`Stages 1 → 7`)

Execute each stage and step in `tutorial-test-drive` in strict order:

1. **Wait reactively for prompt completion:** After `invoke_subagent` or `send_message`, end your turn with no tool calls (never use `schedule` polling). Verify the step's deterministic stage gate before advancing.
2. **Send the read-only review prompt to the same subagent:** Send the verbatim `/agy-customizations` prompt from [`references/review-prompt-template.md`](./references/review-prompt-template.md) via `send_message` to the **same `conversationId`** that ran the step.
   - For multi-turn steps (`3.3a` → `3.3b` → `3.3c`, `5.2a` → `5.2b`, and conditional `6.2`), run and save the read-only review immediately after **each** turn completes before sending the next turn's prompt.
3. **Persist raw evidence immediately:** Save each verbatim reply (preserving multiple complementary replies if a subagent emits more than one message) to `<appDataDir>/brain/<conversation-id>/scratch/skill_reviews/<slug>.md` using the slug schedule in [`references/review-prompt-template.md`](./references/review-prompt-template.md).
4. **Pause cleanly on sandbox-escape timeouts:** If any subagent reports a `BypassSandbox: true` user-approval timeout, **do not kill it** and do not treat the timeout as a hard blocker. Leave the subagent parked in its wait state, stop calling tools, and post a concise note in the main conversation with:
   - Stage & Step name
   - Subagent `Role` and `conversationId`
   - Exact command awaiting approval
   When the user replies to poke the subagent, send a brief `send_message` to that `conversationId` to retry the single timed-out command (standalone, without chained `&&`) and resume.

---

## 3. Synthesizing `SkillImprovementAuditReport.md`

1. Read all saved `scratch/skill_reviews/*.md` files.
2. Deduplicate overlapping findings across turns, verify every target path and symbol directly against `stages/stage-7/.agents/skills/` (never cite unverified paths from memory), and write `SkillImprovementAuditReport.md` following [`references/report-format.md`](./references/report-format.md).
3. Update `AuditReport.md` per Section 6 of [`../tutorial-test-drive/SKILL.md`](../tutorial-test-drive/SKILL.md), cross-linking `SkillImprovementAuditReport.md`.

---

## 4. Verification & Repository Hygiene

Run the audit verifier and clean-root checks before reporting or committing:

```bash
python3 .agents/skills/skill-improvement-audit/scripts/verify_skill_audit.py check-all \
    --report SkillImprovementAuditReport.md \
    --scratch-dir <appDataDir>/brain/<conversation-id>/scratch/skill_reviews
python3 .agents/skills/tutorial-test-drive/scripts/check_stage.py check-clean-root
```

Confirm:
- `0` source mutations between `stages/stage-1/.agents/skills` and `stages/stage-7/.agents/skills`.
- `100%` of skill links in `SkillImprovementAuditReport.md` resolve on disk.
- Executive Summary severity totals match Section 2 finding bullets verbatim.
- `stages/stage-*/.ruff_cache` directories are removed and `stages/` contains `0` `.git` directories before any requested `git commit`.
