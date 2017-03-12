import importlib


class ApiAiConfig:
    def __init__(self, client_access_token, language):
        """
        Apiai bot configuration
        :param client_access_token: api.ai client access token
        :type client_access_token: str
        :param language: apiai language (e.g. "ru")
        :type language: str
        """
        self.client_access_token = client_access_token
        self.language = language


class SpeechkitRecognitionConfig:
    def __init__(self, language):
        """
        Speech recognition configuration
        :param language: language code (e.g. "ru-RU")
        :type language: str
        """
        self.language = language


class SpeeckitSynthesisConfig:
    def __init__(self, cache_size, language, speaker, emotion, speed):
        """
        Speechkit TTS
        :param cache_size: LRU chache size for speechs
        :type cache_size: int
        :param language: language code (e.g. "ru-RU")
        :type language: str
        :param speaker: speaker name (jane, oksana, alyss, omazh, zahar, ermil)
        :type speaker: str
        :param emotion: emotion (good/neutral/evil)
        :type emotion: str
        :param speed: speed (0.1 <= x <= 3.0)
        :type speed: float
        """
        self.cache_size = cache_size
        self.language = language
        self.speaker = speaker
        self.emotion = emotion
        self.speed = speed


class SpeechkitConfig:
    def __init__(self, key, recognition, synthesis):
        """
        Speechkit config
        :type key: str
        :type recognition: SpeechkitRecognitionConfig|dict
        :type synthesis: SpeeckitSynthesisConfig|dict
        """
        self.key = key
        if isinstance(recognition, dict):
            self.recognition = SpeechkitRecognitionConfig(**recognition)
        else:
            self.recognition = recognition
        if isinstance(synthesis, dict):
            self.synthesis = SpeeckitSynthesisConfig(**synthesis)
        else:
            self.synthesis = synthesis


class RecordConfig:
    def __init__(self, silence_calculation_chunks, speech_level_coefficient, start_wait_chunks, finish_wait_chunks):
        """
        Record config
        :param silence_calculation_chunks: count of chunks to calculate silent sound level
        :type silence_calculation_chunks: int
        :param speech_level_coefficient: chunk marked as speech if middleAmp(chunk) >= k * middleAmp(silence)
        :type speech_level_coefficient: float
        :param start_wait_chunks: maximal count of chunks to wait speech
        :type start_wait_chunks: int
        :param finish_wait_chunks: minimal count of silent chunks to stop record
        :type finish_wait_chunks: int
        """
        self.silence_calculation_chunks = silence_calculation_chunks
        self.speech_level_coefficient = speech_level_coefficient
        self.start_wait_chunks = start_wait_chunks
        self.finish_wait_chunks = finish_wait_chunks


class Config:
    def __init__(self, command_handlers, apiai, speechkit, record):
        """
        Configuration
        :param command_handlers: dict of command name - handler ] \
            (there handler presented by string "module_name:function_name") \
            Handler consume application instance and list of string params \
                and return break flag and (mp3 sound (as bytes) or None)
        :type command_handlers: dict[str, str]
        :param apiai: apiai config
        :type apiai: ApiAiConfig|dict
        :param speechkit: speechkit config
        :type speechkit: SpeechkitConfig|dict
        :param record: recorder config
        :type record: RecordConfig|dict
        """
        self.command_handlers = {}
        for command, path in command_handlers.items():
            module_name, function_name = path.split(":")
            self.command_handlers[command] = getattr(importlib.import_module(module_name), function_name)
        if isinstance(apiai, dict):
            self.apiai = ApiAiConfig(**apiai)
        else:
            self.apiai = apiai
        if isinstance(speechkit, dict):
            self.speechkit = SpeechkitConfig(**speechkit)
        else:
            self.speechkit = speechkit
        if isinstance(record, dict):
            self.record = RecordConfig(**record)
        else:
            self.record = record