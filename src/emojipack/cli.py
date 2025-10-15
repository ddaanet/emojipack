"""Command line interface for emojipack."""
# ruff: noqa: FBT001, FBT002
# Boolean arguments are required for typer CLI flags

import importlib.resources
from pathlib import Path

import typer

from emojipack.download import fetch_gemoji_data
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

app = typer.Typer()


@app.command()
def main(macos: bool = False) -> None:
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
