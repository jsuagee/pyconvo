import os, json, time, pickle
from textwrap import TextWrapper
from pathlib import Path
import openai

from gspeech import text_to_speech, play_mp3
import preprocess

# TODO: Put this example construction in a config file.
# Construction of an example prompt for the ChatGPT API.
s1 = '''
Juliet is a professor of Literature at a university and knows about many things. 
'''
s2 = '''
John is a university professor, but a real idiot who doesn't know much but likes \
to think he knows everything.
'''
s3 = '''
Write a short conversation between Juliet and John about Romance literature in which \
John really demonstrates how insufferable he is and Juliet tells him how stupid he is \
and everybody gets upset about it.
'''
api_prompt = s1 + s2 + s3

# Set function that we use to preprocess the speakers' lines before
# turning them into audio:
#
#preprocess_line = preprocess.do_no_preprocessing
preprocess_line = preprocess.remove_commas

# Pause between speakers lines:
pause_length = 0.25

voice_juliet, voice_john = "en-GB-Neural2-A", "en-GB-Neural2-B"

# TODO: Put reload_from_cache as an input argument.
reload_from_cache = True

audio_dir = Path("audio_files/")
cache_file = Path("cache/") / "cache.pkl"

def cache(conv, cache_file):
    with open(cache_file, "wb") as f:
        pickle.dump(conv, f)

def load_from_cache(cache_file):
    with open(cache_file, "rb") as f:
        return pickle.load(f)

def send_api_request():
    with open("keys.json", "r") as file:
        config = json.load(file)
    openai.organization = config["org"]
    openai.api_key = config["key"]
    print("Sending request to API server. Waiting for openai response...")
    a = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user", "content": api_prompt
            },
        ]
    )
    print("Response received.")
    conv = a["choices"][0]["message"]["content"]
    return conv

# TODO: Better way to do this without using global variable declarations:
def load_convo():
    global reload_from_cache, cache_file
    if reload_from_cache:
        try:
            print("Attempting to load conversation from cache.")
            conv = load_from_cache(cache_file)
        except:
            print("Failed to load from cache.")
            reload_from_cache = False
    if not reload_from_cache:
        conv = send_api_request()
        cache(conv, cache_file)
    print("Conversation is now loaded.\n")
    return conv

# Code for wrapping text on output so their lines are easier to read:
indent_juliet = "".join([" "] * (len("Juliet: ")))
indent_john = "".join([" "] * (len("Juliet: ")))
tw_prompt = TextWrapper(width=80)
tw_juliet = TextWrapper(width=80, subsequent_indent=indent_juliet)
tw_john = TextWrapper(width=80, subsequent_indent=indent_john)


if __name__ == "__main__":
    conv = load_convo()
    lines = conv.split("\n")

    # Ordered list of alternating speakers' lines:
    text_blocks = []

    i = 0
    for line in lines:
        if "Juliet:" in line[:len("Juliet: ")]:
            text_blocks.append(tw_juliet.fill(line))
            line_ = line[len("Juliet: "):]
            line_ = preprocess_line(line_)
            if not reload_from_cache:
                text_to_speech(line_, audio_dir / "line-{}.mp3".format(i),
                               voice_name=voice_juliet, language_code="en-GB")
            i += 1
        elif "John:" in line[:len("John: ")]:
            text_blocks.append(tw_john.fill(line))
            line_ = line[len("John: "):]
            line_ = preprocess_line(line_)
            if not reload_from_cache:
                text_to_speech(line_, audio_dir / "line-{}.mp3".format(i),
                               voice_name=voice_john, language_code="en-GB")
            i += 1
        else:
            # some lines are blanks, or the initial prompt.
            continue
    nlines = i

    prompt = tw_prompt.fill(lines[0])
    print(prompt + "\n")
    for i in range(nlines):
        print(text_blocks[i] + "\n")
        play_mp3(audio_dir / "line-{}.mp3".format(i))
        time.sleep(pause_length)









