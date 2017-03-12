"""
Command processing module.
Present command processor class.
"""
import logging


class CommandProcessor:
    """
    Command processorr - will apply command handlers to tokenized robot answers
    """
    def __init__(self, handlers):
        """
        Initialize
        :param handlers: list of command handlers. \
            Each handler consume arguments list and return break flag and result (object or None)
        :type handlers: dict[str, (list[str])->(bool, object|NoneType)
        """
        self.handlers = handlers
        self.logger = logging.getLogger("COMMANDS")

    def _run_command(self, command, args):
        if command not in self.handlers:
            self.logger.error("Wrong command : {0}".format(command))
            return False, None
        else:
            return self.handlers[command](args)

    @property
    def commands(self):
        """
        :return: command names
        :rtype: list[str]
        """
        result = list(self.handlers.keys())
        result.sort()
        return result

    def process_commands(self, commands):
        """
        Process list of commands
        :param commands: commands
        :type commands: list[(str, list[str])]
        :return: break flag and results (each result - object of None)
        :rtype: (bool, list[object|NoneType])
        """
        results = []
        for command, args in commands:
            finish, result = self._run_command(command, args)
            results.append(result)
            if finish:
                return True, results
        return False, results
