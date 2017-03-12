import pyaudio
import wave
import numpy
import logging
from io import BytesIO
from pydub import AudioSegment


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SIZE = 1024


class SpeechCapture:
    def __init__(self,
                 silence_calculation_chunks=40,
                 speech_level_coefficient=2.0,
                 start_wait_chunks=200,
                 finish_wait_chunks=100):
        """
        Recorder
        :param silence_calculation_chunks: count of chunk to calculate silence middle level
        :type silence_calculation_chunks: int
        :param speech_level_coefficient: coefficient to check \
            isSpeech(chunk) = middleAmpl(chunk) >= middleSilenceAmpl * speech_level_cooficient
        :type speech_level_coefficient: float
        :param start_wait_chunks: max count of chunks to wait speech
        :type start_wait_chunks: int
        :param finish_wait_chunks: min count of silent chunsk to stop speech record
        :type finish_wait_chunks: int
        """
        self.silence_calculation_chunks = silence_calculation_chunks
        self.speech_level_coefficient = speech_level_coefficient
        self.start_wait_chunks = start_wait_chunks
        self.finish_wait_chunks = finish_wait_chunks
        self.logger = logging.getLogger("RECORDER")

    def _read_chunks(self, stream, count):
        return numpy.fromstring(stream.read(CHUNK_SIZE * count),
                                numpy.int16)

    def _chunk_middle_level(self, chunk):
        return numpy.mean(numpy.abs(chunk))

    def _record_raw(self):
        """
        :return: silent flag, raw bytes
        :rtype: (bool, bytes)
        :return:
        """
        logging.debug("Starting record")
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK_SIZE)

        logging.debug("Silence level calculation")
        silent_chunks = self._read_chunks(stream, self.silence_calculation_chunks)
        chunks = [silent_chunks]
        silence_level = self._chunk_middle_level(silent_chunks)

        logging.debug("Waiting for speech")
        continue_record = False
        for _ in range(0, self.start_wait_chunks):
            chunk = self._read_chunks(stream, 1)
            chunks.append(chunk)
            if self._chunk_middle_level(chunk) >= self.speech_level_coefficient * silence_level:
                continue_record = True
                break
        if continue_record:
            logging.debug("Recording speech")
            silent_chunks_counter = 0
            while silent_chunks_counter <= self.finish_wait_chunks:
                chunk = self._read_chunks(stream, 1)
                chunks.append(chunk)
                if self._chunk_middle_level(chunk) < self.speech_level_coefficient * silence_level:
                    silent_chunks_counter += 1
                else:
                    silent_chunks_counter = 0
        data = numpy.concatenate(chunks)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        return not continue_record, data.tobytes()

    def _record_wav(self):
        """
        Record WAVE bytes
        :return: silent flag, wave bytes
        :rtype: (bool, bytes)
        """
        is_silent, raw = self._record_raw()
        buffer = BytesIO()
        waveFile = wave.open(buffer, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(raw)
        waveFile.close()
        buffer.seek(0)
        return is_silent, buffer.read()

    def record_mp3(self):
        """
        Record MP3 bytes
        :return: silent flag, wave bytes
        :rtype: (bool, bytes)
        """
        is_silent, wave = self._record_wav()
        wave_io = BytesIO()
        wave_io.write(wave)
        wave_io.seek(0)
        segment = AudioSegment.from_wav(wave_io)
        mp3_io = BytesIO()
        segment.export(mp3_io, format="mp3")
        mp3_io.seek(0)
        return is_silent, mp3_io.read()