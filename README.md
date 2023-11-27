## Project Description
This is a repository for generating conversations using ChatGPT and then 
turning these conversations into audio using Google Cloud's text-to-speech API. 
This is experimental code, and is being provided here in the off chance that it proves 
useful later on to someone else. Feel free to do whatever you want with it.

### Google Cloud
The text-to-speech API must be enabled in your Google Cloud account. See 
<https://cloud.google.com/text-to-speech?hl=en>.  


### Credential files for OpenAI and Google Cloud
Name your google cloud credentials file `gcreds.json` and place it in the 
root directory `pyconvo/`.

Place your OpenAI keys file in the root directory. The default name is `keys.json`. 
If it is named something else you must pass the argument `-k <filename>` as an 
argument to the python program below.

### Install mpg123 (or other mp3 player program)
mpg123 (<https://www.mpg123.de/) is an open source program for playing mp3 audio files. 
- On a mac this can be done using Homebrew (<https://brew.sh/>) by running 
`brew install mpg123` in a terminal window.
- On a Linux distro this can be done using your package manager.
- mpg123 runs on Windows too.

If using a different mp3 player this information must be passed in as an 
argument to the main program using the command line argument 
`--mp3-player <mp3_player>`.

### Install python and project code
* Recommended python: 3.7 to 3.11. Tested with python 3.11.
* Install python: [Download Link](https://www.python.org/downloads/)
* Go to the project root directory: pyconvo/
* Create python virtual environment: `python -m venv venv`
* Activate virtual environment: 
  * `venv\Scripts\activate`(Windows) 
  * `source venv/bin/activate`(Linux)
  * `. venv/bin/activate`(Mac)
* Install dependencies: `pip install -r requirements.txt`

### Structure of a config file
See the included example `professors.json`. Most of the file should be self-explanatory. 
The attribute `preprocess_line_methods` can be used to specify a list of preprocessing 
operations to perform on each line of the conversation.

### Run the main program
* Run python code: `python conversation.py -c conversation_configs/professors.json`

### To see a list of command line options
Run `python conversation.py -h`.

