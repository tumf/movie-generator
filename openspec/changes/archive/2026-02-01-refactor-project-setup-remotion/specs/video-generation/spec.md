## MODIFIED Requirements
### Requirement: Dynamic Remotion Project Generation

The system SHALL dynamically generate Remotion projects using official tooling and Python-generated TypeScript code.

The implementation SHALL split setup into well-named steps so failures are easier to diagnose while preserving behavior.

#### Scenario: Remotion Project Initialization
- **WHEN** `Project.setup_remotion_project()` is called
- **THEN** `pnpm create @remotion/video` is executed with `--template blank`
- **AND** a minimal Remotion project is created in `projects/<name>/remotion/`
- **AND** the project is automatically added to pnpm workspace

#### Scenario: TypeScript Component Generation
- **WHEN** Remotion project is initialized
- **THEN** `VideoGenerator.tsx` is dynamically generated from Python template
- **AND** `Root.tsx` is dynamically generated from Python template
- **AND** `remotion.config.ts` is generated with project-specific settings
- **AND** components include proper TypeScript types and React imports

#### Scenario: Project Configuration
- **WHEN** Remotion project is set up
- **THEN** `package.json` is updated with project-specific name `@projects/<name>`
- **AND** `composition.json` is generated from phrase metadata
- **AND** TypeScript components import and read `composition.json`
- **AND** symbolic links are created from `public/audio` and `public/slides` to project asset directories
