.PHONY: bump-patch on-merged test lint format typecheck

# Version management
bump-patch:
	uv run hatch version patch
	git add pyproject.toml
	git commit -m "chore: bump version"

# Hook for conflux on_merged
on-merged: bump-patch
	tldr warm . --lang rust
	tldr semantic index . --lang rust
	leann build openspec-spec --docs ./src

# Development
test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src/
