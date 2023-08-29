from pathlib import Path
from dataclasses import dataclass
import openai


@dataclass
class AudioTranscriber:
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
