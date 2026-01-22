## ADDED Requirements

### Requirement: Slide Transition Configuration

The system SHALL support configurable transitions between slides using Remotion's official `@remotion/transitions` package.

#### Scenario: Default Fade Transition

- **WHEN** video generation is requested without explicit transition configuration
- **THEN** slides transition using the `fade` effect
- **AND** the transition duration is 15 frames (0.5 seconds at 30fps)
- **AND** the timing function is `linear`

#### Scenario: Custom Transition Type Selection

- **WHEN** `video.transition.type` is set to a supported type (`fade`, `slide`, `wipe`, `flip`, `clockWipe`)
- **THEN** the specified transition effect is applied between slides
- **AND** the transition is rendered using Remotion's `TransitionSeries` component

#### Scenario: Transition Duration Configuration

- **WHEN** `video.transition.duration_frames` is specified
- **THEN** the transition effect lasts for the specified number of frames
- **AND** the total video duration is adjusted accordingly (subtracting transition overlap)

#### Scenario: Timing Function Selection

- **WHEN** `video.transition.timing` is set to `linear`
- **THEN** the transition progresses at a constant rate
- **WHEN** `video.transition.timing` is set to `spring`
- **THEN** the transition uses spring physics animation

#### Scenario: Disable Transitions

- **WHEN** `video.transition.type` is set to `none`
- **THEN** no transition effect is applied between slides
- **AND** slides switch instantaneously
- **AND** the standard `Sequence` component is used instead of `TransitionSeries`

#### Scenario: Invalid Transition Type

- **WHEN** an unsupported transition type is specified
- **THEN** a validation error is raised
- **AND** the error message lists the supported transition types

## MODIFIED Requirements

### Requirement: Video Rendering with Remotion

The system SHALL use Remotion to compose slide images, audio, and subtitles into a video file. Each project SHALL have its own independent Remotion project with pnpm workspace integration. Slide transitions SHALL be rendered using Remotion's official `@remotion/transitions` package.

#### Scenario: Per-Project Remotion Setup

- **WHEN** a new video project is created
- **THEN** a dedicated Remotion project is generated in `projects/<name>/remotion/`
- **AND** the Remotion project is initialized via `pnpm create @remotion/video`
- **AND** TypeScript components (VideoGenerator.tsx, Root.tsx) are dynamically generated
- **AND** pnpm workspace is configured to share `node_modules/`
- **AND** `videoData.ts` is dynamically generated from phrase metadata
- **AND** `@remotion/transitions` package is included as a dependency

#### Scenario: Remotion Integration

- **WHEN** asset generation is completed on Python side
- **THEN** `composition.json` is generated with phrase/audio/slide paths, metadata, and transition settings
- **AND** Remotion components read `composition.json` to configure the video and transitions
- **AND** `npx remotion render` is executed with `--props` pointing to `composition.json`
- **AND** rendering happens in the project's `remotion/` directory

#### Scenario: Successful Video Composition

- **WHEN** all assets (slides, audio) are ready
- **THEN** an H.264 encoded MP4 file is output to the project directory
- **AND** subtitles are displayed synchronized with phrase timing
- **AND** configured transition effects are applied between slides

#### Scenario: Subtitle Synchronization

- **WHEN** video is played
- **THEN** subtitles are synchronized with corresponding audio within ±0.1 second accuracy

#### Scenario: Animation Effects

- **WHEN** video is generated
- **THEN** transition effects defined in configuration are applied between slides
- **AND** transitions are rendered using Remotion's `TransitionSeries` component
- **AND** the transition presentation and timing match the configuration

#### Scenario: Shared Dependencies via pnpm

- **WHEN** multiple video projects exist
- **THEN** Remotion dependencies including `@remotion/transitions` are shared via pnpm workspace
- **AND** disk usage is minimized through pnpm's hard-link mechanism
- **AND** each project can independently specify Remotion versions in its `package.json`

#### Scenario: Remotion Version Updates

- **WHEN** `pnpm create @remotion/video` is executed
- **THEN** the latest stable Remotion version is installed
- **AND** `@remotion/transitions` version is matched to the Remotion core version
- **AND** existing projects remain on their installed versions unless manually updated
