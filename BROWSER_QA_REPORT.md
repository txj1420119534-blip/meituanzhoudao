# Browser QA Report

## Scope

- Entered Phase 2C Browser/Deploy Polish: YES.
- Entered next phase: NO.
- Business boundaries remain local Mock only.

## Browser UI Adjustments

- Candidate cards now use merchant-first Plan A/B cards with emoji/logo, merchant name, category, quick facts, chips, feature copy, and risk copy.
- Stepper blocks future steps, lets completed steps scroll back to the top, and clears downstream stale booking/checkout/execution state when upstream information changes.
- AA split now states that each person's A amount can be manually edited; amount inputs update Mock A-money links and show a soft mismatch hint.
- Other issue uses inline input and Mock support/rescue routing instead of `prompt()`.

## Data And Ecosystem Cleanup

- User-facing merchant names no longer use `Mock 001` style labels.
- Real-brand-looking names in the demo catalog were converted to fictional local-life names.
- Online movie/online platform records are marked `disabled_for_recommendation` and do not enter user-facing transaction recommendations.

## Deploy Preparation

- `server.py` reads the Render `PORT` environment variable and defaults to 8000 locally.
- `render.yaml` is included for Render Web Service deployment.
- `DEPLOY_RENDER_GUIDE.md` documents Render setup, Netlify limitations, optional LongCat key, and Mock boundaries.
- `FRIEND_TEST_CHECKLIST.md` gives friends a test path and P0/P1/P2 feedback format.

## Acceptance Cases 185-193

- 185. phase2c browser candidate card visual cleanup: PASS
- 186. phase2c browser stepper back navigation reset: PASS
- 187. phase2c browser split manual amount sync: PASS
- 188. phase2c browser support other issue inline input: PASS
- 189. phase2c browser user-facing merchant names clean: PASS
- 190. phase2c browser no online movie user-facing recommendation: PASS
- 191. phase2c browser render config: PASS
- 192. phase2c browser friend test checklist: PASS
- 193. phase2c browser no external API boundary regression: PASS

## Verification

- `python acceptance_check.py --quick`: PASS
- `python acceptance_check.py`: PASS
- `python pack_submit.py`: PASS

## Remaining Risks

- Browser QA is supported by manual in-app browser preview plus static acceptance checks, not automated pixel regression.
- The merchant catalog remains synthetic Mock data for hackathon demonstration.
- Render deploy is prepared but not connected to real external services.

## Failures

- none
