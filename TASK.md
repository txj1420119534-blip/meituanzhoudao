# TASK.md

## Goal

Implement Phase 2C itinerary-loop flow reconstruction. Turn the user app from an engineering stepper demo into a chat-like Meituan local-life itinerary tool.

## Scope

- Update the user home screen into a chat input entry.
- Remove the visible stepper from the user flow.
- Keep the right panel as a weaker judge/debug summary.
- Preserve FastAPI + local JSON + vanilla HTML/JS.
- Preserve all external-business integrations as local Mock only.
- Rebuild the main visible flow:
  1. user input and clarification,
  2. segment-by-segment Plan A/B selection,
  3. per-segment booking confirmation,
  4. execution page with transport, itinerary, tips, change rescue, bill, and finish feedback.
- Expand and normalize local merchant mock data to support richer Plan A/B cards and admin display.
- Add local reservation status for the admin page after Mock booking.

## Required Behavior

- Home page:
  - Phone shell is the visual center.
  - Example chips are complete sample sentences and only fill the input box.
  - No start-time picker on the first page.
  - Area/location is a light context selector, not a required business slot.
  - Model/API loading feedback appears only while requests are running.

- Clarification:
  - Chat bubbles are used.
  - `duration_minutes` is asked as `想玩多久？`.
  - `吃饭 + 剧本杀` and `剧本杀 + 吃饭` preserve user order.
  - Missing duration should not become “activity type unknown”.

- Plan selection:
  - Each main segment is one system bubble.
  - Each segment has Plan A and Plan B merchant cards.
  - Cards show emoji image, merchant name, rating, review snippet, hours, distance, price, feature tags, and a replace button.
  - Confirming A/B only selects that segment.
  - All main segments must be selected before booking.
  - Group scenarios can use a local Mock friend vote.

- Booking:
  - Each selected segment has one booking bubble.
  - Arrival time is filled from start time, travel time, and previous segment duration.
  - Confirmed booking buttons become `分享给朋友`.
  - Consulting a merchant is local Mock only.
  - Cancelling a segment returns to Plan selection and resets that segment.

- Execution:
  - Show transport blocks, itinerary blocks, route-tip/add-on blocks, change rescue, bill, and finish feedback.
  - `导航`, `打车`, `买单`, `购买/核验券`, `评价`, `联系客服` are all local Mock interactions.
  - Finish asks a 0-10 share willingness question, thanks the user, and resets.

- Budget:
  - A user's per-person budget applies to the total of all main segments plus Mock transportation.
  - Over-budget candidates must not be labeled as compliant.

- Admin/data:
  - Local merchant data should reach at least 5000 rows.
  - Merchant rows expose key frontend fields and local Mock reservation status.
  - Category names stay user-facing, such as `奶茶` and `外卖`.

## Forbidden

- Real Meituan API.
- Real payment.
- Real customer service.
- Real map/navigation.
- Real delivery.
- Real merchant booking or ordering.
- User accounts.
- Database migration.
- WebSocket.
- Entering a new phase after this task.

## Verification

Run when practical:

```powershell
python -m compileall agent server.py cli.py acceptance_check.py pack_submit.py
python acceptance_check.py --quick
python acceptance_check.py
python pack_submit.py
```

If long acceptance is unstable or times out, report the exact failure without trying to fake a pass.
