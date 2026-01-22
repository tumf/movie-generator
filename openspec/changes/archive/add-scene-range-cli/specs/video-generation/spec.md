## ADDED Requirements

### Requirement: Scene Range Selection for Partial Video Output

The system SHALL provide a CLI option to specify a scene (section) range
and output a video containing only the phrases within that range.

#### Scenario: 単一シーンの指定

- **WHEN** `movie-generator generate <url> --scenes 2` が実行される
- **THEN** セクション2に属するフレーズのみが動画に含まれる
- **AND** 出力ファイル名は `output_scenes_2.mp4` となる
- **AND** 対応するスライド画像が使用される

#### Scenario: シーン範囲の指定

- **WHEN** `movie-generator generate <url> --scenes 1-3` が実行される
- **THEN** セクション1、2、3に属するフレーズが動画に含まれる
- **AND** 出力ファイル名は `output_scenes_1-3.mp4` となる
- **AND** セクション順にフレーズが配置される

#### Scenario: 範囲未指定時の従来動作

- **WHEN** `--scenes` オプションが指定されない
- **THEN** すべてのセクションのフレーズが動画に含まれる
- **AND** 出力ファイル名は従来通り `output.mp4` となる
- **AND** 既存のワークフローとの後方互換性が維持される

#### Scenario: 無効な範囲指定時のエラー

- **WHEN** 存在しないセクション番号が指定される（例: セクション数が3なのに `--scenes 5`）
- **THEN** 明確なエラーメッセージが表示される
- **AND** 利用可能なセクション範囲が案内される

#### Scenario: 逆順範囲指定時のエラー

- **WHEN** 開始が終了より大きい範囲が指定される（例: `--scenes 3-1`）
- **THEN** 明確なエラーメッセージが表示される
- **AND** 正しい形式の例が案内される
