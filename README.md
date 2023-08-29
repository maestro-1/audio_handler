# audio_handler
This is a project for performing actions on audio files on a large scale. 

### The Workflow
There are 3 different kind of processes. 
- The first to cut out unwanted parts in the beginning and at the end
- The Second to automate the cutting out of pieces of an audio
- The Third to cut the audio file into multiple parts

You may want to perform 1 or more of these processes on a single file. Doing this is simple
The general workflow for performing the action is to put the name of the file you want to work on in the 
relevant csv documents. 

And it will follow the process listed above in the exact other
- Cut unwanted beginning and end out
- Cut out the unwanted parts in the audio out
- Divide the audio into multiple pieces

If the name of the file is only in one of the relevant csv document, only that action is performed and so on.

After the item is worked on, the csv document is updated with a status such that a user can be aware of whether the process
was completed or if it failed

By putting all the target files in the `unedited` folder, the program knows which file to target from the folder