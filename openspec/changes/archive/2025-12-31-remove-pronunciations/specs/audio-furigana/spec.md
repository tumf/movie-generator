## REMOVED Requirements

### Requirement: Pronunciation Persistence

**Reason**: `reading` フィールドが各ナレーションに直接含まれるようになったため、`pronunciations` セクションへの保存は不要になりました。

**Migration**: 既存のスクリプトファイルに含まれる `pronunciations` は無視されます。`reading` フィールドが音声合成に使用されます。
