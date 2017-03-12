from apiai import ApiAI
from apiai.requests.query.events import Event
import json
import logging


class Robot:
    def __init__(self, client_access_token, lang, command_names=[]):
        self.apiai = ApiAI(client_access_token)
        self.command_names = command_names
        self.lang = lang
        self.contexts = []
        self.logger = logging.getLogger("ROBOT")

    def _process_text(self, text):
        """
        Tokenize text
        :param text: text
        :type text: str
        :return: commands
        :rtype: list[(str, list[str])]
        """
        parts = text.split("|")
        result = []
        for part in parts:
            items = [item
                     for item in part.split(" ")
                     if item != ""]
            if len(items) == 0:
                continue
            if items[0] not in self.command_names:
                command = "text"
                args = [" ".join(items)]
            else:
                command = items[0]
                args = items[1:]
            result.append((command, args))
        return result

    def _query(self, request):
        response = json.loads(request.getresponse().read())
        self.contexts = response.get("result", {}).get("contexts", [])
        error_type = response.get("status", {}).get("errorType", 0)
        success = True
        if error_type != "success":
            self.logger.error("API.AI returned error : {0}".format(error_type))
            success = False
        session_id = response.get("sessionId", "")
        speech = response.get("result", {}).get("fulfillment", {}).get("speech", "")
        return success, session_id, self._process_text(speech)

    def event(self, event):
        """
        Process event
        :param event: event name
        :type event: str
        :return: success flag, session id, commands
        :rtype: (bool, str, list[str, list[str]])
        """
        return self._query(self.apiai.event_request(Event(event)))

    def welcome(self):
        """
        Process "WELCOME" event
        :return: success flag, session id, commands
        :rtype: (bool, str, list[str, list[str]])
        """
        self.contexts = []
        return self.event("WELCOME")

    def query(self, text):
        """
        Process text request
        :param text: user request
        :type text: str
        :return: success flag, session id, commands
        :rtype: (bool, str, list[(str, list[str])])
        """
        request = self.apiai.text_request()
        request.query = text
        request.lang = self.lang
        return self._query(request)