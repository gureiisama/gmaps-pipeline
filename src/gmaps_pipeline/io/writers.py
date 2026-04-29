import json


def write_json(api_object: object, path: str):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(api_object, file)
