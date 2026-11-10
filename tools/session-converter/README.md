# OpenCode V1 → V2.2 Session JSON 轉換器

純 Python 3 標準函式庫，單一 V1 Session JSON 離線轉換成特定 V2.2 匯入格式。**不自動匯入、不修改 OpenCode 資料庫、不覆蓋輸出檔，也不會去識別化輸入或輸出。**

## Windows PowerShell（從儲存庫根目錄執行）

先把自己的匯出檔放在忽略追蹤的 `input/test.json`；目標專案需為已存在資料夾。以下全程使用相對路徑，沒有實體硬碟代號。

```powershell
New-Item -ItemType Directory -Force input, output | Out-Null
# 請自行放入 input/test.json；專案目錄使用當前目錄示範
$target = (Resolve-Path .).Path
python ./tools/session-converter/convert.py ./input/test.json --directory $target --output ./output/test.v2.json
# 檢查轉換警告，再手動匯入
opencode session import ./output/test.v2.json --directory $target
```

如想讓對話歸屬另一個專案，請將 `$target` 改為該專案的 `Resolve-Path` 結果。

## Linux / macOS

```bash
mkdir -p input output
python3 ./tools/session-converter/convert.py ./input/test.json --directory "$PWD" --output ./output/test.v2.json
opencode session import ./output/test.v2.json --directory "$PWD"
```

## 單元測試

```powershell
python -m unittest discover -s tools/session-converter -p "test_*.py" -v
```

## 已知限制及隱私

- V1 訊息必須含 `info` / `parts`；assistant 需有 providerID/modelID。
- 支援文字、reasoning、部分工具執行狀態及 data URL 附件；patch、step、compaction 等僅存 metadata，未必在 v2 原生介面顯示。
- 非 data URL 附件只保留原始 metadata，不讀取本機檔案或網路。
- 原始 V1 `info` 和 `parts` 完整保存在 metadata；**轉換檔仍可能含真實姓名、內部資料、憑證、路徑與附件**。
- 有 parentID 的子 Session 可能需要先匯入父 Session；已存在 Session 時不要刪除舊資料重試。
- 匯入支援度取決於確切 v2 版本。單元測試不等於實際端對端匯入驗證。
- **只分享程式、合成測試與文件；絕對不要提交真實 Session JSON。** `.gitignore` 是防呆，不是資料清理或完整防洩漏保證。

此工具並非 OpenCode 官方專案。
