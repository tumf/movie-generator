# Change: ブログURLからスライド動画を一括生成するPythonスクリプト

## Why

ブログ記事などのネタURLからYouTube向けスライド動画を生成するワークフローを自動化したい。
現在の `/Users/tumf/work/study/daihon` での実験では、手動でフレーズ分割、音声生成、Remotion動画合成を行っているが、
これを一括処理するPythonスクリプトとして統合し、再利用可能なツールにする。

## What Changes

- **新規**: Python 3.13 + uv によるプロジェクト構成
- **新規**: YAMLベースの設定管理（スタイル、音声設定、出力設定の統一）
- **新規**: URLからコンテンツ抽出 → スクリプト生成パイプライン
- **新規**: VOICEVOX音声合成との統合
- **新規**: フレーズベース字幕・音声同期システム
- **新規**: Remotion/ffmpeg による動画レンダリング

## Impact

- Affected specs: `video-generation`, `config-management`（新規capability）
- Affected code: プロジェクト全体（新規構築）
- Dependencies:
  - Python 3.13 (uv管理)
  - VOICEVOX Core
  - Remotion or ffmpeg（動画合成）
  - OpenRouter/LLM API（コンテンツ生成）

## 参考

実験環境: `/Users/tumf/work/study/daihon/` の成果物
- `scripts/phrase_based_script.py`: フレーズデータ管理
- `voicevox/generate_phrases.py`: 音声生成
- `tui-video/src/VideoPhrases.tsx`: Remotionコンポーネント
- `docs/PROJECT_SUMMARY.md`: 制作フロー全体像
