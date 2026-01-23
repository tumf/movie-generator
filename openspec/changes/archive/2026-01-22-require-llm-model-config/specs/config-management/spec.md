## ADDED Requirements
### Requirement: LLMモデルの明示指定
システムは、LLM呼び出し時にモデルIDを設定ファイルから明示的に指定しなければならない（SHALL）。

#### Scenario: モデル指定の強制
- **GIVEN** 設定ファイルに `content.llm.model` と `slides.llm.model` が定義されている
- **WHEN** LLM呼び出しが実行される
- **THEN** 関数デフォルトに依存せず、設定値が渡される
