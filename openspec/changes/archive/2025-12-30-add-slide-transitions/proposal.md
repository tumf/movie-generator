# Change: Support Configurable Slide Transitions

## Why

Currently, slide transitions only support manually implemented fade-in/fade-out effects. By leveraging Remotion's official `@remotion/transitions` package, we can enable more diverse and smoother transition effects through configuration.

## What Changes

- Integrate Remotion's official `@remotion/transitions` package
- Enable transition type and timing configuration via config files
- Available transitions: `fade`, `slide`, `wipe`, `flip`, `clockWipe`, `none`
- Timing configuration: duration (in frames), timing function (linear/spring)

## Impact

- Affected spec: `video-generation`
- Affected code:
  - `src/movie_generator/config.py`: Add transition configuration to `VideoConfig`
  - `src/movie_generator/video/templates.py`: New template using `TransitionSeries`
  - `config/default.yaml`: Add default transition settings
- **Non-breaking change**: Defaults to `fade` to maintain existing behavior
