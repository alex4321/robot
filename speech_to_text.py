#!/usr/bin/env python
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from xml.etree import ElementTree


class SpeechToText:
    def __init__(self, key, uuid, lang):
        """
        Initialize
        :param key: speechkit key
        :type key: str
        :param uuid: uuid
        :type uuid: str
        :param lang: language
        :type lang: str
        """
        self.key = key
        self.uuid = uuid
        self.lang = lang

    def _prepare_input(self, content):
        output = b''
        chunked_size = 2000
        while len(content) > 0:
            size = min(len(content), chunked_size)
            output += hex(size)[2:].encode("utf-8")
            output += b'\r\n'
            output += content[:size]
            output += b'\r\n'
            content = content[size:]
        output += b'0\r\n\r\n'
        return output

    def convert(self, speech_mp3):
        """
        Convert speech (in MP3) to text
        :param speech_mp3: speech record bytes
        :type speech_mp3: bytes
        :return: success flag, text
        :rtype: (bool, str)
        """
        chunked = self._prepare_input(speech_mp3)
        url = "https://asr.yandex.net/asr_xml?uuid={0}&key={1}&topic=queries&lang={2}".format(
            self.uuid, self.key, self.lang
        )
        request = Request(url, urlencode({}))
        request.add_header("Content-Type", "audio/x-mpeg-3")
        request.add_header("Transfer-Encoding", "chunked")
        request.data = chunked
        response = urlopen(request).read().decode('utf-8')
        tree = ElementTree.fromstring(response)
        success = tree.attrib['success'] == "1"
        if not success:
            return False, ""
        variants = tree.findall("variant")
        if len(variants) == 0:
            return False, ""
        max_confidence = None
        max_confident_text = None
        for variant in variants:
            confidence = float(variant.attrib["confidence"])
            print(confidence, variant.text)
            if max_confidence is None or confidence > max_confidence:
                max_confidence = confidence
                max_confident_text = variant.text
        return True, max_confident_text