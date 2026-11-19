# Variables
SRC		= pac-man.py
DEBUG	= pdb
PYTHON	= uv run python
GREEN	= \033[32m
BOLD	= \033[1m
BLUE	= \033[34m
CYAN	= \033[36m
RES		= \033[0m
CONFIG_PATH = data/config.json
ARCHIVE	= pac-man.tar.gz

# Rules
all:
	@printf "\n$(BLUE)===== PAC-MAN =====$(RES)\n\n"
	@printf "Here is the list of allowed commands:\n"
	@printf "  - $(CYAN)make install$(RES): install all the dependencies of the project.\n"
	@printf "  - $(CYAN)make run $(RES): run the program.\n"
	@printf "  - $(CYAN)make debug $(RES): run the program with python pdb debugger.\n"
	@printf "  - $(CYAN)make clean$(RES): clean temp files and cache.\n"
	@printf "  - $(CYAN)make lint$(RES): run flake8 and mypy.\n"
	@printf "  - $(CYAN)make lint-strict$(RES): same as lint but with --strict flag for mypy.\n\n"


install:
	@printf "$(GREEN)--> Installing all dependencies...$(RES)\n"
	@uv sync
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install mazegenerator-00001-py3-none-any.whl
	@printf "$(GREEN)--> All dependencies successfully installed !$(RES)\n"

run:
	@uv run python $(SRC) $(CONFIG_PATH)

build:
	@echo "$(BOLD)Building project archive...$(RES)"
	@touch pac-man.tar.gz
	@tar -czf $(ARCHIVE) \
		--exclude='./.git' \
		--exclude='./.venv' \
		--exclude='./__pycache__' \
		--exclude='./.mypy_cache' \
		--exclude='./dist' \
		--exclude='./.claude' \
		--exclude='./src/*.egg-info' \
		--exclude='./src/**/__pycache__' \
		--exclude='./pac-man.tar.gz' \
		.
	@echo "$(GREEN)Archive built: $(ARCHIVE)$(RES)"

debug:
	@uv run python -m $(DEBUG) $(SRC) $(CONFIG_PATH)

clean:
	@rm -rf ./src/__pycache__
	@rm -rf ./src/**/__pycache__
	@rm -rf .venv
	@rm -rf .mypy_cache
	@rm -rf pac-man.tar.gz
	@printf "$(GREEN)--> Successfully deleted .venv$(RES)\n"
	@printf "$(GREEN)--> Successfully deleted .mypy_cache$(RES)\n"
	@printf "$(GREEN)--> Successfully deleted ./src/__pycache__$(RES)\n"
	@printf "$(GREEN)--> Successfully deleted ./src/**/__pycache__$(RES)\n"
	@printf "$(GREEN)--> Successfully deleted .pac-man.tar.gz$(RES)\n"

lint:
	@printf "Starting flake8 and mypy tests...\n"
	@uv run flake8 .
	@uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@printf "Starting flake8 and mypy strict tests...\n"
	@uv run flake8 .
	@uv run mypy . --strict

.PHONY:
	install run debug clean lint lint-strict
