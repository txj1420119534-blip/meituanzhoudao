# Phase 2C Polish + Catalog Expansion Report

## Scope

- Entered Phase 2C Polish + Catalog Expansion: YES, explicitly requested by the current task.
- Entered next phase: NO.
- Real Meituan/Dianping/Gaode/map/payment/customer-service/delivery/order/member APIs: NO.
- LLM boundary: LongCat remains optional and local rule fallback is safe when no key exists.

## What Changed

- Multi-select preferences now support date preferences, broad activity choices, food preferences, and script style choices.
- Homepage presets are complete sentences and only fill the input box; they do not bypass required slots.
- Candidate cards use a lighter merchant-first hierarchy with Plan A / Plan B titles only.
- Stepper lets users revisit unlocked steps and blocks future steps until the workflow state unlocks them.
- Friend co-select supports Plan A wins, Plan B wins, and none of these; none of these returns to requirement update instead of booking.
- Execution page exposes Meituan group-buy coupon Mock, Meituan pay-at-store Mock, editable AA split, add-on drawer, and rescue/support entry points.
- Birthday cake/flowers are treated as long-lead optional preparation, not as Plan A/B core content.

## Catalog Size

- Current merchant count: 5000
- Area coverage: 11 areas
- Category coverage: 24 categories
- Recommendations carry matching metadata such as candidate pool size, area/category/budget filter counts, constraints, and selected merchant ids.

## New Acceptance Cases

- 169. phase2c date preferences multi-select: PASS
- 170. phase2c homepage template completeness: PASS
- 171. phase2c candidate card cleanup: PASS
- 172. phase2c stepper navigation gate: PASS
- 173. phase2c friend co-select no-option: PASS
- 174. phase2c execution payment buttons: PASS
- 175. phase2c split bill manual adjustment: PASS
- 176. phase2c support other issue: PASS
- 177. phase2c addon placement: PASS
- 178. phase2c long-lead addon early prompt: PASS
- 179. phase2c catalog size: PASS
- 180. phase2c catalog coverage: PASS
- 181. phase2c data-driven food recommendation: PASS
- 182. phase2c data-driven script recommendation: PASS
- 183. phase2c no online movie core recommendation: PASS
- 184. phase2c mock boundary scan: PASS

## Verification

- `python acceptance_check.py --quick`: PASS
- `python acceptance_check.py`: PASS
- `python pack_submit.py`: PASS

## Mock Boundaries

- Friend co-select is local Mock, not true real-time multi-user collaboration.
- Booking, group-buy coupons, pay-at-store, AA links, support, rescue, delivery, and merchant inventory are local Mock.
- No external service is called during acceptance.

## Remaining Risks

- The expanded catalog is synthetic Mock data; quality is sufficient for demo but not production.
- Frontend checks are static acceptance checks plus backend scenarios, not full browser visual regression.
- Planner remains rule based and should not be presented as production-grade optimization.

## Failures

- none
