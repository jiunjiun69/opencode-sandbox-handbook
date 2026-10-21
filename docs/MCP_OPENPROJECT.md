# OpenProject Community + OpenCode MCP（API v3）

範例 Python Server 位於 [mcp/openproject](../mcp/openproject/)。支援設定固定的 OpenProject 專案，查詢、新增和更新 Work Package；不依賴 Enterprise MCP。

## Windows 安裝
```powershell
$base = Join-Path $env:USERPROFILE ".config\opencode\openproject-mcp"
New-Item -ItemType Directory -Force $base | Out-Null
Copy-Item .\mcp\openproject\server.py $base
Copy-Item .\mcp\openproject\requirements.txt $base
py -3 -m venv "$base\.venv"
& "$base\.venv\Scripts\python.exe" -m pip install -r "$base\requirements.txt"
```
在本機 `%USERPROFILE%\.config\opencode\openproject-key.txt` 保存 API Token，不要提交。V2 JSON 中修改 `YOUR_USERNAME`、`OPENPROJECT_URL` 和 `OPENPROJECT_PROJECT_IDENTIFIER`（網址 slug，不是數字 Project ID），設 `disabled=false`。

- `project_options`、`list_work_items`、`get_work_item`：唯讀。
- `create_work_item`、`update_work_item`：預設 `apply=false` 預覽；必須 `apply=true` 且 `OPENPROJECT_ENABLE_WRITES=true` 才寫入。
- HTTP：預設僅允許 HTTPS。內網若不得已使用 HTTP，必須同時設定 `OPENPROJECT_ALLOW_HTTP=true` 與 `OPENPROJECT_HTTP_ALLOWED_HOST=example.internal`（與 URL hostname 完全一致）。HTTP 的 Token 傳輸沒有加密，應優先改為 HTTPS，並限制網段／權限。
- 使用最小權限專用 Token，並保持 OpenCode 寫入工具 `ask` 權限。

## 測試順序
1. `opencode mcp list` 檢查連線。
2. 在聊天呼叫 `openproject_project_options` 查詢專案。
3. 呼叫 `openproject_list_work_items` 核對已存在工作項目。
4. `create_work_item(apply=false)` 檢查預覽。
5. 明確確認後再開啟 writes，測試建立、更新並比對 OpenProject 網頁。

HTTP 401 檢查 Token，403 檢查權限，404 檢查 API/專案；`Missing OPENPROJECT_PROJECT_ID` 代表可能使用到不相容舊版 server.py。
