# Change: Product Logo Asset Download and Slide Generation Integration

## Why

Currently, when generating video slides that explain products or services, we lack appropriate logos and images, forcing us to use unrelated placeholder images. This is disrespectful to the products and services and significantly degrades the video quality.

By downloading proper logos from official product websites and passing them to the LLM during slide image generation, we can represent products accurately and respectfully.

## What Changes

- When LLM determines that a product/service logo is needed during script generation, it outputs the logo URL
- Automatically download logo images from URLs specified by the LLM
- Automatically convert SVG format images to PNG
- Include downloaded assets in the slide generation prompt passed to the LLM
- Store assets in the `assets/logos/` directory for reuse across projects

## Impact

- Affected spec: `video-generation`
- Affected code:
  - `src/movie_generator/script/generator.py` - Extract logo URLs during script generation
  - `src/movie_generator/slides/generator.py` - Asset download and prompt integration
  - `src/movie_generator/project.py` - Asset directory management
- New additions:
  - `src/movie_generator/assets/` - Asset management module (download, SVG→PNG conversion)
