import argparse
from csv_processor.csv_processor import csv_processing_methods
from audio_editor.audio_editor import CSVFileAudioEdit, AudioEditingEnhancement


"""
Need a function to run argparse so that arguments can be passed from the 
terminal. This will allow for chaining without having to touch the source code

-p is --podcast
-se is --remove-from-beginning-and-end
-i is --intro

editor unedited-audio-path -se csv-file-path  -p csv-file-path-for-podcast -i csv-file-path-for-intro 
"""


def build_request():
    parser = argparse.ArgumentParser()
    parser.add_argument("unedited_audio_path")

    parser.add_argument("-p", "--podcast")
    parser.add_argument("-se", "--remove-from-beginning-and-end")
    parser.add_argument("-i", "--intro")

    args = parser.parse_args()

    if remove_from_beginning_and_end := args.remove_from_beginning_and_end:
        run("main_body", remove_from_beginning_and_end)
    if podcast := args.podcast:
        run("podcast", podcast)
    # if edit := args.edit:
    #     run("edit", edit)
    if intro := args.intro:
        pass


# TODO: change csv_type to an enum instead of string
def run(csv_type: str, csv_path: str):
    csv_func, return_directory = csv_processing_methods.get(csv_type)
    generated_information = csv_func(csv_path)

    for info in generated_information:
        audi_enhanced = AudioEditingEnhancement(info.filename, return_directory)
        match csv_type:
            case "main_body":
                audi_enhanced.clip_file_start_and_end(info.timestamp)
            case "podcast":
                audi_enhanced.divide_by_specified_lengths(info.lengths)
    return


def main():
    build_request()


if __name__ == "__main__":
    main()
