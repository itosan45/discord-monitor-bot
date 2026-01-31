# Discord 常時監視Bot

## 概要

Discordサーバーのメッセージをリアルタイムで監視するBotです。

## セットアップ

```powershell
cd C:\Users\user\.gemini\antigravity\scratch\discord-monitor-bot
npm install
npm start
```

## 機能

| コマンド | 説明 |
|----------|------|
| `!ping` | Botの応答確認 |
| `!status` | Botの稼働状況を表示 |
| 「こんにちは」 | 自動で挨拶を返す |

## 注意事項

- `.env` ファイルにBot Tokenが含まれています。**絶対に公開しないでください**。
- 24時間稼働させる場合は、クラウドサービス（Railway、Heroku等）へのデプロイが必要です。
