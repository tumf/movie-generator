## ADDED Requirements

### Requirement: Firecrawl summaryによる事前コンテンツ品質チェック
システムは、WebUIの`/jobs/create`とAPIの`/api/jobs`におけるジョブ作成要求に対して、Firecrawlのsummaryを取得して品質チェックを実施しなければならない (SHALL)。
summaryは前後の空白を除去したうえで200文字以上を合格とする。
品質チェックに失敗した場合、システムはエラーメッセージを返しジョブを作成してはならない。

#### Scenario: WebUI/APIで品質チェックが合格する
- **WHEN** ユーザーがURLでジョブ作成を要求する
- **AND** Firecrawl summaryが200文字以上である
- **THEN** ジョブが作成される

#### Scenario: Summaryが短すぎる
- **WHEN** ユーザーがURLでジョブ作成を要求する
- **AND** Firecrawl summaryが200文字未満である
- **THEN** エラーメッセージが返され、ジョブは作成されない

#### Scenario: Firecrawlのsummary取得に失敗する
- **WHEN** ユーザーがURLでジョブ作成を要求する
- **AND** Firecrawl APIキー未設定、タイムアウト、または取得エラーが発生する
- **THEN** エラーメッセージが返され、ジョブは作成されない
