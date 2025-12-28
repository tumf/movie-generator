# Change: デフォルト設定ファイル出力コマンドの追加

## Why

ユーザーが設定ファイルのサンプルを簡単に取得できるようにするため。現在、デフォルト設定は `config/default.yaml` に存在するが、ユーザーがこのファイルの存在を知らず、設定のカスタマイズ方法が分かりにくい状態となっている。

`movie-generator config init` コマンドで標準出力またはファイルにデフォルト設定を出力することで、ユーザーが設定のカスタマイズを開始しやすくする。

## What Changes

- 新しいCLIサブコマンド `config init` を追加
- デフォルトでは標準出力に設定を出力
- `--output` オプションでファイルパスを指定可能
- 出力される設定にはヘルプコメントを含める
- YAML形式のみをサポート（現在の設定形式に合わせる）

## Impact

- 影響を受ける仕様: `config-management`
- 影響を受けるコード:
  - `src/movie_generator/cli.py` - 新しいサブコマンド追加
  - `src/movie_generator/config.py` - 設定出力機能の追加
