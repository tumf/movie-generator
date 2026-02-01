# Codebase Structure Refactoring

## Purpose

Refactor the Movie Generator codebase to improve maintainability, testability, and code reusability by eliminating code duplication, reducing function complexity, standardizing error handling, consolidating constants, and enhancing type safety.
## Requirements
### Requirement: Utility Module Organization
The system SHALL provide reusable utility modules for common operations including file system operations, retry logic, subprocess execution, and text processing.

#### Scenario: File system utilities are available
- **WHEN** code needs to check file existence or perform path operations
- **THEN** utilities from `src/movie_generator/utils/filesystem.py` SHALL be used

#### Scenario: Retry logic is standardized
- **WHEN** code needs to retry operations
- **THEN** utilities from `src/movie_generator/utils/retry.py` SHALL be used with exponential backoff

#### Scenario: Subprocess execution is standardized
- **WHEN** code needs to execute external commands
- **THEN** utilities from `src/movie_generator/utils/subprocess.py` SHALL be used

### Requirement: Constants Consolidation
The system SHALL define all magic numbers and strings as named constants in a centralized location.

#### Scenario: Video constants are centralized
- **WHEN** code needs FPS or resolution values
- **THEN** constants from `VideoConstants` in `src/movie_generator/constants.py` SHALL be used

#### Scenario: Project paths are standardized
- **WHEN** code needs to reference standard directory names
- **THEN** constants from `ProjectPaths` SHALL be used

### Requirement: Exception Hierarchy
The system SHALL provide a structured exception hierarchy for clear error categorization and handling.

#### Scenario: Base exception is available
- **WHEN** raising Movie Generator-specific errors
- **THEN** exceptions SHALL inherit from `MovieGeneratorError` base class

#### Scenario: Configuration errors are distinct
- **WHEN** configuration-related errors occur
- **THEN** `ConfigurationError` SHALL be raised

#### Scenario: Rendering errors are distinct
- **WHEN** rendering operations fail
- **THEN** `RenderingError` SHALL be raised

### Requirement: Function Decomposition
The system SHALL decompose overly long functions into smaller, focused functions with single responsibilities.

#### Scenario: CLI generate function is decomposed
- **WHEN** the generate command is executed
- **THEN** implementation SHALL use multiple focused functions instead of a single 400+ line function

#### Scenario: Scene range parsing is decomposed
- **WHEN** scene range arguments are parsed
- **THEN** implementation SHALL use sub-functions for different range formats

### Requirement: Type Safety
The system SHALL use proper type annotations and reduce type checking suppressions.

#### Scenario: TypedDict is used for structured data
- **WHEN** passing composition or phrase data
- **THEN** TypedDict types SHALL be used instead of plain dict

#### Scenario: Type ignore annotations are minimized
- **WHEN** code requires type hints
- **THEN** proper types SHALL be defined instead of using `type: ignore`

### Requirement: Docker Compose Environment Variable Uniqueness
The system SHALL maintain unique environment variable definitions in `web/docker-compose.yml` and eliminate duplicate keys.

#### Scenario: PocketBase environment variables have no duplicates
- **WHEN** `docker-compose config` is executed
- **THEN** PocketBase environment variables SHALL have no duplicate keys

### Requirement: Web API Utility Consolidation
The system SHALL consolidate common request utilities (IP retrieval) and datetime processing utilities used in Web API routes into reusable modules, improving maintainability without changing response content.

#### Scenario: Same utilities used across routes
- **WHEN** `api_routes.py` and `web_routes.py` perform request processing
- **THEN** IP retrieval and datetime processing SHALL use common utilities
- **AND** response content SHALL remain unchanged

### Requirement: Pydantic v2 Validation Maintenance
The system SHALL maintain empty string to `None` conversion for datetime fields in `JobResponse` using Pydantic v2 validator API.

#### Scenario: Empty datetime normalized to None
- **WHEN** `JobResponse` receives empty string datetime fields
- **THEN** those fields SHALL be converted to `None`

### Requirement: Web Worker Module Separation
The system SHALL separate web worker configuration, PocketBase client, generation wrapper, and worker loop into dedicated modules while maintaining existing startup paths and behavior.

#### Scenario: Existing startup method is maintained
- **WHEN** `python web/worker/main.py` is executed
- **THEN** configuration SHALL be loaded using the same environment variable names as before
- **AND** the worker SHALL start and begin job polling

