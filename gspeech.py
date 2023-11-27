from google.cloud import texttospeech
import os
import subprocess

# TODO: Enable passing of the credentials filename to the function text_to_speech itself.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcreds.json"


def text_to_speech(text, output_file, voice_name='en-US-Wavenet-D', language_code='en-US'):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )

    # Specify the type of audio file
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Write the response audio content to a file
    with open(output_file, 'wb') as out_file:
        out_file.write(response.audio_content)
        print(f'Audio content written to "{output_file}"')

def play_mp3(path_to_mp3, mp3player='mpg123'):
    # TODO: Document how to install mpg123, or allow for use of different way to play mp3's.
    try:
        subprocess.Popen([mp3player, '-q', path_to_mp3]).wait()
    except Exception as e:
        print(f"Most likely {mp3player} needs to be installed.")
        raise e


if __name__ == "__main__":
    #input_text = input("Enter the text you want to convert to speech: ")
    input_text = "Say something deep and profound."
    output_filename = "google.mp3"
    text_to_speech(input_text, output_filename)
    play_mp3(output_filename)





