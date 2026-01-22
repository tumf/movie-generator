# Change: LLMによる記事内画像の適合性判定機能の追加

## Why

現在、記事内の画像は alt, title, aria-describedby の有無でフィルタリングされているが、
その画像が「現在説明しているスライドの内容に適しているか」の判定はLLMに委ねられていない。
LLMに画像の適合性を判定させることで、より適切な画像選択を実現する。

## What Changes

- LLMプロンプトに画像選択の判定基準を明示的に追加
- alt, caption（title）, aria-describedby を**総合的に判断**して、現在のセクションのスライドに適すると判断した場合のみ `source_image_url` を採用するよう指示
- 曖昧な画像や内容と関連の薄い画像は AI 生成を優先するよう誘導

## Impact

- Affected specs: `script-generation`
- Affected code:
  - `src/movie_generator/script/generator.py` (プロンプトテンプレート修正)
