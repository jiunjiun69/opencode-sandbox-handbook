# OpenCode Sandbox 使用手冊

因工作也會用到，因此隨手整理的 OpenCode Sandbox 使用手冊。

本專案示範如何在 **WSL + Docker Compose** 中執行 OpenCode，並連接內部或自架的 OpenAI-compatible LLM 服務。  
目標是讓 OpenCode 這類 Coding Agent 在容器中執行，只能操作指定專案資料夾，而不是直接取得整台 Windows 主機的檔案與環境權限。

---

## 為什麼要用這種方式？

OpenCode 是一種 Coding Agent，可以讀取檔案、修改檔案，也可能執行終端機指令。  
直接安裝在本機使用雖然方便，但也代表它可能接觸到較多本機資料、環境變數與工具鏈。

本方案透過 Docker 容器啟動 OpenCode，並且只把指定專案掛載到容器內的 `/workspace`。

```text
Windows / WSL
    ↓
Docker Compose
    ↓
OpenCode Container
    ↓
掛載指定專案路徑：/workspace
    ↓
OpenAI-compatible LLM Endpoint
```

這樣做的好處：

- 不需要把專案搬到 OpenCode 工具資料夾底下。
- 每次只掛載目前要開發的專案。
- OpenCode 設定集中管理。
- OpenCode session 資料保存到本機 `opencode-data/`，重啟容器後仍可保留。
- 不同專案可以透過 `PROJECT_DIR` 快速切換。
- API Key 放在本機 ignored 檔案中，不進 Git。
- 可降低 Agent 誤讀、誤改專案外部資料的風險。

---

## 專案結構

```text
opencode-sandbox-handbook/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
├── opencode-config/
│   ├── opencode.example.json
│   └── llm-key.example.txt
├── opencode-data/
│   └── .gitkeep
├── scripts/
│   ├── run-example-project.sh
│   └── run-with-project-dir.sh
└── docs/
    ├── SECURITY.md
    └── TROUBLESHOOTING.md
```

---

## 前置需求

請先確認已完成以下準備：

- Windows 已啟用 WSL。
- 已安裝 Docker Desktop。
- Docker Desktop 已啟用 WSL integration。
- 可以從 WSL 連線到你的 OpenAI-compatible LLM endpoint。
- 已取得 LLM API Key。

在 WSL 中確認 Docker 是否可用：

```bash
docker --version
docker compose version
```

如果以上指令能正常顯示版本，代表 WSL 中可以使用 Docker。

---

## 快速開始

### 1. 取得本專案

```bash
git clone https://github.com/YOUR_ACCOUNT/opencode-sandbox-handbook.git
cd opencode-sandbox-handbook
```

或將資料夾複製到 WSL home 目錄：

```bash
cp -r opencode-sandbox-handbook ~/OpenCodeSandbox
cd ~/OpenCodeSandbox
```

---

### 2. 建立 `.env`

```bash
cp .env.example .env
nano .env
```

範例：

```env
PROJECT_DIR=/mnt/d/path/to/your/project
```

Windows 路徑：

```text
D:\path\to\your\project
```

對應到 WSL 會是：

```text
/mnt/d/path/to/your/project
```

---

### 3. 建立 OpenCode 設定檔

```bash
cp opencode-config/opencode.example.json opencode-config/opencode.json
nano opencode-config/opencode.json
```

請修改以下 placeholder：

```json
"baseURL": "http://YOUR_LLM_HOST:PORT",
"model": "provider/YOUR_MODEL_NAME"
```

---

### 4. 建立本機 API Key 檔案

```bash
cp opencode-config/llm-key.example.txt opencode-config/llm-key.txt
nano opencode-config/llm-key.txt
```

檔案內只放 API Key：

```text
sk-your-api-key
```

請勿將 `llm-key.txt` 提交到 Git。

---

### 5. 啟動 OpenCode Docker Sandbox

```bash
docker compose run --rm opencode
```

啟動後，容器內的工作目錄會是：

```text
/workspace
```

而 `/workspace` 會對應到 `.env` 中設定的 `PROJECT_DIR`。

Compose 也會把本機的 `./opencode-data` 掛載到容器內的 `/root/.local/share/opencode`，用來保留 OpenCode session 等本機執行資料。

`--rm` 代表離開 TUI 後，自動移除這次產生的一次性 container；因為 session 資料已掛載到 `./opencode-data`，移除 container 後仍會保留。

---

## 切換不同專案

修改 `.env`：

```env
PROJECT_DIR=/mnt/d/path/to/another/project
```

然後重新執行：

```bash
docker compose run --rm opencode
```

也可以啟動時直接帶入：

```bash
PROJECT_DIR="/mnt/d/path/to/another/project" docker compose run --rm opencode
```

---

## 可選：使用啟動腳本

### 固定專案路徑啟動

請編輯：

```bash
scripts/run-example-project.sh
```

將裡面的 `PROJECT_DIR` 改成自己的 WSL 專案路徑。

然後執行：

```bash
chmod +x scripts/run-example-project.sh
./scripts/run-example-project.sh
```

### 以參數指定專案路徑

```bash
chmod +x scripts/run-with-project-dir.sh
./scripts/run-with-project-dir.sh /mnt/d/path/to/your/project
```

---

## 確認掛載的專案是否正確

進入 OpenCode 後，可以要求它確認目前工作目錄：

```text
請確認目前工作目錄，並列出根目錄下的主要檔案。
```

它應該要在：

```text
/workspace
```

若要從 Docker 直接確認，可以暫時覆蓋 entrypoint：

```bash
docker compose run --rm --entrypoint sh opencode -lc "pwd && ls -la /workspace"
```

---

## 重要使用提醒

如果你的目標是使用 Docker Sandbox，請不要直接在 Windows PowerShell 執行：

```bash
opencode
```

因為這可能會啟動 Windows 本機安裝的 OpenCode，而不是 Docker 容器版。

請固定使用：

```bash
cd ~/OpenCodeSandbox
docker compose run --rm opencode
```

或從 Windows PowerShell 呼叫 WSL：

```powershell
wsl bash -lc "cd ~/OpenCodeSandbox && docker compose run --rm opencode"
```
