from command_processor import CommandProcessor
from robot import Robot
from speech_to_text import SpeechToText
from text_to_speech import TextToSpeech
from recorder import SpeechCapture
from config import Config
from stdhandlers import handlers as stdhandlers
from player import play_list
import json


class Application:
    """
    Application main class
    """
    def __init__(self,
                 config
                 ):
        """
        Initialize
        :param config: configuration
        :type config: Config
        """
        self.command_processor = CommandProcessor(self._command_handlers(config.command_handlers))
        self.robot = Robot(config.apiai.client_access_token, config.apiai.language, self.command_processor.commands)
        self.speech_to_text = SpeechToText(config.speechkit.key, "", config.speechkit.recognition.language)
        self.text_to_speech = TextToSpeech(config.speechkit.synthesis.cache_size,
                                           config.speechkit.key,
                                           config.speechkit.synthesis.language,
                                           config.speechkit.synthesis.speaker,
                                           config.speechkit.synthesis.emotion,
                                           config.speechkit.synthesis.speed)
        self.record = SpeechCapture(config.record.silence_calculation_chunks,
                                    config.record.speech_level_coefficient,
                                    config.record.start_wait_chunks,
                                    config.record.finish_wait_chunks)

    def _handler(self, real_handler):
        return lambda args: real_handler(self, args)

    def _command_handlers(self, command_handlers):
        result = {}
        for command, handler in stdhandlers.items():
            result[command] = self._handler(handler)
        for command, handler in command_handlers.items():
            result[command] = self._handler(handler)
        return result

    def _process_answer(self, commands):
        finish, results = self.command_processor.process_commands(commands)
        if not finish:
            noempty_results = [result
                               for result in results
                               if result is not None]
            play_list(noempty_results)

    def welcome(self):
        """
        Run robot welcome event
        """
        success, session_id, answer_commands = self.robot.welcome()
        if success:
            self.speech_to_text.uuid = session_id
            self._process_answer(answer_commands)

    def query(self):
        """
        Run speech request (if we'lll have it)
        """
        print("Listening")
        silent, record = self.record.record_mp3()
        if silent:
            print("Silent")
            return
        success, text = self.speech_to_text.convert(record)
        if not success:
            print("Not recognized")
            return
        print("User : " + text)
        success, _, commands = self.robot.query(text)
        print("Robot commands : " + json.dumps(commands))
        if not success:
            return
        self._process_answer(commands)

    def main(self):
        self.welcome()
        while True:
            self.query()