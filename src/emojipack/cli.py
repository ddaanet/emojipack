"""Command line interface for emojipack."""

import typer

app = typer.Typer()


@app.command()
def main() -> None:
    """Generate Emoji Snippet Pack for Alfred."""
