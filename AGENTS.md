# AGENTS.md

## Project Identity

This project is `weekend-agent`, also called "美团周到".

It is a Meituan AI Hackathon topic 6 demo: a local-life execution Agent for weekend leisure planning. The goal is not to build a generic recommender, route planner, chatbot, or merchant search page. The product should understand a user's real intent, ask for missing information, respect constraints, build an executable itinerary, and provide Mock-level closed-loop interactions such as selection, reservation, share card, exception recovery, support entry, and price comparison.

The current architecture is Python + FastAPI + local JSON Mock data + vanilla HTML/JS. Real Meituan, Dianping, Gaode, payment, merchant, map, inventory, account, or customer-service APIs are not used.

## Required Reading Before Every Codex Task

Before doing any work, Codex must read:

1. `PROJECT_STATUS.md`
2. `TASK.md`

If those files are missing, stale, or conflict with the user's newest instruction, stop and ask for clarification before editing code.

## Strictly Forbidden

Codex must not implement or introduce:

- Real payment.
- Real customer service.
- WebSocket or real-time collaboration infrastructure.
- External API calls.
- Real merchant ordering or booking.
- User account systems.
- Database migrations.
- Large architecture rewrites.
- New product phases outside `TASK.md`.
- Phase 2B work unless `TASK.md` explicitly authorizes Phase 2B.
- Any feature not requested in the current `TASK.md`.

Codex must not treat internal defaults as user-confirmed facts. Values such as `party_size=4`, `budget=150`, `transport=public`, `home_area=鏂拌鍙, or `start_time=14:00` may be internal planning assumptions only when not explicitly provided or answered by the user.

## Work Rules

- Keep scope bounded to `TASK.md`.
- Do not expand the task because a feature seems useful.
- Do not enter the next phase unless the user explicitly updates `TASK.md`.
- Preserve the existing runnable demo skeleton unless the task explicitly asks for a rewrite.
- Prefer local rules and deterministic code for workflow control.
- LLM usage must remain limited to natural-language parsing and share-card copy where the current code already permits it.
- Hard constraints must beat ads, coupons, rating, and commercial recommendations.
- Main itinerary and optional add-ons must remain separated.
- Failure should be explicit and structured; silently changing the user's requested category is not acceptable.
- Be careful with a dirty git tree. Do not revert unrelated user or generated changes.
- Do not edit business code when the task is documentation, audit, packaging, or workflow setup only.

## Test Commands

Use these commands when a task touches backend logic, acceptance behavior, packaging, or reports:

```powershell
python -m compileall agent server.py cli.py acceptance_check.py pack_submit.py
python acceptance_check.py --quick
python acceptance_check.py
python pack_submit.py
```

For a documentation-only task that does not modify business code, at minimum verify the intended files exist and confirm no forbidden business files were changed.

## Completion Report Format

At the end of each task, report:

1. Files added or modified.
2. What each changed file is for.
3. Whether business code was modified.
4. Verification commands run and results.
5. Remaining risks or unresolved items.
6. Whether the next phase is authorized by `TASK.md`.

## Scope Control

Codex must not self-authorize new stages. If the next obvious step is Phase 2B, a UI polish pass, a product feature, or a backend rebuild, Codex should only recommend it and wait for `TASK.md` to be updated.


