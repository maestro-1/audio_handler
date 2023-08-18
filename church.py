import os
import csv
import math
from pathlib import Path
from typing import Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pydub import AudioSegment
import openai


@contextmanager
def manage_pwd(path: Path):
    if not Path.is_dir(path):
        raise ValueError(f"expected a dir got {path}")
    if not Path.exists(path):
        raise ValueError(f"{path} does not exist")
    orignal_working_directory = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(orignal_working_directory)


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
    length: float


@dataclass
class AudioEditingEnhancement:
    file_path: Path
    # return path is a folder not a file
    return_file_part: Path
    file_extension: str = field(init=False)
    file_size: int = field(init=False)
    file_segment: AudioSegment = field(init=False)
    filename: str = field(init=False)

    def __post_init__(self):
        self.file_path = Path(self.file_path)
        self.return_file_part = Path(self.return_file_part)

        if not Path.exists(self.file_path):
            raise ValueError("file does not exist")
        if not Path.is_dir(self.return_file_part):
            raise ValueError("A valid path was not provided")

        self.file_extension = self.file_path.suffix.strip(".")
        self.file_size = self.file_path.stat().st_size

        self.file_segment = AudioSegment.from_file(
            file=self.file_path.name, format=self.file_extension
        )
        self.filename = self.file_path.stem

    @property
    def _audio_length_in_seconds(self):
        seconds = self.file_segment.duration_seconds
        if seconds:
            return seconds
        raise ValueError("Audio is zero seconds long")

    def clip_file_start_and_end(self, timestamp: Timestamp) -> AudioSegment:
        start_mil_secs = timestamp.start
        end_mil_secs = timestamp.end
        clipped_file = (
            self.file_segment[start_mil_secs:-end_mil_secs]
            if end_mil_secs > 0 or end_mil_secs < 0
            else self.file_segment[start_mil_secs:]
        )
        filename = f"{self.filename}_automation_clipped.{self.file_extension}"
        with manage_pwd(self.return_file_part):
            self._export_file_segment(
                clipped_file, filename, self.file_extension
            )
        return

    # ##############################################################
    # TODO: complete implementation for cutting specified timestamps
    # ##############################################################
    def _clip_by_timestamp(self, timestamps: Iterable[Timestamp]):
        for timestamp in timestamps:
            start_mil_secs = timestamp.start
            end_mil_secs = timestamp.end
            yield self.file_segment[start_mil_secs:end_mil_secs]

    def clip_by_timestamp(self, timestamps: Iterable[Timestamp]):
        file_segments = self._clip_by_timestamp(timestamps)
        combined_file_segment: AudioSegment = sum(file_segments)
        filename = f"{self.filename}_automation_clipped.{self.file_extension}"
        with manage_pwd(self.return_file_part):
            return self._export_file_segment(
                combined_file_segment, filename, self.file_extension
            )

    def divide_audio_by_length(self, length: float) -> None:
        "The last cut will be affected by math.ceil, so do not use that for the cut"
        number_of_cuts: int = math.ceil(self._audio_length_in_seconds / (length * 60))

        for cut in range(1, number_of_cuts + 1):
            start_cut = (cut - 1) * 60 * length * 1000
            end_cut = cut * 60 * 1000 * length
            start_cut_attempt = start_cut if start_cut == 0 else start_cut + 1
            message = self.file_segment[start_cut_attempt:end_cut]
            filename = f"{self.filename}_{cut}.{self.file_extension}"

            with manage_pwd(self.return_file_part):
                self._export_file_segment(message, filename, self.file_extension)
        return

    def divide_by_specified_lengths(self, specified_lengths: Iterable[float]):
        remainder_length = (self._audio_length_in_seconds / 60) - specified_lengths[-1]

        if remainder_length < 10:
            specified_lengths[-1] = self._audio_length_in_seconds / 60

        elif remainder_length > 10:
            start_cut = specified_lengths[-1] * 60 * 1000
            message = self.file_segment[start_cut:]
            filename = f"{self.filename}_final_cut.{self.file_extension}"
            with manage_pwd(self.return_file_part):
                self._export_file_segment(message, filename, self.file_extension)

        for index, cut in enumerate(specified_lengths):
            # for index at the beginning of the file
            if index == 0:
                start_cut = 0
            else:
                start_cut = specified_lengths[index - 1] * 60 * 1000
            end_cut = cut * 60 * 1000
            message = self.file_segment[start_cut:end_cut]
            filename = f"{self.filename}_{cut}.{self.file_extension}"
            with manage_pwd(self.return_file_part):
                self._export_file_segment(message, filename, self.file_extension)
        return

    def _export_file_segment(
        self, file: AudioSegment, filename: str, file_extension: str
    ):
        """
        Exporting from a helper function, because exporting from the function that the edits happen causes
        file not to be exported
        """
        return file.export(
            filename,
            format=file_extension,
        )

    # ######################################
    # TODO: make fixes to the implementation
    # ######################################
    def divide_audio_by_file_size(self, size: float = 25_000_000) -> None:
        # number of times you can get 25mb file from total file
        number_of_cuts = math.ceil(self.file_size / size)

        # length in seconds of each part which is 25mb long
        length_per_cut = self._audio_length_in_seconds / number_of_cuts

        for cut in range(1, round(length_per_cut / 60) + 1):
            start_cut = (cut - 1) * 1000 * length_per_cut
            end_cut = cut * 1000 * length_per_cut

            start_cut_attempt = start_cut if start_cut == 0 else start_cut + 1

            message = self.file_segment[start_cut_attempt:end_cut]
            filename = f"{self.filename}_divide_{cut}.{self.file_extension}"
            with manage_pwd(self.return_file_part):
                self._export_file_segment(message, filename, self.file_extension)
        return


@dataclass
class CSVFileAudioEdit:
    """
    Read/Process csv files to carry out audio editing actions for quick and effective automation.
    This class expects that each csv file it's fed can accomodate details for multiple audios

    The Header of the csv file is expected to contain the type of operation you wish to perform with the values given
    either cut the audio down to podcast size, cut out the unwanted beginning and end of the audio or cut out parts
    of the audio as specied by the timestamps

    Skips any column with status done
    """
    csv_file: Path

    def _run_csv_read_for_podcast(self) -> list[AudioEditLength]:
        """
        Read csv file and derive the length to cut for podcast.
        """

    def _run_csv_read_for_aimed_audio(self) -> list[AudioEditingTimestamp]:
        """
        Read csv file and derive the beginning and end which users want to keep in their audio
        """

    def _run_csv_read_timestamp(self) -> list[AudioEditingTimestamp]:
        """
        Read csv file and derive the different timestamps intend for being cut out of the audio
        """

    def process_csv(self) -> list[AudioEditingTimestamp]:
        """
        Read csv and derive for editting audios, cutting audio's to specied length or removing just the relevant parts
        of the audio.
        Get the relavant path the file specified in the csv document
        """


@dataclass
class AudioTextDetails:
    """
    Experimental definition:


    # Returns multiple files
    - transcript with message_title as the file name
    - csv containing message_title, guessed_timestamp, words_at_timestamp
    """

    def run_open_ai(self, audio_file):
        """
        Get the text transcription from openai and write it into a text file
        """
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

    def run_manual(self, audio_file_transcript: Path):
        """
        Run every word through the filter words list text
        Get the timestamp for each word by dividing the total length of words in the transcript
        by the total length of the audio to find the rough range of where specific words are

        Write the words(sentence), the message and the timestamp for target words in a csv file
        for vetting if it needs to be removed or not
        """


def main():
    audi_enhanced = AudioEditingEnhancement("Business_Service.mp3", "./edited_files")
    audi_enhanced.clip_file_start_and_end(Timestamp(10, 0.3))
    # audi_enhanced.divide_by_specified_lengths([23, 41, 67])
    # audi_enhanced.clip_by_timestamp(
    #     (
    #         Timestamp(12.3, 12.4),
    #         Timestamp(20.1, 21.5),
    #         Timestamp(22.05, 22.10),
    #         Timestamp(30.5, 31.1),
    #     )
    # )


if __name__ == "__main__":
    main()
