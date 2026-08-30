# Set TAILWIND_BIN according to .env config; else set to default 
set dotenv-required
set dotenv-load
TAILWIND_BIN := env("TAILWIND_BIN", justfile_directory() / "build_files" / "tailwindcss")


# List available commands
default: 
	just --list


# Get started
setup:
	uv sync
	just migrate

# Update database with changes
migrate:
	uv run python manage.py migrate

# Record schema changes as migration files
makemigrations app="":
	uv run python manage.py makemigrations {{app}}

# Build Tailwind CSS files
tailwind:
    {{TAILWIND_BIN}} -i ./assets/static/css/input.css -o ./assets/static/css/output.css


# ENTER PROCESSES

# Run Django development server
runserver:
	uv run python manage.py runserver

# Run Django server with Tailwind hot-reloading
[parallel]
dev: runserver tailwind-watch

# Enter interactive Django shell
shell:
    uv run python manage.py shell

# Run Ruff lint watcher
lint-watch:
    just lint --watch

# Run Tailwind watcher
tailwind-watch:
    {{TAILWIND_BIN}} -i ./assets/static/css/input.css -o ./assets/static/css/output.css --watch


# TIDYING & CHECKING: COMPOUND COMMANDS

# Run checks without making changes: lint, format, typecheck, test 
check:
    just lint
    just format --check --diff
    just typecheck
    just test

# Fix linting & formatting
fix:
    just lint --fix
    just format


# TIDYING & CHECKING: SINGLE COMMANDS

# Run Ruff linter
lint *args:
    uv run ruff check {{args}}

# Run Ruff formatter
format *args:
    uv run ruff format {{args}}

# Run mypy typecheck
typecheck:
    uv run mypy .

# Run pytest test suite
test:
    uv run pytest
