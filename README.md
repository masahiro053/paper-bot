# Daily AI Research Bot for Marketing Optimization

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF.svg?logo=github-actions)](https://github.com/features/actions)
[![Gemini API](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2.svg)](https://aistudio.google.com/)
[![LINE API](https://img.shields.io/badge/LINE-Messaging_API-00C300.svg?logo=LINE)](https://developers.line.biz/)

## 📌 概要 (Overview)
本アプリケーションは、最新のデータサイエンスおよびマーケティング領域の学術論文（arXiv）を毎朝自動で取得し、LLM（Gemini 2.5 Flash）を用いて**「ビジネス実務に即した形式」に要約してLINEへ定期配信する自動化パイプライン**です。

データアナリストやメディアプランナーが、状態空間モデルや因果推論などの高度なモデリング手法の最新トレンドをキャッチアップする際、難解な英語論文をスクリーニングする膨大な手間を削減します。通勤時間のスマートフォン閲覧に最適化されたフォーマットで、明日の意思決定に繋がる「具体的なアイデアの種」を毎朝07:00に提供します。

## ✨ 主な機能 (Key Features)

1. **サーバーレスな完全自動配信 (Automated Daily Delivery)**
   - GitHub ActionsのCronトリガーを活用し、毎朝07:00（JST）にワークフローを厳密に自動実行
   - サーバー維持費ゼロのクラウドネイティブな運用を実現
2. **実務解像度に合わせた高度な検索ロジック (Advanced Filtering)**
   - arXiv APIに対し、大カテゴリ（メディアプランニング等）と小カテゴリ（ベイズ推論、勾配ブースティング等）を掛け合わせた動的なAND検索クエリを生成
   - 抽象的な概念論を弾き、数理モデルや機械学習の実務応用に特化した論文のみを抽出
3. **ビジネスパーソン特化のプロンプトエンジニアリング (Business-Oriented Summarization)**
   - LLM特有の直訳調（「〜が示唆された」等）や難解なアルゴリズム解説を排除するようシステムプロンプトを設計
   - 「🔥10秒でわかる本論文のコア」「💡明日の実務への応用ヒント」など、NewsPicks等の経済メディアを意識した具体的なビジネス見出しによる構造化出力を強制
4. **関心の変化に強いモジュール設計 (Modular Architecture)**
   - 検索キーワード、取得件数、プロンプトテンプレートなどの可変パラメーターを `config.py` に完全分離
   - メインの処理ロジック（`main.py`）を汚さずに、日々の興味関心に合わせてノーコードで柔軟なチューニングが可能

## 🛠 技術スタック (Tech Stack)
- **Language**: Python 3.10
- **LLM / AI**: Google Gen AI SDK (Gemini 2.5 Flash)
- **Data Source**: arXiv API (`xml.etree.ElementTree`)
- **Notification**: LINE Messaging API (`requests`)
- **CI/CD & Infrastructure**: GitHub Actions (Ubuntu latest)

## 📁 ディレクトリ構成 (Directory Structure)
```text
.
├── .github/workflows/
│   └── ally_reseach.yml  # GitHub Actionsの定期実行ワークフロー定義
├── config.py             # 検索キーワードやプロンプトテンプレートの設定ファイル
├── main.py               # データ取得・要約生成・LINE送信のメインロジック
├── requirements.txt      # 依存ライブラリ一覧（バージョン固定済み）
├── CHANGELOG.md          # バージョンごとの変更履歴
└── ADR.md                # アーキテクチャ決定記録（技術選定の背景と意図）
```

## 🚀 デプロイと環境構築の注意点 (Deployment Notes)
本システムはGitHub Actions上での自動実行を前提としていますが、ローカル環境での動作確認やプロンプトのテストを行う際は以下の手順を実行してください。

1. リポジトリのクローン
```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
```

2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

3. 環境変数の設定
実行時に以下の環境変数を設定してください。
- `GEMINI_API_KEY`: Gemini APIの認証キー
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Botのアクセストークン
- `LINE_USER_ID`: 送信先のLINEユーザーID

4. スクリプトの実行
```bash
python main.py
```
