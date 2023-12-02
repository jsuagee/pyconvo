import os, json, time, argparse
from textwrap import TextWrapper
from pathlib import Path
import openai

from gspeech import text_to_speech, play_mp3
import preprocess


# TODO: Do I really need a custom Exception class here.
class InvalidConfigFileException(Exception):
    pass


def get_input_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reload-from-cache", action='store_true',
                        help="Setting this argument flag will reuse the conversation previously returned from OpenAI's API.")
    parser.add_argument("--cache-file", default="cache/cache.txt",
                        help="The path to the cache file where the conversation obtained from the OpenAI API call is stored.")
    parser.add_argument("--reuse-cached-audio", action='store_true',
                        help="Setting this flag causes the program to reuse the cached audio files instead of querying google's API.")
    parser.add_argument("-k", "--keys-file", default="keys.json",
                        help="The path to the file containing your OpenAI credentials.")
    parser.add_argument("-c", "--config", dest="config",
                        help="The path to the conversation config file.")
    parser.add_argument("--mp3-player", default="mpg123",
                        help='The program to use to play the output audio mp3 files. Default is "mpg123"')

    # TODO: Include no-verbose option to disable incremental update print statements.
    # TODO: Include no-cache option to indicate not to overwrite the conversation cache file.
    args = parser.parse_args()
    return args


class Conversation:
    def __init__(self, args):
        self.reload_from_cache = args.reload_from_cache
        self.reuse_cached_audio = args.reuse_cached_audio
        self.cache_file = args.cache_file
        self.convo_config = args.config
        self.api_keys_file = args.keys_file
        self.mp3_player = args.mp3_player

    def cache(self, conv):
        '''
        Cache the conversation that is returned from the API call to OpenAI. This is useful mostly for
        testing purposes, so that we don't waste time making repeated identical API calls to OpenAI.

        :param conv: The conversation <string>
        :return: None
        '''
        cache_dir = Path(self.cache_file).parent
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
        if not Path(self.cache_file).exists():
            Path(self.cache_file).touch()
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write(conv)

    def load_from_cache(self):
        '''
        Reload the conversation from the cache file. (The cache file is just a text file.)

        :return: The conversation <string>
        '''
        with open(self.cache_file, "r") as f:
            conv = f.read()
        return conv

    def load_config(self, conversation_config=None):
        '''
        Read in the conversation config file.

        :param conversation_config: config filename <string>
        :return: None
        '''

        if conversation_config == None:
            conversation_config = self.convo_config
        with open(conversation_config, "r") as file:
            config = json.load(file)
        self.prompt = config["prompt"]
        characters = config["characters"]
        character_dict = lambda c: (c["name"], {"voice": c["voice"], "language": c["language"]})
        self.characters = dict([character_dict(c) for c in characters])

        preprocess_line_methods = config["preprocess_line_methods"]
        if isinstance(preprocess_line_methods, str):
            self.preprocess_line_methods = [preprocess_line_methods]
        elif isinstance(preprocess_line_methods, list):
            self.preprocess_line_methods = []
            for method in preprocess_line_methods:
                self.preprocess_line_methods.append(getattr(preprocess, method))
        else:
            error_msg = (f'In the conversation config file {conversation_config}, the "preprocess_line_methods" field '
                         f'must be either the name of one of the  methods in the preprocess module, or a list of '
                         f'methods in the preprocess module.')
            raise InvalidConfigFileException(error_msg)

        self.audio_pause_length = config["audio_pause_length"]
        self.audio_dir = Path(config["audio_dir"])
        if not self.audio_dir.exists():
            self.audio_dir.mkdir()

    def preprocess_line(self, line):
        for method in self.preprocess_line_methods:
            line = method(line)
        return line

    def send_api_request(self):
        '''
        Package the prompt into an OpenAI API request, read the response and extract the
        returned conversation.

        :return: The conversation <string>
        '''
        with open(self.api_keys_file, "r") as file:
            config = json.load(file)
        # Some credentials might require "org":
        if "org" in config.keys():
            openai.organization = config["org"]
        openai.api_key = config["key"]
        print("Sending request to API server. Waiting for openai response...")
        # TODO: Enable parameters like temperature.
        #  Define the prompt format in a config file instead, so it's easier to switch to another LLM.
        a = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user", "content": self.prompt
                },
            ]
        )
        print("Response received.")
        conv = a["choices"][0]["message"]["content"]
        return conv

    def load_convo(self):
        '''
        Either reload the previous conversation from the cache file, or make an API request for a new conversation
        to OpenAI's model. Saves the conversation in the  member variable self.convo.

        :return: The conversation <string>
        '''
        if self.reload_from_cache:
            try:
                print("Attempting to load conversation from cache.")
                conv = self.load_from_cache()
            except Exception as e:
                # TODO: Check that this raises appropriately.
                print('Failed to load the conversation from the cache file. The default name of the cache file '
                      'is "cache.txt".\n\n')
                raise e
        if not self.reload_from_cache:
            conv = self.send_api_request()
            # TODO: Implement no-cache argument flag feature.
            self.cache(conv)
        print("Conversation is now loaded.\n")
        self.convo = conv
        return self.convo

    def get_speaker_of_line(self, line):
        '''
        Extract the speaker's name from the beginning prefix of the line that comes before the first ":" character.

        :param line: A line from the conversation <string>
        :return: Speakers name <string>
        '''
        name = line.split(":")[0]
        assert name in self.characters.keys(), f'Error: "{name}" is not the name of a character in the conversation.'
        return name

    def is_nonspeaking_line(self, line):
        '''
        Some lines are blanks, and we need to ignore them.

        :param line: A line from the conversation <string>
        :return: True,  if the line is an actual line of the dialogue
                 False, if the line is a blank line or something else.
        '''
        if ":" not in line:
            return True
        else:
            prefix = line.split(":")
            # Check that one of the character names is in the line prefix.
            for name in self.characters.keys():
                if name in prefix:
                    return False
            # It's conceivable that OpenAI returns a line that doesn't follow the usual format.
            # We treat these lines as non-speaking lines.
            return True

    def build_output(self):
        '''
        Construct an ordered list of spoken lines, along with a corresponding mp3 audio file for each line.
        Save this list to the member variable self.output, and also return the list as its return value.

        :return: a list of dictionaries, one for each spoken line, and each of the form
                {"text": <string>, "audio": name of corresponding mp3 file }
        '''
        output = []
        text_wrappers = construct_text_wrappers(self.characters)
        i = 0
        lines = self.convo.split("\n")
        for line in lines:
            if self.is_nonspeaking_line(line):
                continue
            name = self.get_speaker_of_line(line)
            character = self.characters[name]
            voice, language = character["voice"], character["language"]
            text_block = text_wrappers[name].fill(line)
            audio_file = self.audio_dir / "line_{}.mp3".format(str(i).zfill(2))
            i += 1
            if not self.reuse_cached_audio:
                line_ = line[len(name + ": "):]

                line_ = self.preprocess_line(line_)
                text_to_speech(line_, audio_file,
                               voice_name=voice, language_code=language)
            output.append({"text": text_block, "audio": str(audio_file)})
        self.output = output
        return output

    def play_output(self):
        # Iterate through all spoken lines. Print each one while playing the corresponding mp3 file.
        tw_prompt = TextWrapper(width=80)
        prompt = tw_prompt.fill(self.prompt)
        print(prompt + "\n")
        for line in self.output:
            text, audio = line["text"], line["audio"]
            print(text + "\n")
            play_mp3(audio, self.mp3_player)
            time.sleep(self.audio_pause_length)

    def build_single_file_output(self):
        '''
        For building the audio output into a single mp3 file
        :return: None
        '''
        # TODO: Fill in.
        pass

    def play_single_file_output(self):
        '''
        For playing an mp3 file that was created by build_single_file_output() above.
        :return: None
        '''
        # TODO: Fill in.
        pass

def construct_text_wrappers(characters):
    '''
    Construct TextWrapper objects that we can use to make the print-out of the dialogue easier to read.

    :param characters: A dictionary whose keys are the names of the characters in the dialogue.
    :return: A dictionary of the TextWrapper objects indexed by the names of the characters.
    '''
    text_wrapper = {}
    for name in characters.keys():
        indent_length = len(name) + 2
        indent = "".join([" "]*indent_length)
        text_wrapper[name] = TextWrapper(width=80, subsequent_indent=indent)
    return text_wrapper


if __name__ == "__main__":
    args = get_input_args()
    convo = Conversation(args)
    convo.load_config()
    convo.load_convo()
    convo.build_output()
    convo.play_output()



