import re
from typing import List, Set

MENTION_PATTERN = re.compile(r"@([a-zA-Z0-9_]+)")


def extract_mentioned_usernames(text: str) -> List[str]:
    """Extrait les identifiants @username du texte (ordre conservé, sans doublon)."""
    seen: Set[str] = set()
    out: List[str] = []
    for m in MENTION_PATTERN.finditer(text or ""):
        u = m.group(1)
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
