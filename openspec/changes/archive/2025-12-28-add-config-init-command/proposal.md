# Change: Add Config Init Command

## Why

To enable users to easily obtain a sample configuration file. Currently, the default configuration exists in `config/default.yaml`, but users are often unaware of this file's existence, making it difficult to understand how to customize settings.

By implementing the `movie-generator config init` command to output the default configuration to stdout or a file, users can more easily begin customizing their settings.

## What Changes

- Add new CLI subcommand `config init`
- Output configuration to stdout by default
- Support `--output` option to specify a file path
- Include helpful comments in the output configuration
- Support YAML format only (matching the current configuration format)

## Impact

- Affected specification: `config-management`
- Affected code:
  - `src/movie_generator/cli.py` - Add new subcommand
  - `src/movie_generator/config.py` - Add configuration output functionality

---

**Note**: This is the archived English translation of the original Japanese proposal.
