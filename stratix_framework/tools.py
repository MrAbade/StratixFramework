import re


def to_pascal_case(s: str) -> str:
    s = re.sub(r"[^a-zA-Z]", " ", s)
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    words = s.split()
    return "".join(word.capitalize() for word in words)
