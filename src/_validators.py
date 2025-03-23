import re
from functools import wraps


def url_validator(pattern: str):
    """
    Decorator that validates the URL against a given regex pattern.

    :param pattern: A regex pattern the URL must match.
    :raises ValueError: If the URL does not match the pattern.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, url, *args, **kwargs):
            if not re.fullmatch(pattern, url):
                raise ValueError(
                    f"Invalid URL: {url}. Expected to match pattern: {pattern}"
                )
            return func(self, url, *args, **kwargs)

        return wrapper

    return decorator
