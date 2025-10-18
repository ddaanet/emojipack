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
# Usage: {{ functions + is_dependency() }}
functions := 'load-funcs () { source <(just _functions $1); }; load-funcs '

# Common functions for all recipes
[group('internal')]
[private]
_functions isdep:
    #!/bin/cat
    # exit_with: run command and exit with original status
    exit_with () { local s=$?; "$@"; exit $s; }
    # style-* : set text style.
    style-command () { echo -n "{{ style('command') }}"; }
    style-warning () { echo -n "{{ style('warning')}}"; }
    style-error () { echo -n "{{ style('error') }}"; }
    style-okay () { echo -en '\033[1;92m'; }
    style-reset () { echo -ne "{{ NORMAL }}"; }
    # echo-style STYLE ARGS... : Print ARGS in with STYLE.
    echo-style () {
        # Uncomment following line to ignore style if stdout is not a tty.
        # [ ! -t 1 ] && { shift; echo "$*"; return; }
        "style-$1"; shift
        echo -n "$*"; style-reset; echo
    }
    do-command () { echo-style command "$*"; "$@"; }
    okay () { echo-style okay "✅ ${*:-OK}"; }
    warning () { echo-style warning "⚠️  $*"; }
    error () { echo-style error "❌ $*"; }
    # No success output when running as dependency.
    if {{ isdep }}; then okay () { :; }; fi

# Display available styles
[group('internal')]
[private]
colors:
    #!/usr/bin/env bash -euo pipefail
    {{ functions + is_dependency() }}
    echo "Inline styles:"
    for x in command warning error okay reset
    do style-$x; echo -n "$x "
    done
    echo
    echo "Line styles:"
    do-command command
    for x in warning error okay
    do $x $x
    done

# Development workflow: format, test, check
[group('developer')]
[no-exit-message]
dev: format test check-compile check-ruff check-types
    #!/usr/bin/env bash -euo pipefail
    {{ functions + is_dependency() }}
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
    {{ functions + is_dependency() }}
    quietly () {
        style-command; echo -n "$1... "; shift
        output=$("$@" >&1) \
        && { style-okay; echo OK; style-reset; } \
    || {
            local s=$?
            style-error; echo FAIL
            style-reset; echo "$output"
            return $s
        }
    }
    set +e
    quietly "Test suite" just agent-test; test=$?
    quietly "Static analysis" just agent-check; check=$?
    quietly "Code style" just agent-check-format; format=$?
    set -e
    (( test == 0 && check == 0 && format == 0 )) \
    && okay || { s=$?; style-error; echo "❌ FAIL"; style-reset; exit $s; }

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
    {{ functions + is_dependency() }}
    do-command uv run --dev ruff check --quiet {{ python_dirs }} \
    || exit_with error "Ruff check failed. Try 'just ruff-fix' to fix." \
    && okay "Ruff check passed."

# Ruff static analysis only (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-ruff:
    #!/usr/bin/env bash -euo pipefail
    {{ functions + is_dependency() }}
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
    {{ functions + is_dependency() }}
    do-command uv run --dev ty check && (
        do-command uv run --dev mypy \
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
    {{ functions + is_dependency() }}
    # ty prints annoying output on success, it can be disabled with -q, but
    # that completely disables error reporting.
    quietly () { out=$("$@" 2>&1) || exit_with echo "$out"; }
    quietly uv run --dev ty check --output-format=concise && (
        uv run --dev mypy \
        || exit_with warning "mypy found issues that ty did not."
    ) && okay

# Check code formatting
[group('developer')]
[no-exit-message]
check-format:
    #!/usr/bin/env bash -euo pipefail
    {{ functions + is_dependency() }}
    do-command uv run --dev ruff format --check {{ python_dirs }} \
    && do-command uv run --dev docformatter --check {{ python_dirs }} \
    && okay "Format checks passed." \
    || exit_with error "Format check failed. Try 'just format' to fix."

# Check code formatting (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-format:
    #!/usr/bin/env bash -euo pipefail
    {{ functions + is_dependency() }}
    uv run --dev ruff format --quiet --check {{ python_dirs }} \
    && uv run --dev docformatter --check {{ python_dirs }} \
    || exit_with error "Format check failed. Try 'just format' to fix."

# Reformat code, fail if formatting errors remain
[group('developer')]
[no-exit-message]
format:
    uv run --dev ruff format {{ python_dirs }}
    uv run --dev docformatter --in-place {{ python_dirs }}
