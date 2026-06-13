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