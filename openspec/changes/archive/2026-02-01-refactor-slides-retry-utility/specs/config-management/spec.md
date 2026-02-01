## MODIFIED Requirements
### Requirement: Unified Slide Generation Retry Configuration

The system SHALL retrieve slide generation retry count, delay, and backoff factor from common constants.

The implementation SHALL provide a reusable retry utility so slide generation does not reimplement retry logic.

#### Scenario: Refer to Retry Constants

- **WHEN** performing retry processing in slide generation
- **THEN** reference constants from `RetryConfig`
- **AND** use `RetryConfig.MAX_RETRIES` for maximum retry attempts
- **AND** use `RetryConfig.BASE_DELAY_SECONDS` for initial delay
- **AND** use `RetryConfig.BACKOFF_FACTOR` for exponential backoff
