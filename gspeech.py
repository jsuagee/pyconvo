from google.cloud import texttospeech
import os
import subprocess

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


def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()

if __name__ == "__main__":
    input_text = input("Enter the text you want to convert to speech: ")
    output_filename = "google.mp3"
    text_to_speech(input_text, output_filename)
    play_mp3(output_filename)





