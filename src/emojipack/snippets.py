"""Snippet generation for Alfred."""

from dataclasses import dataclass

from emojipack.download import GemojiEntry


def generate_uid(keyword: str, emoji: str) -> str:
    """Generate stable UID from keyword and emoji hex codes."""
    hex_codes = "-".join(f"{ord(c):X}" for c in emoji)
    return f"{keyword}-{hex_codes}"


@dataclass
class AlfredSnippet:
    """Alfred snippet with keyword, emoji, and metadata."""

    keyword: str
    name: str
    snippet: str
    uid: str

    @classmethod
    def from_gemoji(cls, entry: GemojiEntry, alias: str) -> "AlfredSnippet":
        """Create AlfredSnippet from GemojiEntry and alias keyword."""
        if alias not in entry["aliases"]:
            msg = f"Alias '{alias}' not in {entry['aliases']}"
            raise ValueError(msg)
        return cls(
            keyword=alias.replace("_", " "),
            name=entry["description"],
            snippet=entry["emoji"],
            uid=generate_uid(alias, entry["emoji"]),
        )

    def to_json(self) -> dict[str, dict[str, str | bool]]:
        """Convert to Alfred snippet JSON format."""
        return {
            "alfredsnippet": {
                "keyword": self.keyword,
                "name": self.name,
                "snippet": self.snippet,
                "uid": self.uid,
                "dontautoexpand": False,
            }
        }
