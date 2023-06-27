import json
import pathlib

FILE_NAME = ".42c"


def get_config_file() -> dict:
    home = pathlib.Path.home()
    config_file = home / FILE_NAME

    # create file if not exists
    if not config_file.exists():
        with open(config_file, "w") as f:
            f.write("{}")

    with open(config_file, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            raise Exception("Config file is not valid JSON")

    return config


def add_config_file_entry(key: str, value: str) -> None:
    config_file = get_config_file()

    config_file[key] = value

    home = pathlib.Path.home()
    config_file_path = home / FILE_NAME

    with open(config_file_path, "w") as f:
        json.dump(config_file, f)


def get_token() -> str or None:
    config_file = get_config_file()

    try:
        return config_file["token"]
    except KeyError:
        return None


def get_url() -> str or None:
    config_file = get_config_file()

    try:
        return config_file["url"]
    except KeyError:
        return None


def set_token(token: str) -> None:
    add_config_file_entry("token", token)


def set_url(url: str) -> None:
    add_config_file_entry("url", url)
