from config import Config
from application import Application
import sys
import json


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("Need path to configuration file as argument\n")
        exit(1)
    with open(sys.argv[1], "r") as config_file:
        config = Config(**json.load(config_file))
    app = Application(config)
    app.main()
