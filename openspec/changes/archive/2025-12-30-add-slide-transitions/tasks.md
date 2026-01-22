## 1. Extend Configuration Schema

- [x] 1.1 Add `TransitionConfig` to `VideoConfig`
  - `type`: Transition type (`fade`, `slide`, `wipe`, `flip`, `clockWipe`, `none`)
  - `duration_frames`: Transition duration in frames (default: 15)
  - `timing`: Timing function (`linear`, `spring`)
- [x] 1.2 Add transition configuration section to `config/default.yaml`
- [x] 1.3 Create unit tests for configuration validation

## 2. Update Remotion Template

- [x] 2.1 Add `@remotion/transitions` package dependency
  - Add to root `package.json` (shared via pnpm workspace)
- [x] 2.2 Rewrite `VideoGenerator.tsx` template based on `TransitionSeries`
  - Use `TransitionSeries` and `TransitionSeries.Sequence`
  - Define transitions between slides with `TransitionSeries.Transition`
  - Read configuration from composition.json and apply transitions dynamically
- [x] 2.3 Support dynamic imports per transition type
  - Import all transitions: `fade`, `slide`, `wipe`, `flip`, `clockWipe`, `none`
  - Dynamically select with `getTransitionPresentation()`
- [x] 2.4 Use `none()` in `TransitionSeries.Transition` when `none` option is selected
  - Instant switching without transition effects

## 3. Extend Dynamic Code Generation

- [x] 3.1 Add configuration arguments to `get_video_generator_tsx()` in `templates.py`
  - Add `transition_type`, `transition_duration`, `transition_timing` to function signature
  - Update docstring to reflect TransitionSeries-based implementation
- [x] 3.2 Implement TypeScript code generation logic based on transition configuration
  - Add `getTransitionPresentation()` and `getTransitionTiming()` helper functions
  - Read configuration from composition.json and dynamically build transitions
  - Update `calculateTotalFrames()` to account for transition overlap
- [x] 3.3 Include transition configuration in `composition.json`
  - Add configuration in `setup_remotion_project()` and `update_composition_json()`

## 4. Integration Testing

- [x] 4.1 Template generation tests (`test_template_generation.py`)
  - Test TransitionSeries imports
  - Test reading configuration from composition.json
  - Test helper function existence
  - Test TransitionSeries component usage
  - Test transition overlap calculation
  - Test function parameter documentation
  - Added 7 test cases total
- [x] 4.2 Verify configuration changes correctly reflect in Remotion code
  - Completed composition.json reflection tests (`test_transition_integration.py`)
  - Created 3 test cases:
    - Custom configuration reflection
    - Configuration persistence on update
    - Default configuration application
- [x] 4.3 Verify existing tests continue to pass
  - All config tests (11) pass
  - Integration tests (3) pass
  - Template generation tests (7) pass
  - **All 21 tests pass**

## 5. Documentation Updates

- [x] 5.1 Add comments for transition configuration in `config/default.yaml`
- [x] 5.2 Add transition configuration explanation to README.md
  - Added transition configuration section
  - Description of available transition types
  - Explanation of timing functions
  - Added 3 configuration examples (slide, fade with spring, none)
  - Added to implemented features list
