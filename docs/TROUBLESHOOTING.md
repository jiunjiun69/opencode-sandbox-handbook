# Troubleshooting

## 1. Docker 或 WSL 無法使用

確認 Docker Desktop 已啟用 WSL integration：

```bash
docker --version
docker compose version
```

如果 WSL 裡找不到 Docker，請到 Docker Desktop 設定中啟用目前的 WSL distribution。

## 2. `/workspace` 沒有專案檔案

檢查 `.env`：

```bash
cat .env
```

`PROJECT_DIR` 必須是 WSL path：

```text
/mnt/d/path/to/your/project
```

不要使用 Windows path：

```text
D:\path\to\your\project
```

檢查掛載：

```bash
docker compose run --rm --entrypoint sh opencode -lc "pwd && ls -la /workspace"
```

## 3. OpenCode 無法連到地端 LLM

檢查：

- `opencode-config/opencode.json` 的 `baseURL`
- `opencode-config/llm-key.txt` 是否存在
- proxy 與 `NO_PROXY` 是否正確
- 容器內是否能解析 LLM host

可進容器測試：

```bash
docker compose run --rm --entrypoint sh opencode -lc "env | grep -i proxy"
```

## 4. 前端 dev server 主機瀏覽器打不開

請確認：

- 用 `docker compose run --service-ports --rm opencode` 啟動。
- dev server 綁定 `0.0.0.0`，不是只綁 `127.0.0.1`。
- 使用 `http://localhost:<port>` 從 Windows/主機瀏覽器開啟。

常見指令：

```bash
npm start -- --host 0.0.0.0 --port 4200
npm run dev -- --host 0.0.0.0 --port 5173
uvicorn app.main:app --host 0.0.0.0 --port 8000
dotnet run --urls http://0.0.0.0:5000
```

## 5. `playwright-host` MCP 沒出現

確認 `opencode-config/opencode.json`：

```json
"mcp": {
  "playwright-host": {
    "type": "remote",
    "url": "http://host.docker.internal:8931/mcp",
    "enabled": true
  }
}
```

確認 MCP server 已在主機或 WSL 啟動：

```bash
npx @playwright/mcp@latest --port 8931 --extension
```

在 OpenCode container 內確認：

```bash
docker compose run --rm opencode mcp list
```

如果 `host.docker.internal` 在你的 WSL/Docker 環境不可用，請改用 WSL 可連到的主機 IP，並更新 `opencode.json` 的 URL。

## 6. LLM 看不到 console 或 network error

請確認 prompt 明確要求使用 Playwright MCP：

```text
Use the frontend-debug skill and playwright-host. Open http://localhost:4200,
read console messages and failed network requests, take a screenshot, then fix the issue.
```

如果 MCP 有連上但資訊不足，請讓 LLM 執行：

- browser snapshot
- console messages
- network requests
- screenshot

## 7. OpenCode 設定檔 read-only 造成錯誤

本範本沒有把 `opencode-config` 掛成 read-only，因為 OpenCode 可能需要寫入 runtime metadata。若你自行加上 `:ro` 後遇到 UnknownError，請先移除 read-only 掛載。
