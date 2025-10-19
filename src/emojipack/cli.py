"""Command line interface for emojipack."""
# ruff: noqa: FBT001, FBT002
# Boolean arguments are required for typer CLI flags

import importlib.resources
from pathlib import Path

import typer
import yaml

from emojipack.comparison import EmojiMatch, compare_packs
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
) -> list[str]:
    """Convert emoji->snippets dict to list of snippet names."""
    return [snippets[0].name for snippets in emoji_dict.values()]


def _format_emoji_match_dict(
    emoji_dict: dict[str, EmojiMatch],
) -> list[str]:
    """Convert emoji->EmojiMatch dict to list of mine snippet names."""
    return [match.mine[0].name for match in emoji_dict.values()]


@app.command()
def compare(theirs: Path, mine: Path) -> None:
    """Compare two emoji snippet packs."""
    theirs_pack = SnippetPack.read(theirs)
    mine_pack = SnippetPack.read(mine)
    result = compare_packs(theirs_pack, mine_pack)
    output = {
        "removed": _format_emoji_dict(result.removed),
        "removed_space": _format_emoji_match_dict(result.removed_space),
        "added_emoji_presentation": _format_emoji_match_dict(
            result.added_emoji_presentation
        ),
        "found": _format_emoji_match_dict(result.found),
        "added": _format_emoji_dict(result.added),
    }
    typer.echo(yaml.dump(output, allow_unicode=True, sort_keys=False))
