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
    mkdir -p data
    cd data; uv run emojipack generate {{ ARGS }}

# Generate macOS text remplacements from Emoji Pack
[group('general')]
generate-macos:
    mkdir -p data
    cd data; uv run emojipack generate --macos

# Generate Emoji Pack and open with Alfred
[group('general')]
install: generate
    open "data/Emoji Pack.alfredsnippets"

# Compare generated pack with Joel's pack
[group('general')]
compare: generate
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    if [ ! -f data/joel.alfredsnippets ]
    then do-command curl --location --output data/joel.alfredsnippets \
        "https://joelcalifa.com/blog/alfred-emoji-snippet-pack/Emoji%20Pack.alfredsnippets"
    fi
    do-command uv run emojipack compare data/joel.alfredsnippets "data/Emoji Pack.alfredsnippets"

# Hack to perform string interpolation on variables. Render the content of
# the variables in a just subprocess, passing in the is_dependency() value.
# In the subprocess, is_dependency() is always false.
# Usage: {{ functions }} {{ is_dependency() }} {{ inner }}
inner := "false"
functions := 'load-funcs () { source <(just _functions $2 $1); }; load-funcs '

# Common functions for all recipes
[group('internal')]
[private]
_functions isdep inner:
    #!/bin/cat
    # exit-with: run command and exit with original status
    exit-with () { local s=$?; "$@"; exit $s; }
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
    do-command () {
        local cmd=""
        for arg in "$@"; do
            cmd+=$(printf "%q " "$arg")
        done
        echo-style command "${cmd% }" >&2
        "$@"
    }
    okay () { echo-style okay "✅ ${*:-OK}" >&2; }
    warning () { echo-style warning "⚠️  $*" >&2; }
    error () { echo-style error "❌ ${*:-FAIL}" >&2; }
    # No success or error output when running as dependency.
    if {{ isdep }} || {{ inner }}
    then okay () { :; }; error () { :; }
    fi
    # add-status command ...: run command and add $? to status variable
    # Can run multiple seqential commands, delaying failure.
    add-status () { set +e; "$@"; (( status = ${status:-0} + $? )); set -e; }
    # do-status: return the accumulated status
    do-status () { return ${status:-0}; }

# Display available styles
[group('internal')]
[private]
colors:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    echo "Inline styles:"
    for x in command warning error okay reset
    do style-$x; echo -n "$x "
    dones
    echo
    echo "Line styles:"
    do-command command
    for x in warning error okay
    do $x $x
    done

# Development workflow: test, check
[group('developer')]
[no-exit-message]
dev:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    just inner=true check-compile || exit-with error
    add-status just inner=true test
    add-status just inner=true check
    do-status && okay "Development checks OK" || exit-with error

python_dirs := "src tests"

# Remove caches and build files
[group('developer')]
clean:
    find {{ python_dirs }} -type d -name '__pycache__' | xargs rm -rf
    rm -rf .*_cache .venv build

# Agent workflow: minimal output version of dev
[group('agent')]
[no-exit-message]
agent:
    #!/usr/bin/env bash -euo pipefail
    # Do not reformat code in agent mode, to prevent desync with agent state.
    {{ functions }} {{ is_dependency() }} {{ inner }}
    quietly () {
        style-command; echo -n "$1... "; shift
        output=$("$@" >&1) \
        && { style-okay; echo OK; style-reset; } \
        || {
            local s=$?
            style-error; echo FAIL
            style-reset; echo "${output}"
            return $s
        }
    }
    add-status quietly "Test suite" just inner=true agent-test
    add-status quietly "Static analysis" just inner=true agent-check
    add-status quietly "Code style" just inner=true agent-check-format
    do-status && okay || exit-with error

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
check:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    # if inner=true, recipe is being run by dev recipe,
    if ! {{ inner }}
    then just inner=true check-compile || exit-with error
    fi
    add-status just inner=true check-format
    add-status just inner=true check-ruff
    add-status just inner=true check-types
    do-status && okay Static analysis and format checks passed \
    || exit-with error

[private]
[group('agent')]
[no-exit-message]
agent-check: agent-check-compile
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    add-status just inner=true agent-check-ruff
    add-status just inner=true agent-check-types
    do-status && okay || exit-with error

# Check that all Python files compile
[private]
[group('developer')]
[no-exit-message]
check-compile:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    do-command uv run -m compileall -q {{ python_dirs }} \
    && okay || exit-with error

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
check-ruff:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    do-command uv run --dev ruff check --quiet {{ python_dirs }} \
    && okay "Ruff check passed" \
    || exit-with error "Ruff check failed, try 'just ruff-fix' to fix"


# Ruff static analysis only (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-ruff:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    uv run --dev ruff check --quiet {{ python_dirs }} \
    && okay || exit-with error "Ruff check failed, try 'just ruff-fix' to fix"

# Ruff auto-fix (unsafe fixes enabled)
[group('developer')]
[no-exit-message]
ruff-fix:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    do-command uv run --dev ruff check --fix --unsafe-fixes {{ python_dirs }} \
    && okay || exit-with error "Manual fix required"

# Type checking with ty and mypy
[group('developer')]
[no-exit-message]
check-types:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    do-command uv run --dev ty check && (
        do-command uv run --dev mypy \
        || exit-with warning "mypy found issues that ty did not"
    ) \
    && okay "Type checks passed" \
    || exit-with error "Type check failed, manual fix required"

# Type checking with ty and mypy (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-types:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    # ty prints annoying output on success, it can be disabled with -q, but
    # that completely disables error reporting.
    quietly () { out=$("$@" 2>&1) || exit-with echo "$out"; }
    quietly uv run --dev ty check --output-format=concise && (
        uv run --dev mypy \
        || exit-with warning "mypy found issues that ty did not"
    ) && okay || exit-with error

# Check code formatting
[group('developer')]
[no-exit-message]
check-format:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    add-status do-command uv run --dev ruff format --check {{ python_dirs }}
    add-status do-command uv run --dev docformatter --check {{ python_dirs }}
    do-status && okay "Format checks passed" \
    || exit-with error "Format check failed, try 'just format' to fix"

# Check code formatting (less output)
[private]
[group('agent')]
[no-exit-message]
agent-check-format:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    add-status uv run --dev ruff format --quiet --check {{ python_dirs }}
    add-status uv run --dev docformatter --check {{ python_dirs }}
    do-status && okay \
    || exit-with error "Format check failed, try 'just format' to fix"

# Reformat code, fail if formatting errors remain
[group('developer')]
[no-exit-message]
format:
    #!/usr/bin/env bash -euo pipefail
    {{ functions }} {{ is_dependency() }} {{ inner }}
    add-status do-command uv run --dev ruff format {{ python_dirs }}
    add-status do-command \
        uv run --dev docformatter --in-place {{ python_dirs }}
    do-status && okay Code format OK || exit-with error Code format failed


