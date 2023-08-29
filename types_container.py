from pathlib import Path
from dataclasses import dataclass


@dataclass
class Timestamp:
    start: int
    end: int

    """
    The timestamp is in milliseconds.
    This is in accordance with the interface of pydub
    """

    def __post_init__(self):
        self.start = self.start * 60 * 1000
        self.end = self.end * 60 * 1000


@dataclass
class AudioEditingTimestamp:
    filename: Path
    timestamp: Timestamp


@dataclass
class AudioEditLength:
    filename: Path
    lengths: list[float | int]
