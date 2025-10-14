"""Command line interface for emojipack."""

from pathlib import Path

import typer

from emojipack.download import fetch_gemoji_data
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

app = typer.Typer()


@app.command()
def main() -> None:
    """Generate Emoji Snippet Pack for Alfred."""
    output_path = Path("Emoji Pack.alfredsnippets")
    emoji_data = fetch_gemoji_data()
    snippets = [
        AlfredSnippet.from_gemoji(entry, alias)
        for entry in emoji_data
        for alias in entry["aliases"]
    ]
    pack = SnippetPack(prefix=":", suffix=":", snippets=snippets)
    pack.write(output_path)
    typer.echo(f"Generated {output_path} with {len(snippets)} snippets")
