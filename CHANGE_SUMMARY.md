# Change Summary

## 2026-06-07 Phase 2C Micro Flow Patch

- `web/app.html`: changed the Phase 2C home screen into a chat-first layout with a white header, message history, compact examples, location selector, and bottom composer/button.
- `web/app.html`: added local chat message persistence for user instructions and assistant responses across input, clarification, candidate, friend-pick, and booking stages.
- `web/app.html`: changed Plan A / Plan B cards to stack vertically in two rows while keeping each merchant card horizontal.
- `web/app.html`: made `replaceSegmentOption` prefer the explicitly requested area first, so a Jiangning script-game request keeps replacements around Jiangning instead of drifting to Aoti or other areas.
- `web/app.html`: removed the completion button from route-tip blocks and updated execution progression to skip passive tip blocks.
- `web/app.html`: made final score selection reset back to the first page.

### Verification

- `python -m compileall agent server.py cli.py acceptance_check.py pack_submit.py`: PASS.
- JavaScript syntax parse for both embedded scripts: PASS.
- `python acceptance_check.py --case 194`: PASS.
- `python acceptance_check.py --quick`: PASS, 147/147.
- Browser smoke via Python Playwright + system Chrome:
  - `output/phase2c_micro_home_py.png`
  - `output/phase2c_micro_candidates_before_replace.png`
  - `output/phase2c_micro_candidates_after_replace.png`
  - Jiangning replacement stayed in Jiangning; no Aoti text appeared after replacement.

## Modified Files

- `agent/intent_frame.py`: added the Natural Intent Coordination Contract for dine mode defaults, stay-in delivery text, cuisine-any language, ordered sequences, clarification field compatibility, and factual goal framing.
- `agent/parser.py`: routes home delivery wording to stay-in, merges intent-frame sequence categories into request, normalizes empty-clarification states to `build_plan`, and preserves local fallback behavior.
- `agent/clarify.py`: treats `any/都可以/不限` as valid answers, avoids blocking stay-in delivery on area/dine-mode, and emits both `key` and `field`.
- `agent/planner.py`: uses request sequence as slot order, adds optional meal-bridge metadata for meal-window crossings, treats cuisine `any` as unlimited, and replaces evaluative focus copy with factual tokens.
- `agent/catalog.py` / `agent/category_schema.py`: include `any` in unlimited values.
- `agent/core.py`: clears stale `missing_fields` after clarification refinement.
- `web/app.html`: aligns the first homepage template with the explicit eat-in wording.
- `data/merchants.json`: enables `m_026` as the local Mock snack-delivery merchant for stay-in sequence planning.
- `acceptance_check.py`: added cases 216-233 and Natural Intent Coordination report generation.
- `pack_submit.py`: packages the Phase 2C natural-intent delivery zip and includes the new report.
- `PROJECT_STATUS.md`, `ACCEPTANCE_REPORT.md`, `CHANGE_SUMMARY.md`, `NATURAL_INTENT_COORDINATION_REPORT.md`: updated final handoff documents.

## Catalog Result

- Merchant count: 5000
- Area count: 11
- Category count: 24
- User-facing names with `Mock 001` style labels: 0 expected by case 189.
- Every merchant is expected to carry at least two local Mock coupons for the merchant-detail drawer.

## Acceptance Result

- Total cases: 147
- Passed: 147
- Failed: 0
- New cases 216-233:
  - 216. phase2c natural eat template should not block: PASS
  - 217. phase2c natural eat-in planning default: PASS
  - 218. phase2c natural cuisine any recognized: PASS
  - 219. phase2c natural home eating is delivery: PASS
  - 220. phase2c natural stay-in takeaway snacks sequence: PASS
  - 221. phase2c natural clarification key field compatibility: PASS
  - 222. phase2c natural stale missing fields cleared: PASS
  - 223. phase2c natural activity order plus meal bridge: PASS
  - 224. phase2c natural explicit middle meal preserved: PASS
  - 225. phase2c natural long activity dinner bridge: PASS
  - 226. phase2c natural no meal blocks bridge: PASS
  - 227. phase2c natural stay-in no area slot: PASS
  - 228. phase2c natural factual plan focus: PASS
  - 229. phase2c natural homepage template alignment: PASS
  - 230. phase2c natural coordination regression pack: PASS
  - 231. phase2c no_meal public default cleanup: PASS
  - 232. phase2c home eating clarification boundary: PASS
  - 233. phase2c script billiards required slots preserved: PASS

## Still Mock

- Booking, voting, payment, coupons, AA links, support, rescue, delivery, inventory, merchant availability, and deployment remain local Mock/demo boundaries.

## Known Risks

- Browser QA is not full visual regression automation.
- Execution drawers and merchant detail interactions are local-state Mock and should be manually previewed before the live demo.
- Synthetic catalog names are fictional and demo-scoped.

## System Failures

- none
