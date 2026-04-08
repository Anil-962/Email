---
title: OmniTask AI API
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# OmniTask AI API

Docker Space for the FastAPI backend at `my_env.server.main:app`.

## Runtime notes

- Base URL health: `/`
- Interactive docs: `/docs`
- Set Space secret: `OPENAI_API_KEY`
- For Gmail endpoints in hosted mode, set:
  - `GMAIL_CREDENTIALS_JSON` (OAuth client JSON)
  - `GMAIL_TOKEN_JSON` (authorized user token JSON)
