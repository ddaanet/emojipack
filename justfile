_ := require("uv")

# Display available recipes
[default]
[group('general')]
help:
    @just --list --unsorted

# Generate Emoji Pack
[group('general')]
generate *ARGS:
    uv run emojipack-generator {{ ARGS }}

# Generate Emoji Pack and open with Alfred
[group('general')]
install: generate
    open "Emoji Pack.alfredsnippets"

STYLE_OK := '\033[1;92m'
STYLE_WARNING := '\033[1;93m'

# Development workflow: format, test, check
[group('developer')]
[no-exit-message]
dev: format test check-compile check-ruff check-types
    @echo "{{ STYLE_OK }}✅ OK{{ NORMAL }}"

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
    #!/usr/bin/env bash -uo pipefail
    # Do not reformat in agent mode, to prevent desync with agent state.
    mkdir -p build
    quietly () {
        echo -n "$1... "
        shift
        "$@" &>1 > build/agent.log
        status=$?
        if [ $status -eq 0 ]; then
            echo "OK"
        else
            echo "FAIL"
            cat build/agent.log
            return $status
        fi
    }
    run () {
        quietly "Test suite" just agent-test || return $?
        quietly "Static analysis" just agent-check || return $?
        quietly "Code style" just agent-check-format || return $?
    }
    if run; then
        echo "✅ OK"
    else
        status=$?
        echo "❌ FAIL"
        exit $status
    fi

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
# check-format must be done

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
    #!/usr/bin/env bash -uo pipefail
    # Do check-format first to produce the appropriate error message.
    show () { echo "{{ style("command") }}$@{{ NORMAL }}"; "$@"; return $?; }
    show uv run --dev ruff check --quiet {{ python_dirs }}; status=$?
    if [ $status -ne 0 ]; then
        echo -e "{{ style("error") }}❌ Ruff check failed. Try 'just ruff-fix' to fix.{{ NORMAL }}"
        exit $status
    fi

# Ruff static analysis only (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-ruff: agent-check-format
    #!/usr/bin/env bash -uo pipefail
    uv run --dev ruff check --quiet {{ python_dirs }}
    status=$?
    if [ $status -ne 0 ]; then
        echo -e "❌ Ruff check failed. Try 'just ruff-fix' to fix."
        exit $status
    fi

# Ruff auto-fix (unsafe fixes enabled)
[group('developer')]
ruff-fix:
    uv run --dev ruff check --fix --unsafe-fixes {{ python_dirs }}

# Type checking with ty and mypy
[group('developer')]
[no-exit-message]
check-types:
    #!/usr/bin/env bash -uo pipefail
    just _check-types ; status=$?
    if [ $status -ne 0 ];  then
        echo -e "{{ style("error") }}❌ Type check failed. Manual fix required.{{ NORMAL }}"
        exit $status
    fi
    echo -e "\033[1;92m✅ Type check passed.{{ NORMAL }}"

# Internal: helper for check-types
[private]
[group('developer')]
[no-exit-message]
_check-types:
    #!/usr/bin/env bash -uo pipefail
    show () { echo "{{ style("command") }}$@{{ NORMAL }}"; "$@"; return $?; }
    show uv run --dev ty check || exit $?
    show uv run --dev mypy; status=$?
    if [ $status -ne 0 ]; then
        echo -e "{{ STYLE_WARNING }}⚠️  mypy found issues that ty did not{{ NORMAL }}";
        exit $status;
    fi

# Type checking with ty and mypy (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-types:
    #!/usr/bin/env bash -uo pipefail
    just _agent-check-types; status=$?
    if [ $status -ne 0 ]; then
        echo -e "❌ Type check failed. Manual fix required."
        exit $status
    fi

# Internal: helper for agent-check-types
[private]
[group('agent')]
[no-exit-message]
_agent-check-types:
    #!/usr/bin/env bash -uo pipefail
    uv run --dev ty check --output-format=concise 2>/dev/null || exit $?
    uv run --dev mypy; status=$?
    if [ $status -ne 0 ]; then
        echo "⚠️  mypy found issues that ty did not";
        exit $status;
    fi

# Check code formatting
[group('developer')]
[no-exit-message]
check-format:
    #!/usr/bin/env bash -uo pipefail
    just _check-format; status=$?
    if [ $status -ne 0 ] ; then
        echo -e "{{ style("error") }}❌ Format check failed. Try 'just format' to fix.{{ NORMAL }}"
        exit $status
    fi

# Internal: helper for check-format
[private]
[group('developer')]
[no-exit-message]
_check-format:
    uv run --dev ruff format --quiet --check {{ python_dirs }}
    uv run --dev docformatter --check {{ python_dirs }}

# Check code formatting (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-format:
    #!/usr/bin/env bash -uo pipefail
    just _agent-check-format; status=$?
    if [ $status -ne 0 ] ; then
        echo "❌ Format check failed. Try 'just format' to fix."
        exit $status
    fi

# Internal: helper for agent-check-format
[private]
[group('agent')]
[no-exit-message]
_agent-check-format:
    @uv run --dev ruff format --quiet --check {{ python_dirs }}
    @uv run --dev docformatter --check {{ python_dirs }}

# Reformat code, fail if formatting errors remain
[group('developer')]
[no-exit-message]
format:
    uv run --dev ruff format --quiet {{ python_dirs }}
    uv run --dev docformatter --in-place {{ python_dirs }}
