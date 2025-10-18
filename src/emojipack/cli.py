"""Command line interface for emojipack."""
# ruff: noqa: FBT001, FBT002
# Boolean arguments are required for typer CLI flags

import importlib.resources
import unicodedata
from pathlib import Path

import typer
import yaml

from emojipack.comparison import compare_packs
from emojipack.download import fetch_gemoji_data
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

app = typer.Typer()


@app.command()
def generate(macos: bool = False) -> None:
    """Generate Emoji Snippet Pack for Alfred."""
    emoji_data = fetch_gemoji_data()
    snippets = [
        AlfredSnippet.from_gemoji(entry, alias)
        for entry in emoji_data
        for alias in entry["aliases"]
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    if macos:
        output_path = Path("Snippet Pack.plist")
        pack.write_macos_plist(output_path)
    else:
        with importlib.resources.path("emojipack", "icon.png") as icon_path:
            pack.set_icon(icon_path)
        output_path = Path("Emoji Pack.alfredsnippets")
        pack.write(output_path)
    typer.echo(f"Generated {output_path} with {len(snippets)} snippets")


def _format_emoji_dict(
    emoji_dict: dict[str, list[AlfredSnippet]],
) -> dict[str, list[str]]:
    """Convert emoji->snippets dict to name->keywords dict."""
    return {
        snippets[0].name: [s.keyword for s in snippets]
        for snippets in emoji_dict.values()
    }


def _normalize_pack_to_nfd(pack: SnippetPack) -> SnippetPack:
    """Normalize all emoji in pack to NFD and strip variation selectors."""
    normalized_snippets = [
        AlfredSnippet(
            keyword=s.keyword,
            name=s.name,
            snippet=_normalize_emoji(s.snippet),
            uid=s.uid,
        )
        for s in pack.snippets
    ]
    return SnippetPack(
        prefix=pack.prefix, suffix=pack.suffix, snippets=normalized_snippets
    )


def _normalize_emoji(emoji: str) -> str:
    """Normalize emoji to NFD and strip variation selectors."""
    nfd = unicodedata.normalize("NFD", emoji)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


@app.command()
def compare(theirs: Path, mine: Path, unify: bool = False) -> None:
    """Compare two emoji snippet packs."""
    theirs_pack = SnippetPack.read(theirs)
    mine_pack = SnippetPack.read(mine)
    if unify:
        theirs_pack = _normalize_pack_to_nfd(theirs_pack)
        mine_pack = _normalize_pack_to_nfd(mine_pack)
    result = compare_packs(theirs_pack, mine_pack)
    output = {
        "removed": _format_emoji_dict(result.removed),
        "added": _format_emoji_dict(result.added),
    }
    typer.echo(yaml.dump(output, allow_unicode=True, sort_keys=False))
