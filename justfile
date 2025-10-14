_ := require("uv")

# Display available recipes.
help:
    @just --list

# Generate Emoji Pack
generate *ARGS:
    uv run scripts/emojipack-generator {{ ARGS }}

# Generate Emoji Pack and open with Alfred
install: generate
    open "Emoji Pack.alfredsnippets"

# Development workflow: test, format, check
dev: test format check
    @echo "\033[1;92m✅ OK\033[0m"

# Agent workflow: minimal output version of dev
agent:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p build
    if ! just dev 2>&1 | tee build/agent.log | awk 'NF { "date +%s" | getline now; close("date +%s"); if (now - last >= 1 || last == 0) { printf "." > "/dev/stderr"; last = now } }'; then
        echo "" >&2
        echo -e "\033[1;91m❌ ERROR\033[0m" >&2
        cat build/agent.log >&2
        exit 1
    fi
    echo "" >&2
    echo "✅ OK" >&2

# Run test suite
test *ARGS:
    uv run --dev pytest {{ ARGS }}

python_dirs := "src tests"

# Remove caches and build files
clean:
    find {{ python_dirs }} -type d -name '__pycache__' | xargs rm -rf
    rm -rf .*_cache .venv build

# Static code analysis and style checks
check:
    uv run -m compileall -q {{ python_dirs }}
    uv run --dev ruff check {{ python_dirs }}
    uv run --dev ruff format --check {{ python_dirs }}
    uv run --dev docformatter --check {{ python_dirs }}
    uv run --dev ty check  # First, because it's faster than mypy
    uv run --dev mypy --strict {{ python_dirs }}

# Static type checking only
mypy:
    uv run --dev ty check  # First, because it's faster than mypy
    uv run --dev mypy --strict --extra-checks {{ python_dirs }}

# Reformat code
format:
    uv run --dev ruff check --fix-only --unsafe-fixes {{ python_dirs }}
    uv run --dev ruff format {{ python_dirs }}
    -uv run --dev docformatter --in-place {{ python_dirs }}
