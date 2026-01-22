# Data Models Specification - Delta

## ADDED Requirements

### Requirement: VideoScript Model Structure

The `VideoScript` model SHALL contain:
- `title: str` - Video title
- `description: str` - Video description
- `sections: list[ScriptSection]` - Script sections
- `role_assignments: list[RoleAssignment] | None` - Persona role assignments (for dialogue mode)

**変更内容**: `pronunciations` フィールドを削除

#### Scenario: VideoScript Model Fields

**GIVEN** a VideoScript instance
**THEN** it SHALL have `title`, `description`, `sections`, and `role_assignments` fields
**AND** it SHALL NOT have a `pronunciations` field
