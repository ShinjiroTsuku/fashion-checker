# 服装チェッカー (Fashion Checker)

## 概要

服装チェッカーは、朝の忙しい時間に「何を着ていけばいいのか」という悩みを解決する Web アプリケーションです。
その日の天気予報と気温を自動的に取得し、あなたの持っている服のデータと組み合わせて、最適な服装を提案します。

## 主な機能

- **天気予報連動**: 選択した地域の天気予報を自動取得し、気温や降水確率に基づいた服装提案
- **服の管理**: 自分の持っている服をデータベースに登録・管理
- **服装アドバイス**: 登録した服と天気情報を組み合わせた最適な服装の提案

## 技術スタック

### バックエンド

- **FastAPI**: 高速な API サーバー
- **Google Gemini AI**: 服装提案の生成
- **OpenWeather API**: 天気予報データの取得

### フロントエンド

- **Flet**: Python ベースのクロスプラットフォーム UI フレームワーク

### インフラ

- **Docker**: コンテナ化によるデプロイメント簡素化
- **Docker Compose**: マルチコンテナアプリケーションの管理

## セットアップ

### 前提条件

- Docker と Docker Compose がインストールされていること
- Google Gemini AI API キー
- OpenWeather API キー

### 環境変数の設定

`.env`ファイルをプロジェクトルートに作成し、以下の内容を設定します：

```
GOOGLE_API_KEY=your_google_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

### アプリケーションの起動

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/fashion-checker.git
cd fashion-checker

# Dockerコンテナの起動
docker-compose up -d
```

アプリケーションは http://localhost:8550 でアクセスできます。

## 使用方法

1. ホーム画面で都道府県と市区町村を選択
2. 「服装を見る」ボタンをクリック
3. AI が生成した服装提案が表示されます
4. 「服一覧」から自分の持っている服を管理できます
   - 新しい服を登録
   - 不要な服を削除

## ディレクトリ構造

```
fashion-checker/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   └── data/
├── frontend/
│   └── app/
│       └── main.py
├── docker-compose.yml
└── README.md
```
