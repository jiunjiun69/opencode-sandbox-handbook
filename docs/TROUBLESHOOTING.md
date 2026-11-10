# 常見問題排查

## 1. WSL 裡無法使用 Docker

請先確認：

```bash
docker --version
docker compose version
```

如果找不到 Docker，請確認 Docker Desktop 已啟用 WSL integration。

---

## 2. 專案路徑沒有正確掛載

檢查 `.env`：

```bash
cat .env
```

確認 `PROJECT_DIR` 是 WSL 路徑格式：

```text
/mnt/d/path/to/your/project
```

不要寫成 Windows 路徑格式：

```text
D:\path\to\your\project
```

---

## 3. OpenCode 找不到 API Key

確認 key 檔案存在：

```bash
ls -la opencode-config/llm-key.txt
```

確認 `opencode.json` 指向的是容器內路徑：

```json
"apiKey": "{file:/root/.config/opencode/llm-key.txt}"
```

請不要在 `opencode.json` 裡寫 host 端路徑。

---

## 4. 啟動時出現 UnknownError

如果你把 config 目錄掛成唯讀，例如：

```yaml
- ./opencode-config:/root/.config/opencode:ro
```

可以先改成可寫：

```yaml
- ./opencode-config:/root/.config/opencode
```

部分 OpenCode 版本可能會在 config 目錄中建立 runtime 檔案，因此整個目錄唯讀時可能啟動失敗。

---

## 5. 不小心執行到本機 OpenCode

如果你直接執行：

```bash
opencode
```

可能會啟動 host 本機安裝的 OpenCode，而不是 Docker sandbox 版本。

請使用：

```bash
docker compose run --rm opencode
```

或從 Windows PowerShell 執行：

```powershell
wsl bash -lc "cd ~/OpenCodeSandbox && docker compose run --rm opencode"
```

---

## 6. 確認 Docker image 版本

```bash
docker images | grep opencode
```

---

## 7. 清理停止的容器

通常使用 `--rm` 就會在離開後自動清除一次性 container。  
若仍需要手動清理：

```bash
docker ps -a
docker container prune
```

---

## 8. 確認目前掛載的工作目錄

可以暫時覆蓋 entrypoint 進行檢查：

```bash
docker compose run --rm --entrypoint sh opencode -lc "pwd && ls -la /workspace"
```

預期應該可以看到你設定在 `PROJECT_DIR` 的專案內容。
