# Changelog

すべての顕著な変更はこのファイルに記録されます。
フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいています。

## [Unreleased]

### Added（追加）
- `config.py` を新規作成し、大カテゴリ・小カテゴリの検索キーワード、取得件数、Geminiのプロンプトなどの設定値を分離

### Changed（変更）
- **プロンプトエンジニアリングの最適化**: Gemini 2.5 Flashへの指示を修正。ターゲット読者を「アイデアを探しているビジネスパーソン」と定義し、「背景・アプローチ・結論・実務へのヒント」の4項目による構造化フォーマットを強制。LINEでの視認性と実務への応用力を向上させた
- **API通信の安定化**: arXiv APIへのリクエストを `http` から `https` に変更し、`User-Agent` ヘッダーを追加してアクセス制限のリスクを軽減

### Fixed（修正）
- `main.py` のキーワードリスト定義におけるSyntaxError（閉じ括弧の重複）を修正し、GitHub Actionsでの自動実行エラー（Exit code 1）を解消
- GitHub ActionsのNode.jsバージョンアップ警告に対応するため、checkoutとsetup-pythonのアクションを最新バージョン（v4, v5）に更新


---

## [2026-06-15]

### Added（追加）
- **論文の重複排除機能**: 過去に送信した論文のIDを `history.txt` に記録・参照するロジックを `main.py` に追加し、同じ論文が二度配信されるのを防ぐ仕組みを実装
- **状態（State）の永続化**: `.github/workflows/ally_research.yml` に処理を追加し、ワークフロー実行完了後に更新された `history.txt` を自動でコミット＆プッシュする仕組みを構築

### Changed（変更）
- **取得件数の最適化**: 重複排除による配信数不足を防ぐため、arXivからの初期取得件数を3件から15件（バッファを持たせた数）に変更し、未送信のものが3件見つかるまでループするロジックへ改修

### Fixed（修正）
- **GitHub Actionsの環境警告**: Node.js 20の非推奨化に伴う警告を解消するため、環境変数 `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` をワークフローに設定
- **実行エラー（Exit code 1）の解消**: 新規論文がなく `history.txt` が生成されなかった場合に `git add` が失敗するバグを防ぐため、ファイル存在チェック (`if [ -f history.txt ]; then`) の条件分岐を追加
- `config.py` 内のコメントアウト記述ミスによる `SyntaxError` を修正

---

## [2026-06-21]

### Changed（変更）
- **検索キーワードの最適化**: `config.py` 内の arXiv 検索用キーワードリストを再構成し、論文のノイズ削減とマッチング精度を向上
  - 大カテゴリ（`MAJOR_KEYWORDS`）に `Digital Transformation` を追加し、`Marketing Mix Modeling` を小カテゴリから移動してドメインとして定義
  - 小カテゴリ（`MINOR_KEYWORDS`）における重複（`Bayesian`, `Causal Inference`）を削除
  - 実務応用への解像度を高めるため、新たな手法・技術キーワード（`Uplift Modeling`, `Attribution`, `GBDT`, `Ensemble`, `RAG`, `Agents`）を追加

  ---

## [2026-06-23]

### Added（追加）
- **APIエラーの例外処理**: `main.py` の要約生成処理（`summarize_paper`）を `try-except` ブロックで囲み、Google側のサーバー高負荷（503 UNAVAILABLE等）発生時にプログラムが強制終了せず、該当論文をスキップして処理を継続するフェイルセーフ機能を実装

### Changed（変更）
- **レート制限（Rate Limit）の厳格化**: Gemini 2.5 Flashの無料枠制限（1分間に5リクエスト）を確実に遵守するため、ループ内の待機時間（`time.sleep`）を5秒から15秒へ延長
- **取得バッファの拡張**: 既読スキップやAPIエラーによるスキップが連続した場合でも、目標配信数（3件）を確保できるよう、arXivからの初期取得件数（`fetch_count`）を15件から50件へと大幅に拡張


---


## [2026-06-26] Update: API制限への対応とシステムの堅牢性（ロバストネス）向上

### 🎯 概要 (Summary)
実運用（毎朝の自動配信）に向けて、外部API（arXiv / Gemini）の利用制限やサーバー高負荷に対するエラーハンドリングを実装し、どのような状況でもシステムが強制終了（クラッシュ）しないプロダクションレディな設計へと改修しました。

### 🚀 機能追加・改善 (Enhancements)
* **arXiv APIのエラー耐性強化**
  * 大量データ取得時のタイムアウトを防ぐため、リクエストの待機時間を余裕を持たせて設定（`timeout=60`）。
  * `429 Too Many Requests` 等のHTTPエラーを検知する `try-except` を実装し、API制限時には警告ログのみを残して安全に処理を終了するフェイルセーフを構築。
* **Gemini APIの厳格なレート制限管理（Rate Limiting）**
  * 無料枠の制限（1分間に5回まで）を確実に遵守するため、ループ内に `time.sleep(15)` を配置。
  * エラーでスキップ（`continue`）した際にも必ず15秒の待機時間を設けることで、APIリクエストの暴走による上限超過を防止。
* **取得バッファの拡張**
  * 既読論文のスキップや要約エラーが連続した場合でも、目標配信数（3件）を安定して確保できるよう、arXivからの初期取得件数を100件に拡張。

### 🐛 バグ修正 (Bug Fixes)
* **SDK互換性エラー（404 NOT FOUND）の解消**
  * 新しい `google-genai` SDK（v1beta）のエンドポイント仕様に合わせ、要約生成モデルを `gemini-1.5-flash` から互換性のある最新の `gemini-2.5-flash` へ修正。
* **変数未定義エラーの修正**
  * ループ処理前における `new_sent_ids = []` の定義漏れによる `NameError` を解消。

### 📝 備考 (Notes)
* 現在のアーキテクチャでは、毎朝の定期実行時におけるAPIリクエスト数は最大でも5回前後に収まるため、1日20回の上限クォータに対して極めて安全に稼働します。