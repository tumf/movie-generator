# Codebase Structure Refactoring

## Purpose

Maintain a well-structured, modular codebase that minimizes duplication, promotes reusability, and ensures type safety for the movie generator application.
## Requirements
### Requirement: Utility Module Organization

The codebase SHALL organize common utility functions into dedicated modules under `src/movie_generator/utils/`.

#### Scenario: File operations utility

- **WHEN** developers need to perform file existence checks or path operations
- **THEN** they SHALL use functions from `utils/filesystem.py`

#### Scenario: Retry logic utility

- **WHEN** developers need retry logic with exponential backoff
- **THEN** they SHALL use functions from `utils/retry.py`

#### Scenario: Subprocess execution utility

- **WHEN** developers need to execute subprocesses
- **THEN** they SHALL use helpers from `utils/subprocess.py`

#### Scenario: Text processing utility

- **WHEN** developers need text processing operations
- **THEN** they SHALL use functions from `utils/text.py`

### Requirement: Centralized Constants

The codebase SHALL consolidate all magic numbers and configuration values into `src/movie_generator/constants.py`.

#### Scenario: Video configuration constants

- **WHEN** code requires video-related configuration (FPS, resolution)
- **THEN** it SHALL reference `VideoConstants` from `constants.py`

#### Scenario: File extension constants

- **WHEN** code needs to validate or work with file extensions
- **THEN** it SHALL reference `FileExtensions` from `constants.py`

#### Scenario: Project path constants

- **WHEN** code references standard directory names
- **THEN** it SHALL reference `ProjectPaths` from `constants.py`

#### Scenario: Retry configuration constants

- **WHEN** code requires retry parameters
- **THEN** it SHALL reference `RetryConfig` from `constants.py`

### Requirement: Exception Hierarchy

The codebase SHALL define a consistent exception hierarchy in `src/movie_generator/exceptions.py`.

#### Scenario: Base exception usage

- **WHEN** raising application-specific errors
- **THEN** they SHALL inherit from `MovieGeneratorError`

#### Scenario: Configuration errors

- **WHEN** configuration-related errors occur
- **THEN** the system SHALL raise `ConfigurationError`

#### Scenario: Rendering errors

- **WHEN** rendering operations fail
- **THEN** the system SHALL raise `RenderingError`

#### Scenario: MCP communication errors

- **WHEN** MCP communication fails
- **THEN** the system SHALL raise `MCPError`

### Requirement: Function Modularity

Functions SHALL be kept concise and focused on a single responsibility, with complex functions split into smaller components.

#### Scenario: CLI function size

- **WHEN** reviewing CLI functions
- **THEN** no single function SHALL exceed 100 lines of code

#### Scenario: Scene range parsing modularity

- **WHEN** parsing scene ranges
- **THEN** the logic SHALL be split into focused sub-functions

### Requirement: Type Safety

The codebase SHALL use Python type annotations and TypedDict where appropriate to ensure type safety.

#### Scenario: Composition data typing

- **WHEN** working with composition data structures
- **THEN** the code SHALL use `CompositionData` TypedDict

#### Scenario: Phrase data typing

- **WHEN** working with phrase data structures
- **THEN** the code SHALL use `PhraseDict` TypedDict

#### Scenario: Type ignore minimization

- **WHEN** adding new code
- **THEN** developers SHALL avoid using `type: ignore` annotations unless absolutely necessary

### Requirement: Code Reusability

The codebase SHALL eliminate code duplication by extracting common patterns into reusable utilities.

#### Scenario: Duplicate pattern elimination

- **WHEN** identical logic appears in multiple locations
- **THEN** it SHALL be extracted into a shared utility function

#### Scenario: Consistent API patterns

- **WHEN** similar operations are performed across modules
- **THEN** they SHALL use the same utility function with a consistent interface

### Requirement: Webワーカーの責務分割
システムは、Webワーカーの設定・PocketBaseクライアント・生成ラッパー・ワーカーループを専用モジュールに分割し、起動経路と挙動を維持しなければならない（SHALL）。

#### Scenario: 既存の起動方法を維持する
- **WHEN** `python web/worker/main.py` を実行する
- **THEN** 既存と同じ環境変数名で設定が読み込まれる
- **AND** ワーカーが起動してジョブポーリングを開始する

