---
name: frontend-debug
description: Use when debugging frontend rendering, browser console errors, failed network requests, or visual regressions through the configured Playwright MCP host browser bridge.
license: MIT
---

# Frontend Debug

Use this workflow when the user asks to fix or verify a web UI.

## Required posture

- Prefer the configured `playwright-host` MCP tools when available.
- Do not use web search or web fetch.
- Keep source-code access inside `/workspace`.
- Treat host-browser mode as sensitive because it can reuse cookies, login state, localStorage, and open tabs.
- If the page may contain secrets or production data, ask before reading or interacting with it.

## Workflow

1. Identify the expected local URL. Common defaults are:
   - Angular: `http://localhost:4200`
   - Vite: `http://localhost:5173`
   - Next.js or Node: `http://localhost:3000`
   - ASP.NET Core: `http://localhost:5000`
   - Python API/web: `http://localhost:8000`
2. Confirm or start the dev server with host binding:
   - Angular: `npm start -- --host 0.0.0.0 --port 4200`
   - Vite: `npm run dev -- --host 0.0.0.0 --port 5173`
   - ASP.NET Core: `dotnet run --urls http://0.0.0.0:5000`
   - FastAPI: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. Open the page with `playwright-host`.
4. Capture:
   - accessibility snapshot
   - screenshot
   - console messages
   - failed network requests
5. Map browser errors back to source files.
6. Apply the smallest code change that fixes the issue.
7. Re-run the browser check and relevant tests.
8. Report what changed, what was verified, and any remaining risk.

## Failure handling

- If `playwright-host` is unavailable, tell the user to enable it in `opencode.json` and start `npx @playwright/mcp@latest --port 8931 --extension`.
- If the host cannot reach the dev server, ensure OpenCode was started with `docker compose run --service-ports --rm opencode` and the dev server binds to `0.0.0.0`.
- If `host.docker.internal` does not resolve, use the WSL-reachable host IP in the MCP URL.
