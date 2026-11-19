"""Entry point for the Pac-Man game."""

import sys
from .config.loader import get_config_path, load_config, load_scores
from .config.data import Config, HighScores
from .game.game import Game
from .config.config import PATH_SCORE, CONFIG_FILE

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'


def main() -> None:
    """Parse CLI arguments, load configuration, and start the game."""

    # ARGV
    if getattr(sys, 'frozen', False):
        cfg_path: str = CONFIG_FILE
    else:
        try:
            cfg_path = get_config_path(sys.argv)
        except Exception as e:
            print(f"{RED}[ERROR] {e}.{RESET}", file=sys.stderr)
            sys.exit(1)

    # GAME
    try:
        config: Config = load_config(cfg_path)
        if getattr(sys, 'frozen', False):
            score_path: str = PATH_SCORE
        else:
            score_path = config.highscores_filename
        hi_scores: HighScores = load_scores(score_path)

        pacman: Game = Game(config, hi_scores)
        pacman.play()
        hi_scores.to_json(score_path)

    except Exception as e:
        print(e)
        print(f"{RED}[ERROR] An error has occured while playing."
              f"\nPlease restart the game.{RESET}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
