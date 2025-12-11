# 🤖 VLM GUI Automation

**自然言語でGUI操作を自動化する業務特化エージェント**

> "この画面で売上一覧から12月分だけ抽出して、CSV で保存して"
> → ✨ **ボタンを探して、クリックして、操作を完了します**

**📊 [完全ステータスレポート](STATUS_REPORT.md) | 📘 [クイックスタート](QUICKSTART.md) | 📈 [開発進捗](PROGRESS.md)**

---

## 📖 概要

**VLM GUI Automation** は、非エンジニアが自然言語で業務システムを操作できる、
Vision-Language Model（VLM）ベースの GUI 自動化エージェントです。

### 特徴

- 🗣️ **自然言語で指示**
  - 「この画面でボタンBを押して」
  - 「最初のボタンをクリック」
  - 「フィルタから2024年12月を選択」

- 👁️ **画面を理解**
  - Qwen2.5-VL-32B がボタン・入力欄・テーブルを自動認識
  - スクリーンショット → UI要素検出 → 座標マッピング

- 🛡️ **安全性重視**
  - 危険な操作（削除・支払い・送信）を自動ブロック
  - Rule Engine でアプリ別・画面別ルール設定可能
  - 人間承認フロー（セミ自律エージェント）

- 🎯 **業務特化設計**
  - 対象: 日本の中小〜中堅企業バックオフィス
  - Excel 対応（予定）
  - Chrome 上の業務システム対応

---

## 📊 Current Status (2025-12-12)

**Phase 5-A** (VLM adapter + HTTP endpoint + unified error handling) has been implemented and merged into `master`.

### Quality Gates: ALL PASSING ✅
- Product quality tests: **8/8 PASS** (`backend/test_product_quality.py`)
- Error handler tests: **4/4 PASS** (`backend/test_error_handler.py`)
- E2E API checks: documented in `E2E_CHECK_RESULTS.md`

### Documentation
- [Phase 5-A Summary](PHASE5A_VLM_ADAPTER_SUMMARY.md)
- [Product Quality Report](PRODUCT_QUALITY_REPORT.md)
- [Developer Quick Start](DEVELOPER_QUICKSTART.md)

### Progress vs Full Vision
- **~30%** complete (Phases 0-1 mostly done, Phase 2 partial)
- See [PRODUCT_QUALITY_REPORT.md](PRODUCT_QUALITY_REPORT.md) for details

---

## 🚀 クイックスタート

### 必須環境
- **OS:** Windows 11
- **Python:** 3.10+
- **GPU:** CUDA対応（Qwen推論時、RTX 5090推奨）
- **RAM:** 32GB+

### インストール

#### cmd.exe の場合
```cmd
# 1. リポジトリクローン
cd C:\Users\<your-name>\Desktop
git clone <repository-url>
cd vlm-gui-automation

# 2. 環境セットアップ
call activate.bat

# 3. バックエンド起動（Dummyモード）
cd backend
set USE_DUMMY_VLM=true
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

#### PowerShell の場合
```powershell
# 1. リポジトリクローン
cd C:\Users\<your-name>\Desktop
git clone <repository-url>
cd vlm-gui-automation

# 2. 環境セットアップ
conda activate vlm-gui

# 3. バックエンド起動（Dummyモード）
cd backend
$env:USE_DUMMY_VLM="true"
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

> **注:** PowerShell では `call` コマンドは使えません。`conda activate` を直接使用してください。

### 10秒デモ
```bash
cd backend
quick_test.bat
```

これで以下が自動実行されます：
1. テストページをChromeで開く
2. 画面キャプチャ＆VLM解析
3. 「新しいタブ」ボタンを自然言語でクリック ✓

---

## 💡 使い方

### 基本フロー

```bash
# 1. 対象ウィンドウを開く（Chrome, Excelなど）
start chrome https://example.com/admin

# 2. 画面をキャプチャ＆解析
cd backend
python capture_and_call.py

# 3. 自然言語で指示
python auto_click_test.py -i "フィルタボタンを押して"
python auto_click_test.py -i "2024年12月を選択"
python auto_click_test.py -i "エクスポートをクリック"
```

### API経由で使う

```python
import requests

# 画面解析
with open("screenshot.png", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/analyze_screen",
        files={"file": f}
    )
elements = response.json()["elements"]

# 自然言語でクリック
response = requests.post(
    "http://127.0.0.1:8001/api/v1/auto_click_simple",
    json={
        "user_instruction": "フィルタボタンを押して",
        "elements": elements
    }
)
print(response.json())  # → クリック成功
```

---

## 📊 アーキテクチャ

```
[自然言語指示]
    ↓
[Orchestrator] (SimpleOrchestrator or GPT-4)
    ↓ (要素選択)
[Rule Engine] (安全性チェック)
    ↓
[VLM Service] (画面解析: Qwen2.5-VL-32B)
    ↓ (UI要素 + bbox座標)
[Action Executor] (PyAutoGUI クリック実行)
    ↓
[実際のGUI操作] ✓
```

### コンポーネント

| コンポーネント | 技術 | 役割 |
|--------------|------|------|
| **VLM Service** | Qwen2.5-VL-32B (4bit量子化) | 画面解析・UI要素検出 |
| **Orchestrator** | ルールベース or GPT-4 | 自然言語 → 操作プラン |
| **Rule Engine** | JSON + 正規表現 | 危険操作ブロック |
| **Action Executor** | PyAutoGUI | 物理クリック実行 |
| **Backend** | FastAPI (Python) | REST API サーバー |
| **Frontend** | Electron + React (予定) | GUI Dashboard |

---

## 🎯 実装済み機能

### Phase 0: 環境構築 ✅
- プロジェクト構造
- Python 仮想環境
- FastAPI バックエンド
- Dummy VLMモード

### Phase 1: VLM統合 ✅
- VLMService (dummy fallback)
- `/api/v1/analyze_screen` - 画面解析API
- Screen capture script
- Test HTML page

### Phase 2: 自然言語クリック ✅
- **ActionExecutor** - PyAutoGUI クリック実行
- **SimpleOrchestrator** - ルールベース要素選択
- `/api/v1/auto_click_simple` - 自動クリックAPI
- **auto_click_test.py** - CLI ツール
  - 対話モード
  - 非対話モード: `-i "命令文"`
  - バッチモード: `-b test_cases.json`
- アクションログ記録 (`logs/actions.log`)

**テスト結果:**
```bash
$ python auto_click_test.py -i "新しいタブ"
[OK] AUTO-CLICK SUCCESSFUL
Selected Element: button '新しいタブ' (Index: 0)
✓ 画面上でボタンが実際にクリックされる
```

### Phase 3: Rule Engine ✅
- **Rule Engine** - 安全性チェック機構
  - グローバルルール（削除・支払い・送信禁止）
  - アプリ別ルール
  - 画面別ルール
  - パターンマッチング（正規表現）
- `/api/v1/check_rule` - アクション許可チェックAPI
- `/api/v1/rules/all` - ルール管理API

**テスト結果:**
```bash
$ curl -X POST http://127.0.0.1:8001/api/v1/check_rule \
  -d '{"element": {"type": "button", "text": "delete"}, ...}'
{
  "allowed": false,
  "reason": "Never click delete buttons without confirmation",
  "severity": "critical"
}
```

### Phase 3: GPT Orchestrator ✅
- **orchestrator_gpt.py** - GPT-4ベースプラン生成
- `/api/v1/generate_plan_gpt` - Multi-stepプラン生成API
- `/api/v1/execute_plan` - プラン実行API
- **plan_test.py** - GPTプラン生成＆実行テストツール

**テスト方法:**
```bash
# GPT-4プラン生成（要 OPENAI_API_KEY）
export OPENAI_API_KEY=sk-...
python plan_test.py -i "フィルタボタンを押して2024年12月を選択"

# プラン実行まで一括
python plan_test.py -i "..." --execute
```

---

## 🧪 テストコマンド

### 統合デモ（推奨）
```bash
# 全機能を一括デモ（Phase 0-3）
python final_demo.py

# カスタム指示でデモ
python final_demo.py -i "設定ボタンを押す"

# GPT-4プラン生成デモ（要 OPENAI_API_KEY）
python final_demo.py --gpt -i "フィルタを押して設定を開く"

# GPT-4プラン生成＆実行
python final_demo.py --gpt -i "..." --execute
```

### 基本テスト
```bash
# 1. サーバー起動確認
curl http://127.0.0.1:8001/

# 2. 画面解析テスト
python capture_and_call.py

# 3. 自然言語クリック
python auto_click_test.py -i "新しいタブ"
python auto_click_test.py -i "最初のボタン"
python auto_click_test.py -i "設定"
```

### バッチテスト
```bash
python auto_click_test.py -b test_cases.json
# → 7つのテストケースを自動実行
```

### Rule Engineテスト
```bash
# Python直接実行
python rule_engine.py

# API経由
curl http://127.0.0.1:8001/api/v1/rules/all
curl -X POST http://127.0.0.1:8001/api/v1/check_rule \
  -d '{"element": {"type": "button", "text": "delete"}, "app_name": "test"}'
```

---

## 📂 プロジェクト構造

```
vlm-gui-automation/
├── backend/
│   ├── main.py                      # FastAPI サーバー (9 API endpoints)
│   ├── vlm_service.py               # Qwen VLM 推論サービス
│   ├── orchestrator_simple.py       # ルールベース Orchestrator ✓
│   ├── orchestrator_gpt.py          # GPT-4 Orchestrator ✓
│   ├── rule_engine.py               # Rule Engine ✓
│   ├── action_executor.py           # PyAutoGUI クリック実行 ✓
│   ├── capture_and_call.py          # 画面キャプチャ＆解析
│   ├── auto_click_test.py           # 自然言語クリックCLI ✓
│   ├── run_full_demo.py             # 統合デモスクリプト
│   ├── quick_test.bat               # ワンコマンドデモ
│   ├── test_cases.json              # バッチテストケース
│   ├── logs/
│   │   └── actions.log              # クリック履歴 (JSON Lines)
│   └── config/
│       └── rules.json               # Rule Engine 設定
├── frontend/
│   └── static/
│       └── button_test.html         # テスト用HTMLページ
├── models/
│   └── Qwen2.5-VL-32B-Instruct/     # VLMモデル (ダウンロード中)
├── scripts/
│   └── download_model.py            # モデルDLスクリプト
├── README.md                        # このファイル
├── QUICKSTART.md                    # クイックスタートガイド
├── PROGRESS.md                      # 開発進捗レポート
└── activate.bat                     # 環境アクティベート
```

---

## 🔧 開発ロードマップ

### ✅ 完了済み
- [x] Phase 0: 環境構築
- [x] Phase 1: VLM統合
- [x] Phase 2: 自然言語クリック
- [x] Phase 3: Rule Engine
- [x] Phase 3: GPT Orchestrator統合
- [x] Phase 3: Multi-step実行

### 🚧 進行中
- [ ] Qwen モデル統合（ダウンロード 61%完了）

### 📅 今後の予定
- [ ] Qwen Real VLM推論テスト
- [ ] Excel対応
- [ ] Phase 4: Electron GUI Dashboard
- [ ] Phase 4: Windowsインストーラー
- [ ] Phase 4: ユーザーガイド（日本語）
- [ ] Phase 5: RAG（過去の成功パターン参照）

---

## 📈 パフォーマンス

| 指標 | Dummy Mode | Real VLM (予想) |
|------|-----------|----------------|
| 画面解析 | 0.5秒 | <5秒 |
| クリック実行 | 0.2秒 | 0.2秒 |
| End-to-End | <1秒 | <10秒 |

---

## ⚠️ 既知の制約

1. **Qwen推論未実装** - モデルDL進行中（61%）
2. **Single-stepのみ** - Multi-step planning未統合
3. **Excel未対応**
4. **Windows専用** - Linux/Mac未対応
5. **GUI Dashboard未実装** - CLIのみ

---

## 📝 ログとデバッグ

### アクションログ
```bash
# JSON Lines 形式
$ tail -3 backend/logs/actions.log
{"timestamp": "2025-12-11T02:41:17.975050", "action": "click", "success": true, ...}
{"timestamp": "2025-12-11T02:41:19.815887", "action": "click", "success": true, ...}
{"timestamp": "2025-12-11T02:41:21.776590", "action": "click", "success": true, ...}
```

### 画面解析結果
```bash
$ cat backend/last_analysis.json
{
  "summary": "Chrome ブラウザが表示されています...",
  "elements": [
    {"type": "button", "text": "新しいタブ", "bbox": [100, 50, 200, 80]},
    {"type": "input", "text": "検索またはURLを入力", "bbox": [300, 50, 800, 80]},
    {"type": "button", "text": "設定", "bbox": [1200, 50, 1250, 80]}
  ]
}
```

---

## 🤝 貢献

プロジェクトへの貢献を歓迎します！

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 ライセンス

[ライセンス情報を記載]

---

## 🙏 謝辞

- **Qwen Team** - Qwen2.5-VL-32B-Instruct
- **OpenAI** - GPT-4 API
- **FastAPI** - Modern Python web framework
- **PyAutoGUI** - Cross-platform GUI automation

---

## 📞 お問い合わせ

- **開発者:** [Your Name]
- **Email:** [your-email]
- **Repository:** [GitHub URL]

---

**最終更新:** 2025-12-11
**バージョン:** 0.3.0 (Phase 2-3)
**ステータス:** 実装中 🚧
