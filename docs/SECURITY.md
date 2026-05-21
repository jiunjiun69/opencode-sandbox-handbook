# Security Guide

此範本的核心目標是讓 OpenCode 能協助開發，但不能任意讀取公司機器上的資料，也不能把程式碼送到外部服務。

## 不要提交的資料

請勿提交以下內容：

- API key、access token、private key
- 公司內部 IP、hostname、帳號、密碼
- 內部 repository URL 或客戶資料
- `.env`
- `opencode-config/llm-key.txt`
- `opencode-config/opencode.json`
- `opencode-data/*`

Git 只應保存可分享的範例設定：

- `.env.example`
- `opencode-config/llm-key.example.txt`
- `opencode-config/opencode.example.json`
- `opencode-data/.gitkeep`

## Docker sandbox 邊界

容器只掛載一個工作目錄：

```text
${PROJECT_DIR} -> /workspace
```

不要把下列路徑直接掛進容器：

```text
/
/mnt/c/Users
/mnt/d
公司共用磁碟根目錄
```

請每次只掛載單一專案資料夾。

## OpenCode 權限

預設範例設定會要求使用者確認 edit/bash，並禁止外部瀏覽與 workspace 外存取：

```json
"permission": {
  "edit": "ask",
  "bash": "ask",
  "webfetch": "deny",
  "websearch": "deny",
  "external_directory": "deny"
}
```

## MCP 風險

MCP 會把額外工具提供給 LLM。工具越多，權限與 context 成本越高。

本範本的 `playwright-host` 預設為 disabled。只有在需要前端畫面觀測時才啟用。

主機瀏覽器模式的風險：

- 可能重用你 Chrome/Edge 的登入狀態、cookies、localStorage。
- 可能看見已開啟 tab 的頁面內容。
- 若使用 browser extension，會與瀏覽器 extension 生態互動。

建議控管：

- 僅在受信任的 OpenCode session 啟用。
- 優先使用測試帳號與測試環境。
- 高敏感專案改用 isolated browser profile，不重用主機登入狀態。
- MCP server 只綁定 localhost 或內網，不暴露到外網。

## Proxy 與外連

公司網路若要求 proxy，請在 `.env` 設定：

```env
HTTP_PROXY=http://proxy.company.local:8080
HTTPS_PROXY=http://proxy.company.local:8080
NO_PROXY=localhost,127.0.0.1,host.docker.internal,.company.local,YOUR_LLM_HOST
```

`docker-compose.yml` 會同時把這些值映射到小寫的 `http_proxy`、`https_proxy`、`no_proxy`，方便 Linux 工具使用。

`NO_PROXY` 至少應包含：

- `localhost`
- `127.0.0.1`
- `host.docker.internal`
- 公司內部 domain
- 地端 LLM endpoint
- Playwright MCP endpoint

## 日常安全檢查

在要求 AI 做較大修改前後，建議檢查：

```bash
git status
git diff
```

若要確認 sandbox 只看見指定 workspace：

```bash
docker compose run --rm --entrypoint sh opencode -lc "pwd && ls -la /workspace"
```
