# Video Generation Spec Delta

## MODIFIED Requirements

### Requirement: Video Rendering with Remotion

The system SHALL use Remotion to compose slide images, audio, and subtitles into a video file. Each project SHALL have its own independent Remotion project with pnpm workspace integration.

#### Scenario: Per-Project Remotion Setup
- **WHEN** a new video project is created
- **THEN** a dedicated Remotion project is generated in `projects/<name>/remotion/`
- **AND** the Remotion project is initialized via `pnpm create @remotion/video`
- **AND** TypeScript components (VideoGenerator.tsx, Root.tsx) are dynamically generated
- **AND** pnpm workspace is configured to share `node_modules/`
- **AND** `videoData.ts` is dynamically generated from phrase metadata

#### Scenario: Remotion Integration
- **WHEN** asset generation is completed on Python side
- **THEN** `composition.json` is generated with phrase/audio/slide paths and metadata
- **AND** Remotion components read `composition.json` to configure the video
- **AND** `npx remotion render` is executed with `--props` pointing to `composition.json`
- **AND** rendering happens in the project's `remotion/` directory

#### Scenario: Successful Video Composition
- **WHEN** all assets (slides, audio) are ready
- **THEN** an H.264 encoded MP4 file is output to the project directory
- **AND** subtitles are displayed synchronized with phrase timing

#### Scenario: Subtitle Synchronization
- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy

#### Scenario: Animation Effects
- **WHEN** video is generated
- **THEN** transition effects defined in Remotion template are applied
- **AND** fade and animations between slides are displayed smoothly

#### Scenario: Shared Dependencies via pnpm
- **WHEN** multiple video projects exist
- **THEN** Remotion dependencies are shared via pnpm workspace
- **AND** disk usage is minimized through pnpm's hard-link mechanism
- **AND** each project can independently specify Remotion versions in its `package.json`

#### Scenario: Remotion Version Updates
- **WHEN** `pnpm create @remotion/video` is executed
- **THEN** the latest stable Remotion version is installed
- **AND** existing projects remain on their installed versions unless manually updated

## ADDED Requirements

### Requirement: Dynamic Remotion Project Generation

The system SHALL dynamically generate Remotion projects using official tooling and Python-generated TypeScript code.

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

### Requirement: pnpm Workspace Configuration

The system SHALL use pnpm workspaces to manage Remotion projects efficiently.

#### Scenario: Workspace Definition
- **GIVEN** a `pnpm-workspace.yaml` file exists at repository root
- **WHEN** the workspace is configured
- **THEN** it includes `projects/*/remotion` as workspace members
- **AND** it includes `remotion-template` as a workspace member

#### Scenario: Dependency Installation
- **WHEN** `pnpm install` is executed at repository root
- **THEN** all workspace dependencies are installed
- **AND** `node_modules/` at root contains shared dependencies
- **AND** each project's `remotion/node_modules/` links to the shared store

#### Scenario: pnpm Not Installed
- **WHEN** `pnpm` is not available on the system
- **THEN** an informative error message is displayed
- **AND** installation instructions for pnpm are provided
- **AND** fallback to npm is NOT attempted (to ensure consistent behavior)

## REMOVED Requirements

### Requirement: Shared Remotion Directory

**Reason**: The shared `remotion/` directory at repository root is being removed in favor of per-project Remotion instances.

**Migration**: Users must run project setup to generate individual Remotion projects for existing video projects.
