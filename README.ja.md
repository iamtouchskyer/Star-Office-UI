# Star Office UI

🌐 Language: [中文](./README.md) | [English](./README.en.md) | **日本語**

![Star Office UI カバー](docs/screenshots/readme-cover-2.jpg)

**マルチ Agent 協調のためのピクセル・オフィス・ダッシュボード** —— AI アシスタント（OpenClaw / ロブスター）の作業状態をリアルタイムで可視化し、「誰が何をしているか」「昨日何をしたか」「今オンラインか」を直感的に把握できます。

> 本プロジェクトは **Ring Hyacinth と Simon Lee の共同制作（co-created project）** です。

---

## ✨ 30 秒クイックスタート

```bash
# 1) リポジトリをクローン
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) 依存関係をインストール
python3 -m pip install -r backend/requirements.txt

# 3) 状態ファイルを初期化（初回のみ）
cp state.sample.json state.json

# 4) バックエンドを起動
cd backend
python3 app.py
```

**http://127.0.0.1:19000** を開き、状態を切り替えてみましょう：

> ✅ ローカル開発ではデフォルト設定のままで構いませんが、本番環境では `.env.example` を `.env` にコピーし、`FLASK_SECRET_KEY` と `ASSET_DRAWER_PASS` に十分な長さのランダム値を設定することをおすすめします（弱いパスワードやセッション漏洩を防ぐため）。

```bash
python3 set_state.py writing "ドキュメント整理中"
python3 set_state.py error "問題を検出、調査中"
python3 set_state.py idle "待機中"
```

![Star Office UI プレビュー](docs/screenshots/readme-cover-1.jpg)

---

## ✅ インストール確認（任意）

バックエンドが起動している状態で、簡単な smoke test を実行して主要エンドポイントが正常かどうかを確認できます：

```bash
python3 scripts/smoke_test.py --base-url http://127.0.0.1:19000
```

すべてのチェックが `OK` と表示されれば、Star Office UI の基本的なステータスフローが正しく動作していることを意味します。

## 📋 機能一覧

1. **ステータス可視化** —— 6 種類の状態（`idle` / `writing` / `researching` / `executing` / `syncing` / `error`）がオフィスの各エリアに自動マッピングされ、アニメーションと吹き出しでリアルタイム表示
2. **昨日メモ** —— `memory/*.md` から直近の作業記録を自動取得し、匿名化して「昨日メモ」カードとして表示
3. **マルチ Agent 協調** —— join key で他のロブスターをオフィスに招待し、全員のステータスをリアルタイム確認
4. **中英日 3 言語対応** —— CN / EN / JP をワンクリック切替、UI テキスト・吹き出し・ローディング表示すべてが連動
5. **アート資産カスタマイズ** —— サイドバーからキャラクター / 背景 / 装飾素材を管理、動的フレーム同期でちらつき防止
6. **AI 画像生成による模様替え** —— 自前の Gemini API を接続してオフィス背景を AI 生成（推奨: `nanobanana-pro` / `nanobanana-2`）; API 未接続でもコア機能は利用可能
7. **モバイル対応** —— スマホからそのまま閲覧可能、外出先からのクイックチェックに最適
8. **セキュリティ強化** —— サイドバーのパスワード保護、本番環境での弱パスワード拒否、Session Cookie 強化
9. **柔軟な公開アクセス** —— Cloudflare Tunnel でワンステップ公開、独自ドメイン / リバースプロキシにも対応
10. **デスクトップペット版** —— オプションの Tauri デスクトップラッパーで、オフィスを透明ウィンドウのデスクトップペットに（下記参照）

---

## 🚀 セットアップ

### 1) 依存関係インストール

```bash
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
```

### 2) 状態ファイル初期化

```bash
cp state.sample.json state.json
```

### 3) バックエンド起動

```bash
cd backend
python3 app.py
```

`http://127.0.0.1:19000` を開く

### 4) ステータス切替

```bash
python3 set_state.py writing "ドキュメント整理中"
python3 set_state.py syncing "進捗同期中"
python3 set_state.py error "問題を検出、調査中"
python3 set_state.py idle "待機中"
```

### 5) 公開アクセス（任意）

```bash
cloudflared tunnel --url http://127.0.0.1:19000
```

`https://xxx.trycloudflare.com` のリンクを共有するだけで OK。

---

## 🦞 OpenClaw ユーザー向け

> [OpenClaw](https://openclaw.com) をご利用中なら、以下の 3 ステップでロブスターとピクセルオフィスを深く連携できます。

### 4.1 Skill をインストール

リポジトリ内の `SKILL.md` を OpenClaw のワークスペースにコピーします：

```bash
cp SKILL.md ~/.openclaw/workspace/SKILL.md
```

ロブスターが自動的に読み込み、デプロイガイドに沿ってバックエンド起動・公開リンク設定・パスワードと API の案内まで進めてくれます。

### 4.2 ステータス自動同期

`SOUL.md`（またはエージェント設定ファイル）に以下のルールを追加すると、ロブスターがステータスを自動で更新します：

```markdown
## Star Office ステータス同期ルール
- タスク開始時：`python3 set_state.py <状態> "<説明>"` を実行してから作業開始
- タスク完了時：`python3 set_state.py idle "待機中"` を実行してから返答
```

**6 種類のステータス → 3 つのエリア：**

| ステータス | オフィスエリア | 使用場面 |
|-----------|--------------|---------|
| `idle` | 🛋 休憩エリア（ソファ） | 待機 / タスク完了 |
| `writing` | 💻 ワークエリア（デスク） | コーディング / ドキュメント作成 |
| `researching` | 💻 ワークエリア | 検索 / リサーチ |
| `executing` | 💻 ワークエリア | コマンド実行 / タスク処理 |
| `syncing` | 💻 ワークエリア | データ同期 / プッシュ |
| `error` | 🐛 バグコーナー | エラー / デバッグ |

### 4.3 他のロブスターをオフィスに招待

**Step 1：join key を準備**

バックエンドを初回起動するとき、カレントディレクトリに `join-keys.json` が存在しない場合は、`join-keys.sample.json` を元にランタイム用の `join-keys.json` が自動生成されます（例として `ocj_example_team_01` などのサンプル key が含まれます）。生成された `join-keys.json` を編集して key を追加・変更・削除できます。各 key はデフォルトで最大 3 名まで同時接続できます。

**Step 2：ゲストにプッシュスクリプトを実行してもらう**

ゲストは `office-agent-push.py` をダウンロードし、3 つの変数を入力するだけ：

```python
JOIN_KEY = "ocj_starteam02"          # あなたが割り当てたキー
AGENT_NAME = "太郎のロブスター"        # 表示名
OFFICE_URL = "https://office.hyacinth.im"  # あなたのオフィス URL
```

```bash
python3 office-agent-push.py
```

スクリプトが自動で参加し、15 秒ごとにステータスをプッシュします。ゲストのロブスターがダッシュボードに表示され、状態に応じて該当エリアに移動します。

**Step 3（任意）：ゲストも Skill をインストール**

ゲストは `frontend/join-office-skill.md` を Skill として使うこともできます。ロブスターが設定とプッシュを自動で行います。

> 詳しいゲスト参加手順は [`frontend/join-office-skill.md`](./frontend/join-office-skill.md) を参照。

---

## 📡 API リファレンス

| エンドポイント | 説明 |
|--------------|------|
| `GET /health` | ヘルスチェック |
| `GET /status` | メイン Agent のステータス取得 |
| `POST /set_state` | メイン Agent のステータス設定 |
| `GET /agents` | 全 Agent リスト取得 |
| `POST /join-agent` | ゲスト参加 |
| `POST /agent-push` | ゲストステータスプッシュ |
| `POST /leave-agent` | ゲスト退出 |
| `GET /yesterday-memo` | 昨日メモ取得 |
| `GET /config/gemini` | Gemini API 設定取得 |
| `POST /config/gemini` | Gemini API 設定変更 |
| `GET /assets/generate-rpg-background/poll` | 画像生成の進捗確認 |

---

## 🖥 デスクトップペット版（任意）

`desktop-pet/` ディレクトリには **Tauri** ベースのデスクトップラッパーが含まれており、ピクセルオフィスを透明ウィンドウのデスクトップペットにできます。

```bash
cd desktop-pet
npm install
npm run dev
```

- 起動時に Python バックエンドを自動起動
- デフォルトで `http://127.0.0.1:19000/?desktop=1` を表示
- 環境変数でプロジェクトパスや Python パスをカスタマイズ可能

> ⚠️ これは**オプションの実験的機能**であり、現在は主に macOS で開発・テストされています。詳細は [`desktop-pet/README.md`](./desktop-pet/README.md) を参照。

---

## 🎨 アート資産とライセンス

### 資産の出典

ゲストキャラクターのアニメーションには **LimeZu** のフリー素材を使用しています：
- [Animated Mini Characters 2 (Platformer) [FREE]](https://limezu.itch.io/animated-mini-characters-2-platform-free)

再配布やデモの際は出典を明記し、原作者のライセンス条項に従ってください。

### ライセンス

- **コード / ロジック：MIT**（[`LICENSE`](./LICENSE) を参照）
- **アート資産：非商用のみ**（学習 / デモ / 共有用途）

> 商用利用の場合は、すべてのアート資産をオリジナル素材に差し替えてください。

---

## 👥 プロジェクト作者

本プロジェクトは **Ring Hyacinth** と **Simon Lee** の共同制作・共同メンテナンスです。

- **Ring Hyacinth** — [@ring_hyacinth](https://x.com/ring_hyacinth)
- **Simon Lee** — [@simonxxoo](https://x.com/simonxxoo)

---

## 📝 更新履歴

| 日付 | 概要 | 詳細 |
|------|------|------|
| 2026-03-06 | 🔌 デフォルトポート変更 — OpenClaw Browser Control との競合を避けるため、バックエンドの既定ポートを 18791 から 19000 に変更。スクリプト、デスクトップシェル、ドキュメントの既定値も同期更新 | [`docs/CHANGELOG_2026-03.md`](./docs/CHANGELOG_2026-03.md) |
| 2026-03-01 | 🎉 **v2 リビルド公開** — 3 言語対応、資産管理システム、AI 画像生成による模様替え、アート資産全面刷新 | [`docs/FEATURES_NEW_2026-03-01.md`](./docs/FEATURES_NEW_2026-03-01.md) |
| 2026-03-03 | 📋 オープンソース公開チェックリスト完了 | [`docs/OPEN_SOURCE_RELEASE_CHECKLIST.md`](./docs/OPEN_SOURCE_RELEASE_CHECKLIST.md) |
| 2026-03-04 | 🔒 P0/P1 セキュリティ強化 — 弱パスワード拒否、バックエンド分割、stale ステータス自動 idle 復帰、スケルトンローディング | [`docs/UPDATE_REPORT_2026-03-04_P0_P1.md`](./docs/UPDATE_REPORT_2026-03-04_P0_P1.md) |
| 2026-03-05 | 📱 安定性修正 — CDN キャッシュ修正、画像生成非同期化、モバイルサイドバー UX 改善、join key 有効期限・同時接続制御 | [`docs/UPDATE_REPORT_2026-03-05.md`](./docs/UPDATE_REPORT_2026-03-05.md) |

---

## 📁 プロジェクト構成

```text
Star-Office-UI/
├── backend/            # Flask バックエンド
│   ├── app.py
│   ├── requirements.txt
│   └── run.sh
├── frontend/           # フロントエンドページ & 資産
│   ├── index.html
│   ├── join.html
│   ├── invite.html
│   └── layout.js
├── desktop-pet/        # Tauri デスクトップラッパー（任意）
├── docs/               # ドキュメント & スクリーンショット
│   └── screenshots/
├── office-agent-push.py  # ゲストプッシュスクリプト
├── set_state.py          # ステータス切替スクリプト
├── state.sample.json     # 状態ファイルテンプレート
├── join-keys.sample.json # Join Key テンプレート（起動時に join-keys.json を生成）
├── SKILL.md              # OpenClaw Skill
└── LICENSE               # MIT ライセンス
```

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/image?repos=ringhyacinth/Star-Office-UI&type=date&legend=top-left)](https://www.star-history.com/?repos=ringhyacinth%2FStar-Office-UI&type=date&legend=top-left)
