# Phase 2C Workflow First Rebuild Report

## Scope

- Entered Phase 2C: YES, explicitly requested by the current task.
- Entered any next phase: NO.
- Real Meituan API / real payment / real customer service / real map / real delivery / real merchant order / database / WebSocket: NO.
- LLM boundary: LongCat adapter only, with no-key local fallback.

## Intent Contract

- User-visible summaries now read `intent_frame.confirmed_fields` and `intent_frame.field_sources`.
- `我和3个朋友` is counted as 4 people and marked as `explicit_text`.
- Named script titles such as `《快乐人生》` lock the primary task to script game before secondary food intent.
- Old request defaults are kept internal and are not rendered as confirmed user conditions.

## Required Slots Contract

- Script-game missing-input flow asks people, time, budget, script style, available window, and area before planning.
- Food discovery asks dine mode, area, time, budget, and cuisine before planning.
- Ambiguous date asks required slots; complete date text can proceed to Plan A/B.

## Frontend Workflow

- Stepper UI: input/required slots, candidate comparison, booking confirmation, execution handling.
- Plan A/B: horizontal comparison cards with origin, route, formal arrangement, endpoint, time, budget, and reason.
- Friend co-select is embedded in the candidate page and does not book anything.
- Final booking uses a bottom drawer; booking confirmation is the first point that creates Mock booking state.
- Execution page merges Mock bill, split, optional add-on, rescue, and support actions.

## Cleanup

- Old engineering banner and default logs are removed from the main user view.
- Old public celebration-style title residue is removed from planner/frontend docs.
- README and demo playbook are updated for Phase 2C workflow-first delivery.

## Acceptance

- Phase 2C cases: 11
- Phase 2C passed: 11/11
- Quick acceptance: PASS
- Full acceptance system failures: none
- Packaging POSIX paths: YES

## Failed Phase 2C Cases

- none

## Next Step

- Stop after Phase 2C and wait for a new explicit task.

