# V2：Windows Desktop / CLI

本說明對應 OpenCode 2.x；使用 `providers`、`mcp.servers`、`permissions`，**不可與 V1 JSON 混用**。

## 安裝
1. 從 [OpenCode 官方網站](https://opencode.ai/) 安裝支援 V2 的 Desktop 與 CLI，執行 `opencode --version` 確認為 2.x。
2. 安裝 Node.js（Playwright MCP）和 Python 3（OpenProject MCP）。
3. 建立 `%USERPROFILE%\.config\opencode`，備份原 `opencode.json`，將 [opencode.v2.example.json](../opencode-config/opencode.v2.example.json) 複製為 `opencode.json`。
4. 將 `REPLACE_WITH_...` 占位字串替換成你的本機有效路徑（僅在私人設定中修改），再調整模型端點、model ID 及 context/output 限制。
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

## 舊版對話匯入

如有 V1 JSON 匯入 V2 時發生格式不相容的情況，參考 [離線 Session 轉換工具](../tools/session-converter/README.md)。這不是匿名化工具，真實對話 JSON 請勿公開。
