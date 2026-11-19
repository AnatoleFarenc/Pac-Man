"""CLI argument parsing and JSON loading helpers for config and scores."""

import sys
import json
from pydantic import ValidationError
from .data import Config, HighScores

RED = '\033[31m'
RESET = '\033[0m'


def get_config_path(args: list[str]) -> str:
    """Extract and validate the config file path from command-line *args*.

    Args:
        args: ``sys.argv``-style argument list
        (first element is the script name).

    Returns:
        Path to the JSON configuration file.

    Raises:
        ValueError: If the argument count is wrong or the file is not a JSON.
    """

    match len(args):
        case 1:
            raise ValueError("Missing config file path.")
        case 2:
            pass
        case _:
            raise ValueError("Too many CLI arguments.")
    if not args[1].endswith('.json'):
        raise ValueError(f"Config file '{args[1]}' is not a json file.")

    return args[1]


def load_config(path: str) -> Config:
    """Load a ``Config`` from the JSON file at *path*,
    falling back to defaults.

    Strips comment lines (starting with ``#`` or ``//``), ignores unknown keys,
    and reverts individual invalid values to their defaults.

    Args:
        path: File-system path to the JSON configuration file.

    Returns:
        A populated ``Config`` instance (may use defaults on parse errors).
    """

    config_lines: list[str] = list()

    try:
        # reconstruct the file minus the comment lines
        with open(path) as f:
            for line in f:
                if line.strip().startswith(('#', '//')):
                    continue
                config_lines.append(line)

        # convert the string to a JSON obj
        config_obj = json.loads('\n'.join(config_lines))
        if not isinstance(config_obj, dict):
            print(f"{RED}[CFGERROR] Wrong config file format.{RESET}\n"
                  "Lauching with default config...",
                  file=sys.stderr)
            return Config()
        else:
            file_keys: set[str] = set(config_obj.keys())
            base_keys: set[str] = set(Config.model_fields.keys())

            # discard unknown keys
            unknown_keys: set[str] = file_keys - base_keys
            for key in unknown_keys:
                config_obj.pop(key)

            # look for missing mandatory keys
            missing_keys: set[str] = (base_keys -
                                      file_keys)
            for key in missing_keys:
                print(f"{RED}[CFGERROR] Missing '{key}' "
                      f"key in config file.{RESET}\n"
                      "Reverting to default value...", file=sys.stderr)
            return Config(**config_obj)

    except ValidationError as e:
        for error in e.errors():
            print(f"{RED}[CFGERROR] Invalid value for {error['loc'][0]}:"
                  f" '{config_obj[error['loc'][0]]}'.{RESET}\n"
                  "Reverting to default value...",
                  file=sys.stderr)
            config_obj.pop(error['loc'][0])
        return Config(**config_obj)
    except OSError as e:
        print(f"{RED}[OSError] {e} ({path}).{RESET}\n"
              "Launching with default config...",
              file=sys.stderr)
        return Config()
    except json.JSONDecodeError as e:
        print(f"{RED}[JSONError] {e} ({path}).{RESET}\n"
              "Launching with default config...",
              file=sys.stderr)
        return Config()


def load_scores(path: str) -> HighScores:
    """Load a ``HighScores`` from the JSON file at *path*,
    falling back to defaults.

    Args:
        path: File-system path to the JSON scores file.

    Returns:
        A ``HighScores`` instance (populated with placeholder scores on error).
    """

    default_scores: list[dict[str, int]] = [
    ]
    score_lines: list[str] = list()

    try:
        with open(path) as f:
            for line in f:
                if line.strip().startswith(('#', '//')):
                    continue
                score_lines.append(line)

        score_obj = json.loads('\n'.join(score_lines))
        if not isinstance(score_obj, list):
            print(f"{RED}[ERROR] Wrong score file format.{RESET}\n"
                  "Lauching with default config...",
                  file=sys.stderr)
            return HighScores(default_scores)
        else:
            return HighScores(score_obj)

    except OSError:
        return HighScores(default_scores)
    except json.JSONDecodeError:
        print(f"{RED}[JSONError] Invalid high-scores content.{RESET}\n"
              "Launching with default scores...",
              file=sys.stderr)
        return HighScores(default_scores)
