## Context

The current implementation only supports fade effects between slides through manual opacity calculations in the `SlideLayer` component. Remotion provides an official `@remotion/transitions` package, which allows implementing diverse transition effects more concisely.

### Current Limitations

- Fade-in/fade-out only
- Hardcoded transition duration (0.5 seconds)
- No user customization

## Goals / Non-Goals

### Goals

- Integrate Remotion's official `@remotion/transitions` package
- Enable transition type and timing configuration via YAML
- Maintain existing behavior (fade) as default

### Non-Goals

- Custom transition presentation implementation (standard offerings only)
- Per-slide individual transition configuration

## Decisions

### 1. Migration to TransitionSeries

**Decision**: Migrate from current `Sequence` + manual opacity to Remotion's `TransitionSeries` component.

**Rationale**:
- Improved maintainability by using official API
- Concise application of diverse transition effects
- Automated timing calculations

### 2. Supported Transition Types

| Type | Import | Description |
|------|--------|-------------|
| `fade` | `@remotion/transitions/fade` | Fade in/out (default) |
| `slide` | `@remotion/transitions/slide` | Slide in/out |
| `wipe` | `@remotion/transitions/wipe` | Wipe effect |
| `flip` | `@remotion/transitions/flip` | Flip effect |
| `clockWipe` | `@remotion/transitions/clock-wipe` | Clockwise wipe |
| `none` | - | No transition |

### 3. Configuration Schema

```yaml
video:
  renderer: "remotion"
  template: "default"
  output_format: "mp4"
  transition:
    type: "fade"           # fade, slide, wipe, flip, clockWipe, none
    duration_frames: 15    # Transition duration in frames
    timing: "linear"       # linear, spring
```

### 4. TypeScript Generation Strategy

Dynamically generate transition imports and presentation functions based on configuration:

```typescript
// Dynamically generated section
import { fade } from "@remotion/transitions/fade";
import { linearTiming, TransitionSeries } from "@remotion/transitions";

// Presentation function selection
const presentation = fade();
const timing = linearTiming({ durationInFrames: 15 });
```

## Risks / Trade-offs

### Total Frame Count Calculation During Transitions

- **Risk**: Transitions overlap both sequences, reducing total frame count
- **Mitigation**: Update `calculateTotalFrames` to account for transition duration

### Increased Package Dependencies

- **Risk**: Adding dependency on `@remotion/transitions`
- **Mitigation**: Official Remotion package ensures good version compatibility

## Migration Plan

1. New configuration fields are optional with default values
2. Existing projects work without configuration (default: `fade`, 15 frames)
3. Rollback: Setting to `none` approximates previous behavior

## Open Questions

- [ ] Should `springTiming` damping values be user-configurable? (Fixed value in initial implementation)
- [ ] Should slide and subtitle transitions be separately configurable? (Consider for future extension)
