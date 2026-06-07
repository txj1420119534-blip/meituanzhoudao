# Phase 2C User Flow Patch Report

## Scope

- Entered Phase 2C User Flow Patch: YES.
- Entered next phase: NO.
- Real API, real payment, real customer service, real map, real delivery, real order, database, and WebSocket remain forbidden.

## User Flow Changes

- Home is now a pure input entry: no homepage stepper, no process explanation, and the title is `你想怎么玩？`.
- Example chips are complete editable sentences; clicking them only fills the input box.
- Clarification removes the `已记住...还差...` copy and supports custom cuisine text for `更想吃哪类？`.
- Later pages no longer render the old `本次目标` card in the phone flow.
- Plan A/B cards are merchant-first and show different merchants, category, price, rating, reviews, business hours, queue/reservation, distance/traffic, and tags.
- Candidate and execution pages can open a local Mock merchant detail drawer with coupons and features.
- Friend co-selection is renamed to `喊朋友一起挑`; abnormal feedback buttons were removed from this stage.
- `都不要` swaps/refills candidates locally and shows the Mock preference `朋友想吃火锅` instead of jumping home.
- Friend voting now leads to `立即预约` only; delivery/stay-in plans skip the booking drawer and enter execution.
- Booking uses an in-phone bottom drawer with editable Mock information.
- Execution is a staged timeline with complete/return viewing, plus four drawer actions in the requested order.
- Bill drawer supports custom total/per-person amounts and one Mock collect link marked `美团/微信支付`.
- Delivery/stay-in wording uses `美团外卖`, delivery time, and delivery fee instead of arrival/queue language.

## Acceptance Cases 194-215

- 194. phase2c itinerary home chat entry: PASS
- 195. phase2c itinerary complete examples fill only: PASS
- 196. phase2c itinerary clarification and loading copy: PASS
- 197. phase2c itinerary preserves explicit segment order: PASS
- 198. phase2c itinerary total budget includes all main segments: PASS
- 199. phase2c itinerary store card structure: PASS
- 200. phase2c itinerary merchant detail and coupons: PASS
- 201. phase2c itinerary per-segment selection backend: PASS
- 202. phase2c itinerary booking bubbles: PASS
- 203. phase2c itinerary API select booking reservation smoke: PASS
- 204. phase2c itinerary friend co-select in segment: PASS
- 205. phase2c itinerary execution action order: PASS
- 206. phase2c itinerary execution transport and itinerary blocks: PASS
- 207. phase2c itinerary rescue and bill drawers: PASS
- 208. phase2c itinerary 5000 merchant catalog contract: PASS
- 209. phase2c itinerary admin key fields and reservation status: PASS
- 210. phase2c itinerary Plan A/B distinct merchants: PASS
- 211. phase2c itinerary stay-in delivery semantics: PASS
- 212. phase2c itinerary replace current card only: PASS
- 213. phase2c itinerary stage gates: PASS
- 214. phase2c itinerary local Mock boundary: PASS
- 215. phase2c itinerary integration tokens: PASS

## Verification

- `python acceptance_check.py --quick`: PASS
- `python acceptance_check.py`: PASS
- `python pack_submit.py`: PASS

## Remaining Risks

- Browser visual acceptance is still mostly static plus manual preview, not pixel-regression automation.
- Merchant coupons, booking, payment, support, voting, rescue, delivery, and inventory are local Mock only.
- Synthetic merchant names and facts are demo-scoped and not production data.

## Failures

- none
