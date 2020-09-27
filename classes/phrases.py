import json
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)

class Phrases(object):
    def __init__(self):
        self.__dict__ = json.load(open(cwd+"/utils/phrases.json"))
