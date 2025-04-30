import re


def validate_url(url: str, pattern: str) -> str:
    """
    Validate a URL against a given regex pattern.

    :param url: The URL to validate
    :param pattern: A regex pattern the URL must match
    :return: The original URL if valid
    :raises ValueError: If the URL does not match the pattern
    """
    if not re.fullmatch(pattern, url):
        raise ValueError(f"Invalid URL: {url}. Expected to match pattern: {pattern}")
    return url
