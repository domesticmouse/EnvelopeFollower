# Subagent Overlay, Review Prompt Template & Scratch Schedule

## 1. Clean-Room Subagent SystemPrompt Overlay

Append these rules to each `tutorial-runner` and `clean-room-stage-N` subagent `SystemPrompt` defined per `tutorial-test-drive`:

```text
EXCEPTION FOR POST-PROMPT `/agy-customizations` REVIEW:
- ONLY when explicitly asked to perform a `/agy-customizations` skill-improvement review, you have READ-ONLY permission to inspect `/Users/brett/.gemini/antigravity/builtin/skills/agy-customizations/`.
- During any `/agy-customizations` review turn, ZERO file writes, edits, or deletions are permitted anywhere (never modify `.agents/skills/` or stage outputs).

SANDBOX & TIMEOUT RULES:
- Always attempt shell commands with `BypassSandbox: false` first.
- Only if a command requires network access or external reads and fails inside the sandbox, retry ONLY that single command (standalone, without chained `&&`) with `BypassSandbox: true` and the EXACT SAME `toolSummary`.
- If a `BypassSandbox: true` command times out awaiting user approval, STOP immediately without retrying in a loop and report the exact command that timed out.
```

---

## 2. Verbatim Post-Prompt `/agy-customizations` `send_message` Prompt

Send this message to the subagent's existing `conversationId` **only after** its task message has arrived and stage-gate checks for that prompt have passed:

```text
Now that the prompt above is complete, please perform a read-only skill-improvement review using `/agy-customizations` based on what you just learned in this conversation.

1. Read `/Users/brett/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md` and `/Users/brett/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md` (plus `docs/rules.md` or `docs/hooks.md` under that folder if relevant).
2. DO NOT edit, create, or delete any files (strictly read-only; do NOT modify anything under `.agents/skills/` or any stage deliverables).
3. Inspect the relevant skill(s) under `stages/stage-<N>/.agents/skills/` that you used (or could have used) during this prompt, and evaluate whether any concrete improvements could be made based on actual friction, pitfalls, missing guidance, script bugs/edge cases, trigger description gaps, progressive-disclosure issues, or missing validation steps encountered in this conversation.
4. Return a structured Markdown report with:
   - **Stage / Step:** `<Stage N — Step X.Y>`
   - **Skills Used (or Inspected):** list of skill names from `stages/stage-<N>/.agents/skills/` (or `None`)
   - **Verdict:** `Improvements Suggested` or `No Improvements Needed`
   - **Findings (if any):** For each concrete improvement:
     - **Target Skill & File:** exact relative path inside `.agents/skills/<skill>/...` (or `New Skill / Rule / Hook` if proposing a new customization)
     - **Customization Type & Principle (`/agy-customizations`):** e.g., `SKILL.md` frontmatter description / progressive disclosure (`references/`) / executable helper (`scripts/`) / validation step / no duplication / rule / hook
     - **What Happened in This Conversation (Evidence):** exact command, error, warning, quirk, or friction observed
     - **Proposed Improvement:** specific, actionable change
     - **Severity / Impact:** `High` | `Medium` | `Low`

Be concrete and evidence-based: if nothing genuinely warrants changing a skill from this prompt, return `No Improvements Needed` rather than inventing generic advice.
```

---

## 3. Prompt-to-Scratch-Slug Schedule

Save each reply immediately to `<appDataDir>/brain/<conversation-id>/scratch/skill_reviews/<slug>.md`:

| Slug | Stage / Step | Subagent Lifecycle |
| :--- | :--- | :--- |
| `stage-1.md` | `Stage 1 — Skills Installation` | Fresh `tutorial-runner` |
| `stage-2.1.md` | `Stage 2 — Step 2.1 (Sketch Extraction)` | Fresh `clean-room-stage-2` |
| `stage-2.2.md` | `Stage 2 — Step 2.2 (Analog Circuit Audit)` | Fresh `clean-room-stage-2` |
| `stage-2.3.md` | `Stage 2 — Step 2.3 (Eurorack Protections)` | Fresh `clean-room-stage-2` |
| `stage-3.1.md` | `Stage 3 — Step 3.1 (JLCPCB Part Research & BOM)` | Fresh `clean-room-stage-3` |
| `stage-3.2.md` | `Stage 3 — Step 3.2 (Audio Electronics Walkthrough)` | Fresh `clean-room-stage-3` |
| `stage-3.3a.md` | `Stage 3 — Step 3.3a (Test Point Recommendations)` | `clean-room-stage-3` Turn 1 |
| `stage-3.3b.md` | `Stage 3 — Step 3.3b (Adding RH-5001 DNP Test Points)` | Same `clean-room-stage-3` Turn 2 |
| `stage-3.3c.md` | `Stage 3 — Step 3.3c (Silkscreen Instructions)` | Same `clean-room-stage-3` Turn 3 |
| `stage-4.md` | `Stage 4 — SKiDL Circuit & ERC` | Fresh `clean-room-stage-4` |
| `stage-5.1.md` | `Stage 5 — Step 5.1 (Main PCB Generation)` | Fresh `clean-room-stage-5` |
| `stage-5.2a.md` | `Stage 5 — Step 5.2a (Silkscreen & Polarity Audit)` | Fresh `clean-room-stage-5` Turn 1 |
| `stage-5.2b.md` | `Stage 5 — Step 5.2b (Silkscreen & Polarity Fixes)` | Same `clean-room-stage-5` Turn 2 (if discrepancies fixed) |
| `stage-6.1.md` | `Stage 6 — Mated 3U Front Panel` | Fresh `clean-room-stage-6` |
| `stage-6.2.md` | `Stage 6 — Conditional QR Marking Fix` | Same `clean-room-stage-6` Turn 2 (only if `JLCJLCJLC` appeared) |
| `stage-7.md` | `Stage 7 — Manufacturing & JLCPCB Assembly Export` | Fresh `clean-room-stage-7` |

---

## 4. Operational Guardrails

- **Never pre-write review files:** Wait for the subagent's actual reply before writing `<slug>.md`.
- **Multi-message replies:** If a subagent sends two complementary messages for one review turn (observed occasionally on complex steps), preserve both verbatim under `## Message 1` and `## Message 2` in `<slug>.md`.
- **Standalone unsandboxed commands:** When poking a subagent after a `BypassSandbox: true` timeout, instruct it to run only the single network/external command without `&&` chains so approval prompts stay atomic.
