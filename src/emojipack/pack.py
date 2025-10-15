"""Snippet pack generation for Alfred."""

import json
import plistlib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from emojipack.snippets import AlfredSnippet


@dataclass
class SnippetPack:
    """Alfred snippet pack with prefix/suffix settings."""

    prefix: str
    suffix: str
    snippets: list[AlfredSnippet] = field(default_factory=list)

    def create_info_plist(self) -> str:
        """Create info.plist content with prefix and suffix settings."""
        data = {
            "snippetkeywordprefix": self.prefix,
            "snippetkeywordsuffix": self.suffix,
        }
        return plistlib.dumps(data).decode()

    def write(self, output_path: Path) -> None:
        """Write .alfredsnippets zip file with info.plist and snippets."""
        with zipfile.ZipFile(output_path, "w") as zf:
            zf.writestr("info.plist", self.create_info_plist())
            for snippet in self.snippets:
                filename = f"{snippet.uid}.json"
                content = json.dumps(snippet.to_json(), ensure_ascii=False)
                zf.writestr(filename, content)

    def write_macos_plist(self, output_path: Path) -> None:
        """Write macOS text expansions plist file."""
        expansions = [
            {
                "phrase": snippet.snippet,
                "shortcut": (
                    f"{self.prefix}{snippet.keyword.replace(' ', '-')}"
                    f"{self.suffix}"
                ),
            }
            for snippet in self.snippets
        ]
        with output_path.open("wb") as f:
            plistlib.dump(expansions, f)

    @classmethod
    def read(cls, input_path: Path) -> "SnippetPack":
        """Read .alfredsnippets zip file and return SnippetPack."""
        with zipfile.ZipFile(input_path) as zf:
            plist_data = plistlib.loads(zf.read("info.plist"))
            prefix = plist_data.get("snippetkeywordprefix", "")
            suffix = plist_data.get("snippetkeywordsuffix", "")
            snippets = []
            for name in zf.namelist():
                if name == "info.plist":
                    continue
                snippet_data = json.loads(zf.read(name))
                alfred_snippet = snippet_data["alfredsnippet"]
                snippet = AlfredSnippet(
                    keyword=alfred_snippet["keyword"],
                    name=alfred_snippet["name"],
                    snippet=alfred_snippet["snippet"],
                    uid=alfred_snippet["uid"],
                )
                snippets.append(snippet)
        return cls(prefix=prefix, suffix=suffix, snippets=snippets)
