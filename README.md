# Weekend Agent

Phase 2C workflow-first plus catalog-expansion demo for the Meituan AI Hackathon topic 6.

The project is a local Mock agent for weekend local-life planning. It does not call live Meituan services, does not write to a production order system, and does not process live payment. The current focus is a demonstrable workflow: intent contract, required-slot confirmation, Plan A/B comparison, friend co-select, booking confirmation, execution handling, and evidence that recommendations are selected from a large local Mock catalog.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

Open:

- User demo: `http://127.0.0.1:8000/`
- Admin mock catalog: `http://127.0.0.1:8000/admin`

`LONGCAT_API_KEY` is optional. If it is absent, the parser uses deterministic local rules and the demo still runs.

To try the LongCat model API once, create or edit `.env` in this project root:

```dotenv
LONGCAT_API_KEY=your_app_key_here
LONGCAT_BASE_URL=https://api.longcat.chat/openai
LONGCAT_MODEL=LongCat-2.0-Preview
```

Then run:

```powershell
python -m agent.llm
```

This is only the LongCat model API used for natural-language parsing fallback. It is not a real Meituan business API, does not place orders, and does not call real merchant, map, delivery, payment, coupon, membership, or customer-service systems.

## Render Deployment

This project should be deployed as a Render Web Service because it has a FastAPI backend. It is not a static-only Netlify app.

Render can use `render.yaml` directly:

```yaml
buildCommand: pip install -r requirements.txt
startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
```

`LONGCAT_API_KEY` can be left blank. Without it, the local rule fallback remains available. No Meituan, Dianping, Gaode, map, payment, customer-service, merchant-order, inventory, coupon, member, or delivery API key is required.

## Workflow

1. User enters one natural-language request.
2. Parser builds an `intent_frame` and only treats explicit text or user answers as confirmed.
3. Required slots pause the flow when the request is underspecified.
4. Planner creates Plan A / Plan B horizontal candidates.
5. Friend co-select is embedded in the candidate page and remains Mock.
6. The user opens a bottom booking drawer and confirms local Mock booking.
7. Execution page combines mock bill, split, optional add-on, support page, and rescue.

## Natural Intent Coordination

- Dining requests such as `吃饭 / 聚餐 / 找个地方吃` default to `dine_mode=eat_in` with source `planning_default` only when `main_role=EAT` or the explicit sequence contains an `EAT` segment.
- If `negative_intents` contains `no_meal`, `dine_mode` stays `unknown`, `cuisine_preference` stays `null`, and meal bridge is disabled.
- `菜系都可以 / 吃什么都行 / 随便吃点 / 不挑` maps to `cuisine_preference=any` only inside an eating context, so the system does not keep asking for cuisine.
- `在家吃点 / 宅家点外卖和零食` routes to stay-in delivery and snack supply; it may ask time, budget, or what kind of delivery supply is wanted, but it does not ask for business area, dine-in mode, or restaurant booking.
- Long activity plans that cross lunch or dinner can attach a meal-bridge prompt as optional supply. It is not treated as a confirmed main segment unless the user explicitly asks to eat.

## Mock Catalog

- Current merchant/service records: 548.
- Coverage: 12 areas and 33 categories.
- The catalog is synthetic local Mock data, not scraped or fetched from production services.
- User-facing merchant names are fictional local-life names, not `Mock 043` style test labels.
- Online movie/platform content is disabled for user-facing transaction recommendations; stay-in plans focus on takeaway meals, snack supply, drinks, desserts, and light food.
- Planner output keeps matching metadata such as candidate pool size, filter counts, constraints, and selected merchant ids so reviewers can see that Plan A/B comes from data matching rather than a fixed script.

## Core Files

- `agent/parser.py`: natural-language parsing plus LongCat/local fallback boundary.
- `agent/intent_frame.py`: user-truth contract for confirmed fields and unknown fields.
- `agent/clarify.py`: required-slot question generation.
- `agent/planner.py`: candidate itinerary generation and local rescue.
- `agent/group_decision.py`: Mock friend co-select and feedback handling.
- `agent/checkout.py`: local Mock checkout and split logic.
- `agent/addon.py`: optional add-on suggestions.
- `server.py`: HTTP thin layer with `session_id` isolation.
- `web/app.html`: Phase 2C workflow-first demo UI.
- `acceptance_check.py`: local acceptance runner.
- `PHASE2C_POLISH_REPORT.md`: current polish and workflow handoff report.
- `CATALOG_EXPANSION_REPORT.md`: local Mock catalog expansion report.
- `NATURAL_INTENT_COORDINATION_REPORT.md`: natural eating, stay-in, cuisine-any, and meal-bridge handoff report.

## API

- `POST /plan`
- `POST /clarify`
- `POST /refine`
- `POST /select`
- `POST /vote/create`
- `POST /vote/{room_id}`
- `POST /vote/{room_id}/confirm`
- `POST /vote/{room_id}/resolve`
- `POST /booking/review`
- `POST /booking/update`
- `POST /booking/confirm`
- `POST /addon/accept`
- `POST /addon/remove`
- `POST /checkout/preview`
- `POST /checkout/apply`
- `POST /checkout/pay`
- `POST /checkout/split`
- `POST /exception`
- `POST /support/create`
- `POST /support/{support_case_id}/reply`
- `POST /support/{support_case_id}/action`
- `GET /support/{support_case_id}`
- `POST /reset`
- `GET /merchants`
- `POST /merchants`

## Verification

```powershell
python -m compileall agent server.py cli.py acceptance_check.py pack_submit.py
python acceptance_check.py --quick
python acceptance_check.py
python pack_submit.py
```

`acceptance_check.py` now covers natural-intent coordination cases 216-233 in addition to the earlier Phase 2C cases for intent truth, required slots, Plan A/B UI, friend co-select, booking drawer, execution page, LongCat fallback, public residue cleanup, multi-select preference polish, Mock catalog size, data-driven recommendation, browser/deploy polish, and Mock boundary scanning.

The current package command produces:

```text
weekend-agent-phase2c-natural-intent-fix.zip
```

## Boundaries

The demo remains local Mock only:

- No real Meituan API.
- No real payment.
- No real customer service.
- No real map.
- No real delivery.
- No real merchant order.
- No database.
- No WebSocket.
