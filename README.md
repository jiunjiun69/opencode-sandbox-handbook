# OpenCode Sandbox Handbook

這個專案是一個公司內部可重複使用的 OpenCode sandbox 範本。目標是在 **WSL + Docker Compose** 中執行 OpenCode，限制 LLM 只能操作掛載進容器的專案目錄，並串接公司內部的 OpenAI-compatible 地端模型。

適合的使用情境：

- 公司程式碼、資料、API 文件不允許送到外部雲端模型。
- LLM endpoint 必須走內網或 proxy。
- 希望 Coding Agent 只能看見指定專案資料夾，而不是整台 Windows/WSL。
- 常做 Python API/網頁、C# console/MVC、TypeScript Angular/Vite 前端開發。
- 前端開發時，希望 LLM 能看見瀏覽器畫面、console error、network error 與 screenshot。

## 架構

```text
Windows / WSL
  |
  |-- Host Chrome/Edge + Playwright MCP Bridge  (可選，用於前端觀測)
  |
Docker Compose
  |
OpenCode container
  |
  |-- /workspace                         -> 你的專案目錄
  |-- /root/.config/opencode             -> OpenCode 設定與 skill
  |-- /root/.local/share/opencode        -> OpenCode session 資料
  |
Internal OpenAI-compatible LLM endpoint
```

核心安全原則：

- OpenCode 只能透過 `/workspace` 存取你指定的專案。
- `webfetch`、`websearch`、`external_directory` 預設禁用。
- API key、OpenCode runtime config、session data 不進 Git。
- 前端瀏覽器觀測使用 opt-in MCP；需要時才啟用。
- 主機瀏覽器模式會重用既有登入狀態，僅建議給受信任的 OpenCode session 使用。

## 專案結構

```text
opencode-sandbox-handbook/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── opencode-config/
│   ├── opencode.example.json
│   ├── llm-key.example.txt
│   └── skills/
│       └── frontend-debug/
│           └── SKILL.md
├── opencode-data/
│   └── .gitkeep
├── scripts/
│   ├── run-example-project.sh
│   └── run-with-project-dir.sh
└── docs/
    ├── FRONTEND_DEBUG.md
    ├── SECURITY.md
    └── TROUBLESHOOTING.md
```

## 前置需求

- Windows + WSL
- Docker Desktop，並啟用 WSL integration
- 可連線的公司內部 OpenAI-compatible LLM endpoint
- LLM API key
- 如需前端觀測：Node.js 18+ 與 Chrome/Edge

在 WSL 中確認 Docker：

```bash
docker --version
docker compose version
```

## 快速開始

### 1. 複製設定檔

```bash
cp .env.example .env
cp opencode-config/opencode.example.json opencode-config/opencode.json
cp opencode-config/llm-key.example.txt opencode-config/llm-key.txt
```

### 2. 設定 `.env`

`PROJECT_DIR` 請使用 WSL path，不要使用 Windows path。

```env
PROJECT_DIR=/mnt/d/path/to/your/project

# 如公司網路需要 proxy，取消註解並調整。
# HTTP_PROXY=http://proxy.company.local:8080
# HTTPS_PROXY=http://proxy.company.local:8080
# NO_PROXY=localhost,127.0.0.1,host.docker.internal,.company.local,YOUR_LLM_HOST
```

### 3. 設定地端模型

編輯 `opencode-config/opencode.json`：

```json
"baseURL": "http://YOUR_LLM_HOST:PORT",
"model": "internal-llm/YOUR_MODEL_NAME"
```

編輯 `opencode-config/llm-key.txt`：

```text
sk-your-api-key
```

## 啟動 OpenCode

一般後端、console、CLI 專案：

```bash
docker compose run --rm opencode
```

前端或網頁專案建議使用 service ports，讓主機瀏覽器能開到容器內 dev server：

```bash
docker compose run --service-ports --rm opencode
```

或使用 helper script：

```bash
chmod +x scripts/run-with-project-dir.sh
./scripts/run-with-project-dir.sh /mnt/d/path/to/your/project
```

進入 OpenCode 後，工作目錄會是：

```text
/workspace
```

## 前端瀏覽器觀測

OpenCode 本身能讀檔、改檔、跑指令，但不會自動看見瀏覽器畫面。要讓 LLM 看到 DOM、console、network、screenshot，需要額外接一個瀏覽器工具。此範本建議使用 **Playwright MCP Bridge 連主機 Chrome/Edge**。

詳細步驟請看 [docs/FRONTEND_DEBUG.md](docs/FRONTEND_DEBUG.md)。

簡化流程：

1. 在主機或 WSL 啟動 Playwright MCP HTTP server。
2. 在 `opencode-config/opencode.json` 將 `playwright-host.enabled` 改成 `true`。
3. 用 `docker compose run --service-ports --rm opencode` 啟動 OpenCode。
4. 請 LLM 使用 `frontend-debug` skill 與 `playwright-host` MCP 檢查頁面。

範例 prompt：

```text
Use the frontend-debug skill. Open http://localhost:4200 with playwright-host,
check console and network errors, take a screenshot, then fix the issue.
```

## 常用開發指令模板

### Angular / TypeScript frontend

```bash
npm install
npm run lint
npm test
npm run build
npm start -- --host 0.0.0.0 --port 4200
```

### Vite / React / Vue frontend

```bash
npm install
npm run lint
npm test
npm run build
npm run dev -- --host 0.0.0.0 --port 5173
```

### Python API / web

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### C# console / MVC

```bash
dotnet restore
dotnet build
dotnet test
dotnet run --urls http://0.0.0.0:5000
```

## Health Check

確認 workspace 掛載：

```bash
docker compose run --rm --entrypoint sh opencode -lc "pwd && ls -la /workspace"
```

確認 OpenCode MCP 設定：

```bash
docker compose run --rm opencode mcp list
```

確認 dev server 可被主機瀏覽器打開：

```text
http://localhost:4200
http://localhost:5173
http://localhost:5000
http://localhost:8000
```

更多問題排查請看 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)。
