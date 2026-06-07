# Phase 2C Itinerary Flow Report

## Scope

This round rebuilt the user-facing itinerary loop around a chat-style Meituan local-life flow while keeping all integrations local Mock only.

## What Changed

- Replaced the visible user stepper with a chat-first home screen and flow-specific states.
- Widened the phone shell and weakened the judge/debug panel so the demo reads as a user tool first.
- Added complete example prompts that fill the input box without auto-planning.
- Kept location as light context on the home page and removed the first-page time picker.
- Added request-time loading copy only while a real request is running.
- Rendered clarification as user/system chat bubbles and changed duration copy to "想玩多久？".
- Preserved explicit sequence order, including `吃饭 -> 剧本杀` and `剧本杀 -> 吃饭`.
- Added per-segment Plan A/B selection with merchant-first cards, merchant detail entry, replace-current-card behavior, and friend co-select mock voting.
- Added per-segment booking review through `/select_segments`, with booking bubbles, auto-filled mock reservation fields, confirm/share/consult/cancel states, and admin reservation visibility.
- Rebuilt the execution page around transport blocks, itinerary blocks, route-tip blocks, change rescue, billing, support, and finish feedback.
- Normalized stay-in delivery categories from `外卖正餐` to user-facing `外卖`, matching the expanded catalog and admin naming.
- Expanded local merchant data to 5000 synthetic merchants across 11 areas and 24 categories with frontend-facing fields and coupons.

## Backend And Data

- `Agent.choose_segments()` records one selected Plan A/B merchant per segment and prepares booking review state.
- `/select_segments` selects all confirmed segment choices without booking anything yet.
- `/merchants` now includes session-local mock reservation status and preview data for the admin page.
- Planner total cost now includes mock transport cost and marks over-budget plans with `needs_user_confirm`.
- Stay-in delivery searches now use `外卖` and `闪购零食`, not stale `外卖正餐` / `小象` naming.

## Verification

- `python -m compileall agent server.py cli.py acceptance_check.py pack_submit.py`: PASS
- `python acceptance_check.py --quick`: PASS, 147/147
- `python acceptance_check.py`: PASS, 230/230
- `python pack_submit.py`: PASS, POSIX archive paths

## Still Mock

- Payment, coupons, booking, support, navigation, taxi, friend voting, delivery, merchant availability, and rescue are local Mock states only.
- No real Meituan API, real payment, real customer service, real map, real delivery, database, WebSocket, or user account system was added.

## Known Risks

- Browser visual QA is still mostly static/acceptance based; manual live preview is recommended before the pitch.
- The 5000-row catalog is synthetic and demo-scoped.
- External-looking actions intentionally stop at local Mock UI states.

