"""Snippet pack generation for Alfred."""

import plistlib
from dataclasses import dataclass


@dataclass
class SnippetPack:
    """Alfred snippet pack with prefix/suffix settings."""

    prefix: str
    suffix: str

    def create_info_plist(self) -> str:
        """Create info.plist content with prefix and suffix settings."""
        data = {
            "snippetkeywordprefix": self.prefix,
            "snippetkeywordsuffix": self.suffix,
        }
        return plistlib.dumps(data).decode()
