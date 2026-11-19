"""Game configuration model and high-score data structures."""

import json
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Validated game configuration loaded from a JSON file via pydantic."""

    width: int = Field(gt=3, lt=22, default=20)
    height: int = Field(gt=3, lt=22, default=15)
    lives: int = Field(gt=0, default=3)
    # pacgums: int = Field(gt=0, lt=70, default=42)
    points_per_pacgum: int = Field(gt=0, default=10)
    points_per_super_pacgum: int = Field(gt=0, default=50)
    points_per_ghost: int = Field(gt=0, default=200)
    seed: int = Field(default=42)
    level_max_time: int = Field(gt=0, default=90)
    max_levels: int = Field(gt=0, default=10)
    highscores_filename: str = Field(default="./data/high_scores.json")


class HighScores:
    """Ordered collection of the top-10 player high scores.

    Scores are kept sorted in descending order.  The list is trimmed to at
    most ten entries whenever a new score is added.
    """

    def __init__(self, scores: list[dict[str, int]]) -> None:
        """Sort and validate an initial list of ``{name: score}`` dicts.

        Args:
            scores: Raw list of single-entry dicts loaded from the JSON file.

        Raises:
            ValueError: If any entry contains more than one key.
        """

        self.scores: list[dict[str, int]] = scores
        for score in self.scores:
            if len(score) != 1:
                raise ValueError(
                    f"High score contain too many entries: {score}"
                )

        self.scores.sort(key=lambda x: list(x.values())[0], reverse=True)

    def is_high(self, score: int) -> bool:
        """Return ``True`` if *score* would rank in the top-10 list.

        Args:
            score: The candidate score to test.
        """

        if len(self.scores) < 10:
            return True
        return score >= min(list(s.values())[0] for s in self.scores)

    def get_rank(self, score: int) -> int:
        """Return the zero-based rank that *score* would occupy in the list.

        Args:
            score: The candidate score to rank.

        Returns:
            Number of existing scores strictly higher than *score*.
        """

        return sum(1 for s in self.scores if list(s.values())[0] >= score)

    def add_score(self, score: int, name: str) -> None:
        """Add a new entry and trim the list to ten.

        Args:
            score: The player's final score.
            name: The player's name (up to 10 characters).
        """

        self.scores.append({name: score})
        self.scores.sort(key=lambda x: list(x.values())[0], reverse=True)
        while len(self.scores) > 10:
            self.scores.pop()

    def to_json(self, path: str) -> None:
        """Persist the sorted score list to a JSON file at *path*.

        Args:
            path: Destination file path.

        Raises:
            OSError: If the file cannot be opened or written.
            json.JSONDecodeError: On serialisation failure.
        """
        self.scores.sort(key=lambda x: list(x.values())[0], reverse=True)
        try:
            with open(path, 'w') as f:
                json.dump(self.scores, f, indent=4)
        except OSError as e:
            raise OSError(f"[OSError] {e} ({path})")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"[JSONError] {e} ({path})", "", 0)
