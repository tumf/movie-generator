## 1. コンテンツ解析の拡張

- [x] 1.1 `ImageInfo` データクラスを `content/parser.py` に追加
  - src（URL）、alt、title、width、height属性を保持
- [x] 1.2 `ParsedContent` に画像リスト（`images: list[ImageInfo]`）を追加
- [x] 1.3 `parse_html()` で `<img>` タグを抽出するロジックを実装
- [x] 1.4 画像抽出のユニットテストを追加

## 2. スクリプト生成での画像参照

- [x] 2.1 `ScriptSection` に `source_image_url: str | None` フィールドを追加
- [x] 2.2 LLMプロンプトを更新して、画像リストを提供し、適切なセクションに画像を割り当てるよう指示
- [x] 2.3 `script.yaml` に `source_image_url` フィールドを含める
- [x] 2.4 スクリプト生成テストを更新

## 3. スライド生成の分岐ロジック

- [x] 3.1 `slides/generator.py` に画像ダウンロード関数を追加
  - URL から画像をダウンロードし、指定パスに保存
  - リサイズ対応（1920x1080へのフィット）
- [x] 3.2 `generate_slides_for_sections()` を拡張
  - `source_image_url` がある場合: ダウンロードして使用
  - ない場合: 従来通りAI生成
- [x] 3.3 スライド生成の統合テストを追加

## 4. ドキュメントとCLI対応

- [x] 4.1 `scripts/generate_slides.py` で新しいフィールドをサポート
- [x] 4.2 `multilang.py` の対応（多言語対応でも画像再利用）
