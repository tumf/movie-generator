# Capability: data-models

Data model classes using Pydantic for type safety and validation.

## ADDED Requirements

### Requirement: Pydantic-based Domain Models

All domain model classes SHALL use Pydantic `BaseModel` instead of `@dataclass` for consistent type validation and serialization.

#### Scenario: Model instantiation with validation
- **WHEN** a model is instantiated with invalid data types
- **THEN** Pydantic raises a `ValidationError` with details

#### Scenario: Model serialization to dict
- **WHEN** `model_dump()` is called on a model instance
- **THEN** the model is serialized to a Python dictionary

#### Scenario: Model deserialization from dict
- **WHEN** `Model.model_validate(data)` is called with a dictionary
- **THEN** a validated model instance is created

### Requirement: Mutable Model Support

Domain models that require field updates after creation SHALL be configured as mutable.

#### Scenario: Phrase duration update
- **WHEN** audio generation completes
- **THEN** `Phrase.duration` field can be updated in-place

#### Scenario: Phrase timing calculation
- **WHEN** `calculate_phrase_timings()` is called
- **THEN** `Phrase.start_time` fields are updated for all phrases

### Requirement: Method Preservation

Model classes with business logic methods SHALL preserve those methods after Pydantic migration.

#### Scenario: Phrase subtitle text method
- **WHEN** `Phrase.get_subtitle_text()` is called
- **THEN** text with trailing punctuation removed is returned

### Requirement: JSON Serialization Compatibility

Model classes used for JSON output SHALL maintain compatibility with existing JSON structure.

#### Scenario: CompositionData JSON output
- **WHEN** `CompositionData` is serialized to JSON for Remotion
- **THEN** the JSON structure matches the existing format expected by Remotion

#### Scenario: VideoScript JSON parsing
- **WHEN** LLM response JSON is parsed into `VideoScript`
- **THEN** the model validates and converts the data correctly
