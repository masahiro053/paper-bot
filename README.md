# Daily AI Research Bot for Marketing Optimization

## 概要
最新のデータサイエンスおよびマーケティング領域の学術論文（arXiv）を毎朝自動で取得し、

LLMを用いて「ビジネス実務に即した形式」に要約してLINEへ配信する自動化パイプラインです。

## 着想の背景（Motivation）
日々のメディアプランニングやデータ分析業務において、Marketing Mix Modeling（MMM）や因果推論、状態空間モデルといった高度な統計手法の最新トレンドをキャッチアップすることは不可欠です。しかし、英語の学術論文を毎日スクリーニングし、実務への応用可能性を評価するには膨大な時間がかかります。
この課題を解決するため、「専門的で難解な一次情報を、通勤時間中のスマートフォンで直感的に理解でき、かつ明日の業務のアイデアの種になるレベルまで咀嚼して届ける」ことを目的とした自動化システムの開発に至りました。

## 主な機能と特徴（Features）

* **完全自動の定期配信パイプライン**
    GitHub ActionsのCron機能を活用し、毎朝07:00に最新の論文情報がLINEに届くサーバーレスな定期実行環境を構築しています。
* **実務解像度に合わせた高度な検索ロジック**
    arXiv APIに対して、大カテゴリ（Marketing Data, Advertising等）と小カテゴリ（Bayesian, Gradient Boosting等）を掛け合わせたAND検索クエリを動的に生成し、ノイズを排除した精度の高いターゲティングを実現しています。
* **ビジネスパーソン向けのLLMプロンプトエンジニアリング**
    Gemini 2.5 Flash APIを活用し、単なる直訳ではなく「ターゲット読者（ビジネスパーソン）」を指定した上で、「背景」「賢いアプローチ」「結論」「実務へのヒント」という4つの構造化されたフォーマットでの出力を強制しています。これにより、学術的な正確性を保ちつつ、LINEのチャット画面での圧倒的な視認性と納得感を実現しました。
* **関心の変化に強いモジュール設計**
    検索キーワードやプロンプトのテンプレート、取得件数などの可変パラメーターを `config.py` に分離し、メインの処理ロジック（`main.py`）と切り離すことで、今後の関心領域の変化にもノーコードで対応できる高い保守性を確保しています。

## 使用技術（Tech Stack）

* **言語:** Python 3.10
* **外部API:**
    * Gemini 2.5 Flash API (Google Gen AI SDK) - 高度な自然言語処理・要約生成
    * LINE Messaging API - モバイル端末へのPush通知
    * arXiv API - 学術論文データのXML取得
* **インフラ・CI/CD:** GitHub Actions (Ubuntu環境での自動実行)
* **主要ライブラリ:** `requests`, `xml.etree.ElementTree`, `google-genai`

## システムアーキテクチャ（Architecture）

1.  **Trigger:** GitHub Actionsが毎朝07:00（JST）にワークフローを起動。
2.  **Fetch:** `config.py` のキーワードに基づき、arXiv APIから最新の論文データ（XML）を取得・パース。
3.  **Summarize:** Gemini 2.5 Flash APIに対して、論文のタイトル・概要とシステムプロンプトを送信し、構造化された要約テキストを生成。
4.  **Notify:** 生成されたテキストをLINE Messaging API経由で指定のユーザー端末へPush送信。

## 実行環境の構築（Setup）

ローカル環境で動作確認を行う場合の手順です。

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
- GEMINI_API_KEY: Gemini APIの認証キー
- LINE_CHANNEL_ACCESS_TOKEN: LINE Botのアクセストークン
- LINE_USER_ID: 送信先のLINEユーザーID

4. スクリプトの実行
```bash
python main.py
```
