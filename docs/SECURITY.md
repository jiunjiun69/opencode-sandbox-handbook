# 安全注意事項

本儲存庫設計為可公開分享的範本。  
請務必避免將任何公司內部資訊或敏感資訊提交到 Git。

---

## 不要提交機敏資訊

請勿提交以下內容：

- API Key
- Access Token
- 內部 IP
- 內部主機名稱
- 員工帳號或員工編號
- 私人或公司內部專案路徑
- 內部 repository 名稱
- 含有機敏資訊的截圖
- 帳號密碼、連線字串、憑證檔

---

## 預設忽略的檔案

本專案預設會忽略：

```text
.env
opencode-config/llm-key.txt
opencode-config/opencode.json
opencode-data/*
```

請使用以下 example 檔案作為公開範本：

```text
.env.example
opencode-config/llm-key.example.txt
opencode-config/opencode.example.json
opencode-data/.gitkeep
```

---

## 為什麼要用 Docker 執行 OpenCode？

OpenCode 這類 Coding Agent 可以讀檔、改檔，也可能要求執行 shell 指令。  
將它放在 Docker container 中，可以降低它直接接觸整台主機的風險。

本範本只把指定專案掛載到：

```text
/workspace
```

請避免掛載過大的主機路徑，例如：

```text
/mnt/c/Users
/mnt/d
/
```

建議每次只掛載目前要開發的單一專案。

---

## 建議的 OpenCode 權限設定

```json
"permission": {
  "edit": "ask",
  "bash": "ask",
  "webfetch": "deny",
  "websearch": "deny",
  "external_directory": "deny"
}
```

設定含義：

```text
edit: 修改檔案前詢問
bash: 執行 shell 指令前詢問
webfetch: 禁止抓取網頁
websearch: 禁止網路搜尋
external_directory: 禁止存取工作目錄外部路徑
```

---

## 務必檢查 AI 產生的修改

OpenCode 產生或修改程式後，請務必檢查：

```bash
git status
git diff
```

不要讓 Agent 在沒有人工審核的情況下修改正式環境設定、部署憑證、密碼、token 或敏感基礎建設檔案。
