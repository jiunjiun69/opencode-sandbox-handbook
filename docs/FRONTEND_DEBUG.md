# Frontend Debugging with Host Browser MCP

OpenCode 可以改程式與執行 shell，但它不會自動知道瀏覽器實際渲染結果。前端開發若要讓 LLM 看見畫面、console error、network error 與 screenshot，需要接瀏覽器工具。

本範本建議：

- OpenCode 仍跑在 Docker sandbox 中。
- 程式碼仍只透過 `/workspace` 掛載。
- 瀏覽器觀測走主機 Chrome/Edge + Playwright MCP Bridge。
- `frontend-debug` skill 固定 LLM 的 debug 流程。

## 1. 啟動主機端 Playwright MCP

在 Windows PowerShell 或 WSL 中啟動：

```bash
npx @playwright/mcp@latest --port 8931 --extension
```

此模式會透過 Playwright MCP Bridge 連到你既有的 Chrome/Edge tab，適合需要 SSO、2FA、公司 extension 或既有登入狀態的內部系統。

替代方案：使用 CDP。

```bash
npx @playwright/mcp@latest --port 8931 --cdp-endpoint=chrome
```

若使用 CDP，請先在 Chrome/Edge 的 `chrome://inspect/#remote-debugging` 啟用 remote debugging，或用公司核准的方式啟動瀏覽器 debug endpoint。

## 2. 啟用 OpenCode MCP 設定

複製範例設定後，編輯 `opencode-config/opencode.json`：

```json
"mcp": {
  "playwright-host": {
    "type": "remote",
    "url": "http://host.docker.internal:8931/mcp",
    "enabled": true,
    "timeout": 10000
  }
},
"tools": {
  "playwright-host_*": true
}
```

如果 `host.docker.internal` 無法連線，請改成 WSL 能連到的主機 IP：

```json
"url": "http://<HOST_IP>:8931/mcp"
```

## 3. 啟動 OpenCode 並保留 dev server ports

```bash
docker compose run --service-ports --rm opencode
```

如果使用 helper script：

```bash
./scripts/run-with-project-dir.sh /mnt/d/path/to/your/project
```

## 4. 啟動前端 dev server

dev server 必須綁定 `0.0.0.0`，主機瀏覽器才容易連到容器內服務。

Angular：

```bash
npm start -- --host 0.0.0.0 --port 4200
```

Vite：

```bash
npm run dev -- --host 0.0.0.0 --port 5173
```

Python FastAPI：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

ASP.NET Core：

```bash
dotnet run --urls http://0.0.0.0:5000
```

## 5. 建議 prompt

```text
Use the frontend-debug skill and playwright-host.
Open http://localhost:4200.
Capture the accessibility snapshot, console messages, failed network requests, and a screenshot.
Summarize the visible problem, then fix the code.
```

## 6. 安全注意事項

主機瀏覽器模式很方便，但權限較高：

- LLM 可能看見已登入頁面。
- LLM 可能讀到 cookies/localStorage 相關狀態。
- LLM 可能操作你既有 tab。

建議：

- 使用測試帳號。
- 避免在同一 browser profile 開啟高度敏感系統。
- 每次只啟用必要 MCP。
- 完成前端 debug 後可把 `playwright-host.enabled` 改回 `false`。

如果專案敏感度更高，請改用 isolated browser profile，不連既有主機瀏覽器登入狀態。
