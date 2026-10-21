# V1：Docker Sandbox

原始架構保留：WSL + Docker Compose，設定檔使用 [opencode.example.json](../opencode-config/opencode.example.json)。

1. 安裝 WSL、Docker Desktop，並開啟 Docker Desktop WSL integration。
2. 複製 `.env.example` 為 `.env`，設定 WSL 格式的 `PROJECT_DIR`。
3. 複製 `opencode-config/opencode.example.json` 為 `opencode-config/opencode.json`，填入自架 LLM Base URL 和模型 ID。
4. 複製 `llm-key.example.txt` 為 `llm-key.txt`，只在 ignored 本機檔案保存 Token。
5. 執行 `docker compose run --rm opencode`。

**MCP：** 範例附 Playwright 和 OpenProject 的**停用**設定；原始 Docker image 並未安裝 Python MCP Server、瀏覽器或所需依賴，不能只將 `enabled` 改為 true。若需使用，必須自行建置具備 Python/Node/瀏覽器的 image 並掛載 MCP 程式。Windows 版路徑不能在 Linux container 使用。

原始詳盡教學請見 [README](../README.md)。V2 Windows 教學見 [INSTALL_V2](./INSTALL_V2.md)。
