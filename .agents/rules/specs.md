# Rules: specs

Specs live in `specs/` and are the source of truth for behaviour. `scripts/check_spec.py`
enforces the mechanical rules below; CI runs it on every PR.

## File
- Name: `specs/<ID>-<short-kebab-name>.md`, e.g. `specs/ORD-002-cancel-order.md`.
- Start from `specs/_TEMPLATE.md`. Keep every section, even if short.
- Front matter: `id` (matches the filename), `title`, `status`, `owner` (`@github-handle`),
  `issue` (`"#<n>"` of the feature request).
- Heading: `# <ID>: <title>`.

## Status
- `draft` while questions are open. `approved` once a person has agreed it (agents never set
  `approved` on their own). `implemented` when the code is merged.
- An `approved` or `implemented` spec has no unchecked `- [ ]` open questions.

## Acceptance criteria
- Heading per criterion: `### <ID>-AC<n> [api]`, `[ui]` or `[api,ui]`. Numbers start at 1,
  are unique, and are never renumbered. Retire one with `### ~~<ID>-AC<n> [tag]~~`.
- Each has **Given** and **Then** bullets (and **When** when there is an action).
- Every **Then** is checkable: exact status codes, error codes, field names, visible text,
  URLs. Not "returns an error", "works correctly", "appropriate message".
- One behaviour per criterion. If a Then lists two unrelated outcomes, split it.
- Changing an approved criterion's meaning needs the owner's agreement in the PR.

## Agents
- Copy decisions only from the issue and its comments. Anything not decided there goes to
  Open questions and keeps the spec in `draft`.
- Run `python scripts/check_spec.py <file>` and fix every error before showing the spec.
