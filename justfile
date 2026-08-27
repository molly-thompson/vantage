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
tailwind *args:
    tailwindcss -i ./static/css/input.css -o ./static/css/output.css {{args}}


# ENTER PROCESSES

# Run Django development server
runserver:
	uv run python manage.py runserver

# Run Django server with Tailwind hot-reloading
dev:
		just --parallel runserver tailwind --watch

# Enter interactive Django shell
shell:
    uv run python manage.py shell

# Run Ruff lint watcher
lint-watch:
    just lint --watch


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

# Run ty typecheck
typecheck:
    uv run ty check

# Run pytest test suite
test:
    uv run pytest
