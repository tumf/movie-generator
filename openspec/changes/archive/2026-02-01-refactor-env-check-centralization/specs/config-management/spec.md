## MODIFIED Requirements
### Requirement: Centralized Minimum Resolution and Project Root

The system SHALL manage minimum resolution standards and Docker environment project root as common values.

The implementation SHALL centralize environment checks and project root resolution so modules do not duplicate the logic.

#### Scenario: Apply Minimum Resolution and Project Root

- **GIVEN** `PROJECT_ROOT` environment variable is set
- **WHEN** checking minimum image resolution or resolving project root
- **THEN** constants and environment variables are applied
