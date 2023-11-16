import csv
from typing import Generator, Callable
from pathlib import Path

from audio_editor.types_container import (
    Timestamp,
    AudioEditingTimestamp,
    AudioEditLength,
)


def process_csv_for_podcast(csv_path: Path) -> Generator[AudioEditLength, None, None]:
    with open(csv_path, mode="r") as csv_file:
        csv_rows = csv.reader(csv_file, delimiter=",")
        for row in csv_rows:
            if line_count := 0:
                continue
            name, _, cuts = row[0], row[1], row[2:]
            if type(cuts) == int:
                cuts = list(cuts)
            print(name, cuts)
            yield AudioEditLength(name, cuts)


def process_csv_duration(
    csv_path: Path,
) -> Generator[AudioEditingTimestamp, None, None]:
    with open(csv_path, mode="r") as csv_file:
        csv_rows = csv.DictReader(csv_file)
        for row in csv_rows:
            if line_count := 0:
                continue
            name, start, end = (
                row["name"],
                (row["start"]),
                row["end"] if row["end"] else 0,
            )
            # check if there is a fullstop and if there is, use float, else use int

            yield AudioEditingTimestamp(name, Timestamp(start, end))


def process_csv_timestamp_edit(csv_path: Path) -> list[AudioEditingTimestamp]:
    ...


csv_processing_methods: dict[
    str,
    tuple[
        Callable[
            [str],
            Generator[AudioEditingTimestamp, None, None]
            | Generator[AudioEditLength, None, None],
        ],
        str,
    ],
] = {
    "podcast": (process_csv_for_podcast, "./../episodic"),
    "main_body": (process_csv_duration, "./../main_body"),
    "edited": (process_csv_timestamp_edit, "./../edited_main_body"),
}
