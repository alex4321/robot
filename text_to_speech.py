from urllib.request import urlopen
from urllib.parse import quote
from functools import lru_cache


class TextToSpeech:
    def __init__(self, cache_size, key, lang, speaker="alyss", emotion="neutral", speed=1.0):
        """
        Initialize
        :param cache_size: cache size (0 - not use cache)
        :type cache_size: int
        :param key: speechkit key
        :type key: str
        :param lang: language
        :type lang: str
        :param speaker: speaker (see speechkit docs)
        :type speaker: str
        :param emotion: emotion (see speechkit docs)
        :type emotion: str
        :param speed: speed (0.1 <= x <= 3.0)
        :type speed: float
        """
        self.key = key
        self.lang = lang
        self.speaker = speaker
        self.emotion = emotion
        self.speed = speed
        self.cache = []

        @lru_cache(cache_size)
        def get_handler(url):
            return urlopen(url).read()

        self.get = get_handler

    def convert(self, text):
        """
        Convert text to speech
        :param text:
        :return:
        """
        url = "https://tts.voicetech.yandex.net/generate?" + \
              "text={0}&format=mp3&lang={1}&speaker={2}&key={3}&emotion={4}&speed={5}" \
              .format(quote(text), self.lang, self.speaker, self.key, self.emotion, self.speed)
        return self.get(url)