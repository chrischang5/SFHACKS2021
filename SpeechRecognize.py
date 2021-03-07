
def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    import io

    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))

import sox
tfm = sox.Transformer()
tfm.set_output_format(file_type='flac', rate=16000, channels=1, bits=16, encoding='signed-integer')
tfm.build(r'C:\Users\caleb\PycharmProjects\SFHACKS2021\temp_audio.wav',r'C:\Users\caleb\PycharmProjects\SFHACKS2021\temp_audio1.flac')
transcribe_file(r'C:\Users\caleb\PycharmProjects\SFHACKS2021\temp_audio1.flac')
