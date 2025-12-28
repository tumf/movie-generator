# AGENTS.md - AI Coding Agent Instructions

Instructions for AI coding assistants working in this repository.

## Project Overview

Movie Generator - A project for generating movies (details TBD in openspec/project.md).

## Quick Reference

### Build/Test/Lint Commands

```bash
# TODO: Add commands when tech stack is defined
# Example patterns for common stacks:

# Python
pip install -e ".[dev]"      # Install with dev dependencies
pytest                        # Run all tests
pytest tests/test_foo.py      # Run single test file
pytest tests/test_foo.py::test_bar  # Run single test function
pytest -k "keyword"           # Run tests matching keyword
ruff check .                  # Lint
ruff format .                 # Format
mypy src/                     # Type check

# TypeScript/Node.js
npm install                   # Install dependencies
npm test                      # Run all tests
npm test -- --grep "pattern"  # Run tests matching pattern
npx vitest run tests/foo.test.ts  # Run single test file
npm run lint                  # Lint
npm run format                # Format
npm run typecheck             # Type check

# Go
go build ./...                # Build
go test ./...                 # Run all tests
go test ./pkg/foo -run TestBar  # Run single test
golangci-lint run             # Lint
```

### Development Setup

```bash
# Start development environment
tmuxinator start              # Uses .tmuxinator.yml
```

## Code Style Guidelines

### General Principles

1. **Simplicity First** - Default to <100 lines per file/function
2. **Single Responsibility** - One purpose per module/class/function
3. **Explicit over Implicit** - Clear naming, no magic
4. **Fail Fast** - Validate inputs early, return errors promptly

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Classes | PascalCase | `UserService` |
| Functions | camelCase (JS/TS), snake_case (Python) | `getUserById`, `get_user_by_id` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES` |
| Variables | camelCase (JS/TS), snake_case (Python) | `userName`, `user_name` |

### Import Organization

Order imports in these groups (separated by blank lines):

1. Standard library / built-ins
2. Third-party packages
3. Local/project imports

### Error Handling

- Use specific error types, not generic exceptions
- Include context in error messages
- Log errors at the point of handling, not throwing
- Return errors explicitly (prefer Result types when available)

### Type Annotations

- Always use type annotations for function signatures
- Use strict type checking (mypy strict, TypeScript strict mode)
- Prefer explicit types over `any` / `Any`
- Document complex types with comments

### Documentation

- Public APIs: Required docstrings/JSDoc
- Internal functions: Brief comment if non-obvious
- Complex logic: Inline comments explaining "why"
- No commented-out code in commits

### Testing

- Test file naming: `test_*.py` or `*.test.ts`
- One assertion concept per test
- Use descriptive test names: `test_user_creation_fails_with_invalid_email`
- Arrange-Act-Assert pattern

## Repository Structure

```
├── AGENTS.md              # This file - AI agent instructions
├── CLAUDE.md              # Claude-specific instructions (symlink to AGENTS.md content)
├── openspec/              # Spec-driven development
│   ├── AGENTS.md          # OpenSpec workflow instructions
│   ├── project.md         # Project context and conventions
│   ├── specs/             # Current specifications
│   └── changes/           # Change proposals
├── .cursor/commands/      # Cursor IDE commands
├── .claude/commands/      # Claude Code commands
└── .opencode/command/     # OpenCode commands
```

## OpenSpec Integration

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

### OpenSpec Commands

| Command | Description |
|---------|-------------|
| `/openspec-proposal` | Create a new change proposal |
| `/openspec-apply` | Implement an approved change |
| `/openspec-archive` | Archive a deployed change |

## Git Workflow

### Commit Messages

Use conventional commits format:

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Branch Naming

- Feature: `feature/<change-id>` or `feat/<short-description>`
- Fix: `fix/<issue-id>` or `fix/<short-description>`
- Chore: `chore/<description>`

## Code References

When referencing code locations, use the format: `file_path:line_number`

Example: "The error handler is in `src/handlers/error.ts:42`"

## Important Reminders

1. **Read before editing** - Always read existing files before modification
2. **Small changes** - Keep PRs focused and reviewable
3. **Test coverage** - Add tests for new functionality
4. **No secrets** - Never commit credentials, API keys, or sensitive data
5. **Check openspec** - For significant changes, create a proposal first
