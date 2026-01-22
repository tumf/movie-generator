## Context

現在のスライド生成パイプラインでは、すべてのスライド画像をAI（NonobananaPro via OpenRouter）で生成しています。しかし、ブログ記事には説明図、スクリーンショット、チャートなど、そのままスライドとして活用できる画像が含まれている場合があります。

ALT属性やタイトル属性が適切に設定されている画像は、内容が理解可能であり、スライドの素材として再利用する価値があります。

## Goals / Non-Goals

### Goals
- ブログ記事内の画像メタデータ（ALT、title等）を抽出してパイプラインに渡す
- LLMが画像をセクションに適切に割り当てられるようにする
- 既存の画像をスライドとして再利用可能にする
- AI生成と画像再利用を混在させて使える柔軟な設計

### Non-Goals
- 画像の内容を自動解析してALTを推測する機能（別途提案として検討）
- 画像の著作権チェック（ユーザーの責任）
- 画像の自動トリミングや加工

## Decisions

### Decision 1: 画像情報の抽出タイミング

**選択**: HTMLパース時に抽出（`parse_html()` 内）

**理由**:
- コンテンツ取得と同じフローで処理できる
- 追加のHTTP呼び出しが不要
- 後続処理（スクリプト生成）で画像情報を活用可能

### Decision 2: 画像の適用判断

**選択**: LLMに画像リストを渡し、セクション割り当てを任せる

**理由**:
- ALTテキストとセクション内容のマッチングはLLMが得意
- 「理解可能かどうか」の判断もLLMが適切に行える
- 手動での画像選択も可能（YAMLで上書き）

**代替案（却下）**:
- 固定ルール（画像順でセクションに割当）: 柔軟性に欠ける
- ユーザーが全て手動指定: 手間がかかる

### Decision 3: 画像のダウンロードとリサイズ

**選択**: ダウンロード時にPillowでリサイズ（1920x1080にフィット）

**理由**:
- 動画のアスペクト比と一致させる必要がある
- Remotionでのリサイズより事前処理の方が効率的
- 品質を維持しつつファイルサイズを最適化

## Risks / Trade-offs

### Risk 1: 外部画像のダウンロード失敗
- **軽減策**: ダウンロード失敗時はAI生成にフォールバック

### Risk 2: 低品質画像の使用
- **軽減策**: 最小解像度チェック（例: 800x600未満は除外）
- 将来的には画質スコアによるフィルタリングも検討

### Trade-off: LLMトークン使用量の増加
- 画像リストをプロンプトに含めるため、若干のトークン増
- ただし、スライド生成APIコスト削減で相殺される

## Data Model

```python
@dataclass
class ImageInfo:
    """ブログ記事から抽出した画像情報"""
    src: str              # 画像URL（絶対URL）
    alt: str | None       # ALT属性
    title: str | None     # title属性
    aria_describedby: str | None  # aria-describedbyで参照される説明テキスト
    width: int | None     # 元の幅（取得できれば）
    height: int | None    # 元の高さ（取得できれば）

@dataclass
class ParsedContent:
    metadata: ContentMetadata
    content: str
    markdown: str
    images: list[ImageInfo]  # 新規追加

@dataclass
class ScriptSection:
    title: str
    narration: str
    slide_prompt: str | None = None
    source_image_url: str | None = None  # 新規追加（排他的に使用）
```

## Open Questions

1. ALTが空や不十分な場合の判断基準は？
   - 提案: 最低10文字以上、または`title`属性で補完可能な場合のみ候補とする
2. 同一画像が複数セクションに使えるケースの扱い
   - 提案: 各セクションで個別にダウンロード（キャッシュで最適化）
