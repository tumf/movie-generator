# Video Rendering - Delta Specification

## ADDED Requirements

### Requirement: 話者情報のcomposition.jsonへの追加

生成されるcomposition.jsonには、各フレーズの話者情報が含まれなければならない（SHALL）。

#### Scenario: 話者情報を含むcomposition.json
- **GIVEN** フレーズリスト
  ```python
  [
    Phrase(text="やっほー！", persona_id="zundamon", persona_name="ずんだもん"),
    Phrase(text="こんにちは", persona_id="metan", persona_name="四国めたん")
  ]
  ```
- **AND** ペルソナ設定
  ```yaml
  personas:
    - id: "zundamon"
      subtitle_color: "#8FCF4F"
    - id: "metan"
      subtitle_color: "#FF69B4"
  ```
- **WHEN** `update_composition_json()`が呼び出される
- **THEN** composition.jsonに以下が含まれる
  ```json
  {
    "phrases": [
      {
        "text": "やっほー！",
        "personaId": "zundamon",
        "personaName": "ずんだもん",
        "subtitleColor": "#8FCF4F",
        ...
      },
      {
        "text": "こんにちは",
        "personaId": "metan",
        "personaName": "四国めたん",
        "subtitleColor": "#FF69B4",
        ...
      }
    ]
  }
  ```

#### Scenario: 単一話者の場合のcomposition.json
- **GIVEN** すべてのフレーズが同じペルソナである
- **WHEN** `update_composition_json()`が呼び出される
- **THEN** すべてのフレーズに同じ`personaId`と`subtitleColor`が設定される
- **AND** 従来の単一話者動画と同じ見た目になる

### Requirement: 話者別字幕スタイルのレンダリング

Remotionは、話者ごとに異なる字幕スタイルを適用しなければならない（SHALL）。

#### Scenario: 字幕色の適用
- **GIVEN** フレーズの`subtitleColor`が`"#8FCF4F"`である
- **WHEN** 字幕がレンダリングされる
- **THEN** 字幕の枠線色が`#8FCF4F`（緑色）になる

#### Scenario: 複数話者の字幕色切り替え
- **GIVEN** フレーズ0の`subtitleColor`が`"#8FCF4F"`である
- **AND** フレーズ1の`subtitleColor`が`"#FF69B4"`である
- **WHEN** 動画がレンダリングされる
- **THEN** フレーズ0の字幕は緑色で表示される
- **AND** フレーズ1の字幕はピンク色で表示される

### Requirement: 話者名表示の準備（将来用）

composition.jsonにはpersonaNameが含まれるが、現バージョンでは表示されない（SHALL include field but not display）。

#### Scenario: 話者名フィールドの存在
- **GIVEN** composition.jsonに`personaName`が含まれている
- **WHEN** Remotionで読み込まれる
- **THEN** フィールドは存在するが画面には表示されない
- **AND** 将来のバージョンで表示機能を追加可能

### Requirement: アバター画像フィールドの予約（将来用）

composition.jsonにavatarImageフィールドを予約するが、現バージョンでは使用しない（SHALL reserve field）。

#### Scenario: アバター画像フィールドの予約
- **GIVEN** ペルソナに`avatar_image`が設定されている
- **WHEN** composition.jsonが生成される
- **THEN** `avatarImage`フィールドは含まれない（または`null`）
- **AND** 将来のバージョンで実装可能

### Requirement: 後方互換性の維持

話者情報がないcomposition.jsonでも動作しなければならない（SHALL）。

#### Scenario: 話者情報なしのcomposition.json
- **GIVEN** composition.jsonに`personaId`や`subtitleColor`が含まれていない
- **WHEN** Remotionで読み込まれる
- **THEN** デフォルト色（#FFFFFF）で字幕が表示される
- **AND** エラーが発生しない

## TypeScript Type Definitions

### PhraseData (拡張)

```typescript
export interface PhraseData {
  text: string;
  audioFile: string;
  slideFile?: string;
  duration: number;
  personaId?: string;
  personaName?: string;
  subtitleColor?: string;
  avatarImage?: string;  // 将来用
}
```

### CompositionData (拡張)

```typescript
export interface CompositionData {
  title: string;
  fps: number;
  width: number;
  height: number;
  phrases: PhraseData[];
  transition?: TransitionConfig;
}
```

## Remotion Component Updates

### AudioSubtitleLayer (拡張)

```typescript
const AudioSubtitleLayer: React.FC<{
  audioFile: string;
  subtitle?: string;
  personaId?: string;
  personaName?: string;
  subtitleColor?: string;
}> = ({ audioFile, subtitle, subtitleColor = "#FFFFFF" }) => {
  return (
    <>
      <Audio src={staticFile(audioFile)} />
      {subtitle && (
        <div style={{
          // ... existing styles
          WebkitTextStroke: `1.5px ${subtitleColor}`,
        }}>
          {subtitle}
        </div>
      )}
    </>
  );
};
```

## API Reference

### update_composition_json (拡張)

```python
def update_composition_json(
    remotion_root: Path,
    phrases: list[Phrase],
    audio_paths: list[Path],
    slide_paths: list[Path] | None,
    personas: dict[str, PersonaConfig],  # 追加
    project_name: str = "video",
    transition: dict[str, Any] | None = None,
) -> None:
    """Update composition.json with current phrase data and persona info.

    Args:
        personas: Dictionary mapping persona_id to PersonaConfig.
        ...
    """
```
