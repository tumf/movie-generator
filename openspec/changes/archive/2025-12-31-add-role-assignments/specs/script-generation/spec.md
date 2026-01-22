## MODIFIED Requirements

### Requirement: Automatic Persona Role Assignment

The dialogue format prompt SHALL assign appropriate roles to personas, and the generated script SHALL include role assignment information.

#### Scenario: Two-Persona Roles
- **GIVEN** two personas are defined
- **WHEN** a dialogue format prompt is generated
- **THEN** persona 0 is designated as the "explainer" role
- **AND** persona 1 is designated as the "questioner/responder" role

#### Scenario: Three or More Persona Roles
- **GIVEN** three or more personas are defined
- **WHEN** a dialogue format prompt is generated
- **THEN** roles are assigned based on each persona's character traits
- **AND** the LLM is instructed to generate natural conversation

#### Scenario: LLM Generates Role Assignments
- **GIVEN** multiple personas are defined
- **WHEN** `generate_script()` is called with personas
- **THEN** the LLM is instructed to assign roles freely
- **AND** the LLM response includes `role_assignments` with persona_id, role, and description
- **AND** the generated `VideoScript` contains `role_assignments` field

#### Scenario: Role Assignments in Script Output
- **GIVEN** a `VideoScript` with `role_assignments` is generated
- **WHEN** the script is serialized to YAML
- **THEN** the output includes a `role_assignments` section
- **AND** each entry contains `persona_id`, `role`, and `description`

#### Scenario: Backward Compatibility Without Role Assignments
- **GIVEN** an LLM response without `role_assignments` field
- **WHEN** the response is parsed
- **THEN** the `VideoScript.role_assignments` is set to `None`
- **AND** no error is raised

## ADDED Requirements

### Requirement: RoleAssignment Data Model

The system SHALL provide a `RoleAssignment` data structure for storing persona role information.

#### Scenario: Create RoleAssignment
- **GIVEN** persona role information:
  - persona_id: "zundamon"
  - role: "解説役"
  - description: "専門知識を持ち、内容を詳しく説明する"
- **WHEN** a `RoleAssignment` is created
- **THEN** all fields are stored correctly
- **AND** the data can be serialized to dict/YAML

#### Scenario: RoleAssignment in VideoScript
- **GIVEN** a `VideoScript` with role assignments:
  ```python
  role_assignments = [
      RoleAssignment(persona_id="zundamon", role="解説役", description="..."),
      RoleAssignment(persona_id="metan", role="質問役", description="..."),
  ]
  ```
- **WHEN** the `VideoScript` is created with these assignments
- **THEN** `script.role_assignments` contains 2 entries
- **AND** each entry has the correct persona_id, role, and description
