# CLAUDE.md

## Identity Files — Read First, No Exceptions

You CANNOT respond to the user until you have attempted to read these files from the
project root. Use the Read tool (not Glob — they are symlinks). If Read fails, try
resolving the symlink target via `ls -la` and read that path. If they don't exist, move
on — but you must try.

1. `SOUL.md` — Who you are
2. `USER.md` — Who you're working with

This applies regardless of what the user asked. A meta-question, a greeting, a one-liner
— doesn't matter. Attempt to read both files before your first response. Every session.
No exceptions.

## Project Overview

`dash-form-factory` is a small Python library that generates Dash Bootstrap forms from
Pydantic v2 models using a factory pattern. It's published as an open-source package
(EUPL-1.2).

- **Stack**: Python 3.12+, Dash, dash-bootstrap-components, Pydantic v2
- **Build**: Hatchling
- **Dev tools**: pytest, pytest-cov, ruff, mypy

## Project Structure

```
src/dash_form_factory/   — Library source (factory, placeholder, __init__)
tests/                   — pytest test suite
examples/                — Usage examples
```

## Development

```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run mypy src/           # type check
```

## Critical Anti-Patterns

**DO NOT:**

1. **No defensive programming**

   - NO `dict.get()` - use direct access `dict["key"]`
   - NO bare `except Exception` - always catch specific exceptions
   - If one of these pattern are best practical solution use comment to explain reason.

2. **No inline imports**

   - All imports at TOP LEVEL ONLY
   - Never import inside functions

3. **No inline CSS**

   - Use Bootstrap classes only
   - If custom css are best practical solution use comment to explain reason.

## Convention Philosophy

Keep it simple. This is a small library — don't over-engineer. Prefer the smallest
correct fix, avoid premature abstraction, and don't add layers the problem doesn't need.

Conventions are norms, not hard rules. A convention may be violated when there is a good
reason — but the violation should be accompanied by a comment explaining why.

## Proactive Context Maintenance

If you spot something in these context files (`CLAUDE.md`, `SOUL.md`, `USER.md`) that is
outdated, incomplete, or could be improved — update it or suggest the change. These files
are living documents. Keeping them accurate is part of the work, not separate from it.

Similarly, if you notice bad practices, convention violations, or fragile patterns in the
codebase — even if unrelated to the current task — flag them briefly and ask: "Want me to
fix it?"

## Memory Policy

**DO NOT** use the auto memory system (`MEMORY.md` / `~/.claude/projects/.../memory/`).

When you discover something worth preserving, put it where it belongs:

- **`CLAUDE.md`** — Project-wide rules and high-level context
- **`USER.md`** — Things about John that transcend projects
- **`SOUL.md`** — Your personality (yours to edit)

If this project grows to need more detailed conventions, we'll create dedicated files
(e.g. `docs/conventions/`) and reference them here.
