[private]
_ := require("uv")

# Display available recipes
[default]
[group('general')]
help:
    @just --list --unsorted

# Generate Emoji Pack
[group('general')]
generate *ARGS:
    uv run emojipack generate {{ ARGS }}

# Generate Emoji Pack and open with Alfred
[group('general')]
install: generate
    open "Emoji Pack.alfredsnippets"

# Hack to perform string interpolation on variables. Render the content of
# the variables in a just subprocess, passing in the is_dependency() value.
# In the subprocess, is_dependency() is always false.
# Usage, user mode: {{ user-functions + is_dependency() }}
# Usage, agent mode: {{ agent-functions + is_dependency() }}
user-functions := 'load () { source <(just _user-functions $1); }; load '
agent-functions := 'load () { source <(just _agent-functions $1); }; load '

# Common functions for all recipes
[group('internal')]
[private]
_common-functions:
    #!/bin/cat
    # exit_with: run command and exit with original status
    exit_with () { local s=$?; "$@"; exit $s; }

# Common functions for developer recipes, with colored output
[group('internal')]
[private]
_user-functions isdep: _common-functions
    #!/bin/cat
    # echo-style STYLE ARGS...
    # Print ARGS in with STYLE.
    echo-style () {
        # Uncomment following line to ignore style if stdout is not a tty.
        # [ ! -t 1 ] && { shift; echo "$*"; return; }
        case "$1" in
            command) echo -n "{{ style('command') }}" ;;
            error) echo -n "{{ style('error') }}" ;;
            okay) echo -en '\033[1;92m' ;;
            warning) echo -en '\033[1;93m' ;;
        esac
        shift; echo -e "$*{{ NORMAL }}"
    }
    show () { echo-style command "$*"; "$@"; }
    okay () { echo-style okay "✅ $*"; }
    warning () { echo-style warning "⚠️  $*"; }
    error () { echo-style error "❌ $*"; }
    # No success output when running as dependency.
    if {{ isdep }}; then okay () { :; }; fi

# Common functions for agent recipes, monochrome output
[group('internal')]
[private]
_agent-functions isdep: _common-functions
    #!/bin/cat
    okay () { echo "✅ ${*:-OK}"; }
    # No output when running as dependency
    if {{ isdep }}; then okay () { :; }; fi
    warning () { echo "⚠️  $*"; }
    error () { echo "❌ $*"; }

# Development workflow: format, test, check
[group('developer')]
[no-exit-message]
dev: format test check-compile check-ruff check-types
    #!/usr/bin/env bash -euo pipefail
    {{ user-functions + is_dependency() }}
    okay "Development checks ok."

python_dirs := "src tests"

# Remove caches and build files
[group('developer')]
clean:
    find {{ python_dirs }} -type d -name '__pycache__' | xargs rm -rf
    rm -rf .*_cache .venv build

# Agent workflow: minimal output version of dev, no reformatting
[group('agent')]
[no-exit-message]
agent:
    #!/usr/bin/env bash -euo pipefail
    # Do not reformat code in agent mode, to prevent desync with agent state.
    {{ agent-functions + is_dependency() }}
    quietly () {
        echo -n "$1... "; shift
        local output=$("$@" >&1) \
        && echo OK || { local s=$?; echo FAIL; echo -n "$output"; return $s; }
    }
    quietly "Test suite" just agent-test \
    && quietly "Static analysis" just agent-check \
    && quietly "Code style" just agent-check-format \
    && okay \
    || exit_with error FAIL

# Run test suite
[group('developer')]
[no-exit-message]
test *ARGS:
    uv run --dev pytest --no-header {{ ARGS }}

# Run test suite in agent mode (less output)
[group('agent')]
[no-exit-message]
agent-test *ARGS:
    @uv run --dev pytest --no-header --quiet --tb=short {{ ARGS }}

# Static code analysis and style checks
[group('developer')]
[no-exit-message]
check: check-compile check-format check-ruff check-types

[private]
[group('agent')]
[no-exit-message]
agent-check: agent-check-compile agent-check-ruff agent-check-types

# Check that all Python files compile
[private]
[group('developer')]
[no-exit-message]
check-compile:
    uv run -m compileall -q {{ python_dirs }}

# Check that all Python files compile (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-compile:
    @uv run -m compileall -q {{ python_dirs }}

# Ruff static analysis only
[private]
[group('developer')]
[no-exit-message]
check-ruff: check-format
    #!/usr/bin/env bash -euo pipefail
    # Do check-format first to produce the appropriate error message.
    {{ user-functions + is_dependency() }}
    show uv run --dev ruff check --quiet {{ python_dirs }} \
    || exit_with error "Ruff check failed. Try 'just ruff-fix' to fix." \
    && okay "Ruff check passed."

# Ruff static analysis only (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-ruff: agent-check-format
    #!/usr/bin/env bash -euo pipefail
    {{ agent-functions + is_dependency() }}
    uv run --dev ruff check --quiet {{ python_dirs }} \
    || exit_with error "Ruff check failed. Try 'just ruff-fix' to fix."

# Ruff auto-fix (unsafe fixes enabled)
[group('developer')]
ruff-fix:
    uv run --dev ruff check --fix --unsafe-fixes {{ python_dirs }}

# Type checking with ty and mypy
[group('developer')]
[no-exit-message]
check-types:
    #!/usr/bin/env bash -euo pipefail
    {{ user-functions + is_dependency() }}
    show uv run --dev ty check && (
        show uv run --dev mypy \
        || exit_with warning "mypy found issues that ty did not."
    ) \
    && okay "Type checks passed." \
    || exit_with error "Type check failed. Manual fix required."

# Type checking with ty and mypy (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-types:
    #!/usr/bin/env bash -euo pipefail
    {{ agent-functions + is_dependency() }}
    # ty prints annoying output on success, it can be disabled with -q, but
    # that completely disables error reporting.
    quietly () { out=$("$@" 2>&1) || exit_with echo "$out"; }
    quietly uv run --dev ty check --output-format=concise \
    && uv run --dev mypy && okay

# Check code formatting
[group('developer')]
[no-exit-message]
check-format:
    #!/usr/bin/env bash -euo pipefail
    {{ user-functions + is_dependency() }}
    source <(just _user-functions {{ is_dependency() }})
    show uv run --dev ruff format --check {{ python_dirs }} \
    && show uv run --dev docformatter --check {{ python_dirs }} \
    && okay "Format checks passed." \
    || exit_with error "Format check failed. Try 'just format' to fix."

# Check code formatting (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-format:
    #!/usr/bin/env bash -euo pipefail
    {{ agent-functions + is_dependency() }}
    uv run --dev ruff format --quiet --check {{ python_dirs }} \
    && uv run --dev docformatter --check {{ python_dirs }} \
    || exit_with error "Format check failed. Try 'just format' to fix."

# Reformat code, fail if formatting errors remain
[group('developer')]
[no-exit-message]
format:
    uv run --dev ruff format {{ python_dirs }}
    uv run --dev docformatter --in-place {{ python_dirs }}
