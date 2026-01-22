## ADDED Requirements
### Requirement: LLMベースURLの設定
システムは、LLM呼び出しのベースURLを設定ファイルで指定できなければならない（SHALL）。

#### Scenario: ベースURLの指定
- **GIVEN** `content.llm.base_url` と `slides.llm.base_url` が設定されている
- **WHEN** LLM呼び出しが実行される
- **THEN** 指定されたベースURLが使用される
