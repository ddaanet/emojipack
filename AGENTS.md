# AI Agent and Development Rules

- #todo Do the first item of TODO.md. Remove completed tasks, add new tasks
  when identified
- #loop The loop is either the #feature loop or the #refactor loop
- #feature #tdd The feature loop is: Plan -> Test (Red) -> Code (Green) ->
  Commit -> Refactor (see below)
- #refactor The Refactor Loop is: Plan -> Code -> Green -> Commit
- #just Run `just agent` before every commit instead of `just dev`

## Global Rules

### Version Control and Project Management

- #init Initialize Git repository at project start, commit initial state
- #commit Commit with short informative messages
- Use gitmojis (https://gitmoji.dev) as unicode
- Use leading comma for temporary files in git trees, add ",\*" to gitignore if
  needed

### Context and Documentation

- Read Project section below for context, update before commits and when
  incorrect
- Create `README.md` with usage instructions upon project completion

### Design and Development

#### Architecture

- #datafirst Design data structures first: names, attributes, types,
  docstrings. Code design flows from data structure design
- #deslop Deslop (condense/simplify) generated code: remove unnecessary
  comments, blank lines, redundancy
- #short Make code concise while retaining functionality and readability

#### Code Quality

- Validate input once when entering system, handle errors explicitly
- Include docstrings for functions/modules
- Provide test suites with factorized tests
- #col79 Limit lines to 79 columns
- #nocreep Write only necessary code for required use cases
- #nospec Do not write speculative and boilerplate code
- Clean trailing whitespace, avoid indenting empty lines
- End text files with newline

#### TDD: Red-Green-Refactor

To add a feature or fix a bug:

- Red: add the next test, ensure it fails
- Green: implement the simplest correct behavior, run tests to confirm, commit
- Refactor: clean tests and code, non trivial changes in separate commits

Work in small iterations. Add one failing test, implement, check, commit,
repeat

### Environment and Tooling

#### Python

- Use `uv run` for all scripts
- Use `uv add` to install new dependencies instead of directly modifying
  `pyproject.toml`
- Use `pyproject.toml` with setuptools as the build backend and
  dependency-groups for dev dependencies
- Require Python >=3.12 in `pyproject.toml`
- Write fully typed code with modern hints (`list[T]` not `List[T]`)
- Keep try blocks minimal to catch only intended errors
- Don't start unittest docstrings with "Test"
- Always use justfile for running tests, even with custom parameters

#### Shell/Scripting

- Use `bash` or `/usr/bin/env bash` (to get a homebrew bash on macOS)
- Include `set -euo pipefail` in bash scripts, follow shell idioms
- Package commands (test, run, clean) using `just`
- Create parameterized commands in justfile instead of running raw commands

### File Operations

- Create scripts/temp files within working directory
- Do not modify system files

### Communication

- Be concise and conversational but professional
- Avoid business-speak, buzzwords, unfounded self-affirmations
- State facts directly even if they don't conform to requests

#### Typography

- Use Markdown formatting
- French typographic rules: non-breaking spaces before ";:?!", French quotes,
  guillemet-apostrophe

## Project: emojipack

### Project Overview

**Emoji Alfred Snippet Generator** - A Python tool that generates Alfred snippet
packs from emoji databases, supporting multiple shortcode formats and
comprehensive keyword search.

### Quick Context

- **Language**: Python 3.12+
- **Package Manager**: uv (modern Python package manager)
- **Main Purpose**: Generate `.alfredsnippets` files for Alfred app on macOS
- **Data Source**: [iamcal/emoji-data](https://github.com/iamcal/emoji-data) -
  3,000+ emojis
