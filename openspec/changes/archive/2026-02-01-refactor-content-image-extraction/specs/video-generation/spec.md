## MODIFIED Requirements
### Requirement: Blog Image Extraction

The system SHALL extract image information from blog HTML content for potential reuse as slide materials.

The implementation SHALL split extraction into testable steps (collection, normalization, resolution, filtering) while preserving behavior.

#### Scenario: Successful Image Extraction
- **WHEN** HTML content is parsed
- **THEN** all `<img>` elements are extracted
- **AND** `src` attribute is converted to absolute URL
- **AND** `alt` and `title` attributes are captured
- **AND** `aria-describedby` attribute is resolved to the referenced element's text content if present
- **AND** `width` and `height` attributes are captured if present

#### Scenario: Filtering Images by Alt Text Quality
- **WHEN** images are extracted from blog content
- **THEN** only images with meaningful description are included as slide candidates
- **AND** meaningful description is defined as: alt text (10+ characters) OR title attribute present OR aria-describedby text present
- **AND** images without any meaningful description are excluded from candidates but still tracked

#### Scenario: Relative URL Resolution
- **WHEN** image src is a relative URL
- **THEN** it is resolved to an absolute URL using the blog's base URL
- **AND** the absolute URL is stored in the image metadata

#### Scenario: Aria-Describedby Reference Resolution
- **WHEN** an `<img>` element has an `aria-describedby` attribute
- **THEN** the system looks up the element with the matching `id` in the same HTML document
- **AND** extracts the text content of that element
- **AND** stores it in the `aria_describedby` field of ImageInfo
- **AND** if the referenced element does not exist, `aria_describedby` is set to None
