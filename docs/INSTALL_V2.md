# V2：Windows Desktop / CLI

本說明對應 OpenCode 2.x；使用 `providers`、`mcp.servers`、`permissions`，**不可與 V1 JSON 混用**。

## 安裝
1. 從 [OpenCode 官方網站](https://opencode.ai/) 安裝支援 V2 的 Desktop 與 CLI，執行 `opencode --version` 確認為 2.x。
2. 安裝 Node.js（Playwright MCP）和 Python 3（OpenProject MCP）。
3. 建立 `%USERPROFILE%\.config\opencode`，備份原 `opencode.json`，將 [opencode.v2.example.json](../opencode-config/opencode.v2.example.json) 複製為 `opencode.json`。
4. 將 `YOUR_USERNAME` 改成本機使用者、`https://llm.example.invalid/v1` 換成自己的 OpenAI-compatible / LiteLLM 端點；填入真正的 model ID、context/output 限制。
5. 將私密 LLM Token 寫入同目錄 `llm-key.txt`，不要放進 JSON 或 Git。

## MCP
Playwright 預設 disabled，請先安裝 Edge 與 Node.js，再把 `disabled` 改為 false。
OpenProject 預設 disabled 且 `OPENPROJECT_ENABLE_WRITES=false`。先依 [MCP_OPENPROJECT](./MCP_OPENPROJECT.md) 裝好 Python MCP，確認已指定 URL、專案識別碼與 Token，再啟用並做唯讀測試。

## 測試（PowerShell）
```powershell
opencode --version
Get-Content -Raw "$env:USERPROFILE\.config\opencode\opencode.json" | ConvertFrom-Json | Out-Null
opencode models
opencode mcp list
```
`connected` 只代表 MCP 子程序可啟動，**不代表**遠端 API 驗證成功；必須實際呼叫 `openproject_project_options` 驗證。

本設定只是一份範例；模型 ID、內網網路、憑證與工具能力仍須自行核對。
