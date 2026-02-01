# Spec: Codebase Structure Refactoring

<!-- Original Japanese proposal: openspec-archive/changes/refactor-codebase-structure/proposal.md -->

## Purpose

Establish a well-organized codebase structure with reusable utilities, consolidated constants, clear exception hierarchy, and improved type safety to enhance maintainability, testability, and code reusability.
## Requirements
### Requirement: Utility Modules Organization
The system SHALL provide dedicated utility modules for common operations including filesystem operations, retry logic, subprocess execution, and text processing.

#### Scenario: File operations through utilities
- **WHEN** code needs to check file existence or perform path operations
- **THEN** it uses functions from `utils/filesystem.py`

#### Scenario: Retry with exponential backoff
- **WHEN** code needs to retry an operation
- **THEN** it uses retry utilities from `utils/retry.py` with configurable backoff

#### Scenario: Subprocess execution
- **WHEN** code needs to execute external commands
- **THEN** it uses helpers from `utils/subprocess.py`

### Requirement: Constants Consolidation
The system SHALL consolidate magic numbers and strings into typed constant classes covering video parameters, file extensions, project paths, and retry configuration.

#### Scenario: Video rendering with standard FPS
- **WHEN** video rendering is performed
- **THEN** it uses `VideoConstants.FPS` instead of hardcoded value 30

#### Scenario: File extension validation
- **WHEN** code validates file types
- **THEN** it uses `FileExtensions` constants

### Requirement: Exception Hierarchy
The system SHALL define a clear exception hierarchy with `MovieGeneratorError` as base class and specific exceptions for configuration, rendering, and MCP errors.

#### Scenario: Configuration error handling
- **WHEN** configuration is invalid
- **THEN** `ConfigurationError` is raised with descriptive message

#### Scenario: Rendering failure
- **WHEN** video rendering fails
- **THEN** `RenderingError` is raised

### Requirement: CLI Function Decomposition
The system SHALL decompose oversized CLI functions into smaller, focused functions with single responsibilities.

#### Scenario: Generate command broken into steps
- **WHEN** `generate()` command is executed
- **THEN** it delegates to separate functions for each phase (content fetch, script generation, audio synthesis, video rendering)

### Requirement: Dead Code Removal
The system SHALL remove unreachable code and unused functions to maintain codebase clarity.

#### Scenario: Unreachable code blocks removed
- **WHEN** code analysis identifies unreachable code
- **THEN** it is removed from the codebase

### Requirement: Type Safety Improvements
The system SHALL use TypedDict for structured data and reduce use of type ignore annotations to improve type checking.

#### Scenario: Composition data with TypedDict
- **WHEN** composition data is structured
- **THEN** it uses TypedDict definitions for type safety

#### Scenario: Reduced type ignores
- **WHEN** code is type-checked
- **THEN** the number of `type: ignore` annotations is minimized

### Requirement: Web APIユーティリティの共通化
システムは、Web APIルートで共通のリクエストユーティリティ（IP取得）と日時処理ユーティリティを再利用可能なモジュールに分割し、応答内容を変えずに保守性を向上させなければならない（SHALL）。

#### Scenario: ルート間で同一のユーティリティを使用する
- **WHEN** `api_routes.py` と `web_routes.py` がリクエスト処理を行う
- **THEN** IP取得と日時処理は共通ユーティリティを経由する
- **AND** レスポンスの内容は変更されない

### Requirement: Pydantic v2 バリデーションの維持
システムは、`JobResponse` の日時フィールドに対する空文字→`None` 変換を、Pydantic v2 のバリデータAPIで維持しなければならない（SHALL）。

#### Scenario: 空文字の日時を `None` に正規化する
- **WHEN** `JobResponse` に空文字の日時フィールドが渡される
- **THEN** そのフィールドは `None` に変換される

