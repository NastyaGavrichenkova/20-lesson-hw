import json
from pathlib import Path

from tests import API


def load_schema(dir_name, file_name):
    path = str(Path(API.__file__).parent.joinpath('json_schemas', f'{dir_name}', f'{file_name}').absolute())
    with open(path) as file:
        json_schema = json.loads(file.read())
    return json_schema
