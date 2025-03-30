import json


def load_html_content(filepath: str) -> str:
    """Load HTML content from a file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def load_json(filepath: str) -> dict:
    """Load expected JSON data from a file."""
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)
