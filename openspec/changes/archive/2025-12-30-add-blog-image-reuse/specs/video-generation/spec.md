## ADDED Requirements

### Requirement: Blog Image Extraction

The system SHALL extract image information from blog HTML content for potential reuse as slide materials.

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

### Requirement: Source Image Reference in Script

The system SHALL allow script sections to reference existing blog images instead of generating new slides.

#### Scenario: LLM Image Assignment
- **WHEN** script generation is requested
- **AND** blog content contains extractable images with meaningful alt text
- **THEN** the image list is provided to the LLM
- **AND** LLM assigns appropriate images to relevant sections
- **AND** assigned images are stored as `source_image_url` in section metadata

#### Scenario: Exclusive Slide Source
- **WHEN** a section has `source_image_url` set
- **THEN** `slide_prompt` for that section MAY be omitted
- **AND** the source image takes precedence over AI generation

#### Scenario: Manual Override
- **WHEN** user manually specifies `source_image_url` in script.yaml
- **THEN** that URL is used regardless of LLM assignment
- **AND** the image is downloaded and used as the slide

### Requirement: Source Image Download and Processing

The system SHALL download and process source images for use as slide materials.

#### Scenario: Successful Image Download
- **WHEN** a section has `source_image_url` specified
- **THEN** the image is downloaded from the URL
- **AND** the image is resized to fit 1920x1080 (maintaining aspect ratio)
- **AND** the processed image is saved as the slide for that section

#### Scenario: Image Download Failure Fallback
- **WHEN** source image download fails
- **AND** `slide_prompt` is available for the section
- **THEN** AI slide generation is used as fallback
- **AND** a warning is logged about the fallback

#### Scenario: Image Download Failure Without Fallback
- **WHEN** source image download fails
- **AND** no `slide_prompt` is available for the section
- **THEN** an error is raised indicating missing slide source
- **AND** processing continues with placeholder image

#### Scenario: Minimum Resolution Check
- **WHEN** source image is downloaded
- **AND** image resolution is below 800x600
- **THEN** the image is rejected as too low quality
- **AND** fallback to AI generation is attempted if `slide_prompt` is available
