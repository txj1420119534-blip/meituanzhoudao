# Render Deploy Guide

## What This Deploys

`weekend-agent` is a FastAPI backend plus a vanilla HTML demo UI. Deploy it as a Render Web Service, not as a static-only site.

## Recommended Render Setup

1. Push the repository to GitHub.
2. In Render, create a new Blueprint or Web Service from the repository.
3. If using Blueprint, Render can read `render.yaml` directly.
4. If configuring manually:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

## Environment Variables

- `LONGCAT_API_KEY`: optional. Leave it blank for local deterministic fallback.
- No Meituan, Dianping, Gaode, payment, customer-service, merchant-order, inventory, coupon, member, map, or delivery keys are needed.

## Why Not Netlify

Netlify is mainly suitable for static frontend hosting. This project needs the FastAPI backend endpoints such as `/plan`, `/clarify`, `/select`, `/booking/review`, `/checkout/preview`, `/exception`, and `/support/create`, so deploy it as a backend web service.

## Mock Boundary

All booking, vote, checkout, split, add-on, support, rescue, coupon, and inventory behavior remains local Mock. The deploy is for demo review only.

## Packaging Status

- Zip internal paths use POSIX `/`: YES
- zip file: `weekend-agent-phase2c-itinerary-flow.zip`
- packaged files: 75
