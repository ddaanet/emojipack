"""Command line interface for emojipack."""
# ruff: noqa: FBT001, FBT002
# Boolean arguments are required for typer CLI flags

import importlib.resources
import shlex
from pathlib import Path
from typing import TypedDict

import typer
import yaml

from emojipack.comparison import (
    EmojiMatch,
    KeywordMatch,
    SnippetPackComparison,
    compare_packs,
)
from emojipack.download import fetch_gemoji_data
from emojipack.pack import SnippetPack
from emojipack.snippets import AlfredSnippet

app = typer.Typer()


class EmojisNormal(TypedDict):
    """Emoji comparison output in normal mode."""

    removed: list[str]
    found: int
    added_emoji_presentation: int
    removed_space: int
    added: int


class KeywordsNormal(TypedDict):
    """Keyword comparison output in normal mode."""

    removed: dict[str, str]
    modified: dict[str, dict[str, str]]
    matching: int
    added: int


class CompareOutputNormal(TypedDict):
    """Normal mode compare output structure."""

    emojis: EmojisNormal
    keywords: KeywordsNormal


class EmojisVerbose(TypedDict):
    """Emoji comparison output in verbose mode."""

    removed: dict[str, list[str]]
    found: dict[str, list[str]]
    added_emoji_presentation: dict[str, list[str]]
    removed_space: dict[str, list[str]]
    added: dict[str, list[str]]


class KeywordsVerbose(TypedDict):
    """Keyword comparison output in verbose mode."""

    removed: dict[str, str]
    added: dict[str, str]
    matching: dict[str, str]
    modified: dict[str, dict[str, str]]


class CompareOutputVerbose(TypedDict):
    """Verbose mode compare output structure."""

    emojis: EmojisVerbose
    keywords: KeywordsVerbose


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
    output_quoted = shlex.quote(str(output_path))
    typer.echo(f"Generated {output_quoted} with {len(snippets)} snippets")


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


def _format_emoji_dict_verbose(
    emoji_dict: dict[str, list[AlfredSnippet]],
) -> dict[str, list[str]]:
    """Convert emoji->snippets dict to name->keywords dict."""
    return {
        snippets[0].name: [s.keyword for s in snippets]
        for snippets in emoji_dict.values()
    }


def _format_emoji_match_dict_verbose(
    emoji_dict: dict[str, EmojiMatch],
) -> dict[str, list[str]]:
    """Convert emoji->EmojiMatch dict to name->keywords dict."""
    return {
        match.mine[0].name: [s.keyword for s in match.mine]
        for match in emoji_dict.values()
    }


def _format_keyword_dict_verbose(
    keyword_dict: dict[str, AlfredSnippet],
) -> dict[str, str]:
    """Format keywords as keyword->snippet name."""
    return {keyword: snippet.name for keyword, snippet in keyword_dict.items()}


def _format_keyword_modified(
    keyword_dict: dict[str, KeywordMatch],
) -> dict[str, dict[str, str]]:
    """Format modified keywords as keyword->{theirs: name, mine: name}."""
    return {
        keyword: {"theirs": match.theirs.name, "mine": match.mine.name}
        for keyword, match in keyword_dict.items()
    }


def _format_compare_verbose(
    result: SnippetPackComparison,
) -> CompareOutputVerbose:
    """Format comparison result in verbose mode."""
    emojis = EmojisVerbose(
        removed=_format_emoji_dict_verbose(result.emojis.removed),
        found=_format_emoji_match_dict_verbose(result.emojis.found),
        added_emoji_presentation=_format_emoji_match_dict_verbose(
            result.emojis.added_emoji_presentation
        ),
        removed_space=_format_emoji_match_dict_verbose(
            result.emojis.removed_space
        ),
        added=_format_emoji_dict_verbose(result.emojis.added),
    )
    keywords = KeywordsVerbose(
        removed=_format_keyword_dict_verbose(result.keywords.removed),
        added=_format_keyword_dict_verbose(result.keywords.added),
        matching=_format_keyword_dict_verbose(result.keywords.matching),
        modified=_format_keyword_modified(result.keywords.modified),
    )
    return CompareOutputVerbose(emojis=emojis, keywords=keywords)


def _format_compare_normal(
    result: SnippetPackComparison,
) -> CompareOutputNormal:
    """Format comparison result in normal mode."""
    emojis = EmojisNormal(
        removed=_format_emoji_dict(result.emojis.removed),
        found=len(result.emojis.found),
        added_emoji_presentation=len(result.emojis.added_emoji_presentation),
        removed_space=len(result.emojis.removed_space),
        added=len(result.emojis.added),
    )
    keywords = KeywordsNormal(
        removed=_format_keyword_dict_verbose(result.keywords.removed),
        modified=_format_keyword_modified(result.keywords.modified),
        matching=len(result.keywords.matching),
        added=len(result.keywords.added),
    )
    return CompareOutputNormal(emojis=emojis, keywords=keywords)


@app.command()
def compare(theirs: Path, mine: Path, verbose: bool = False) -> None:
    """Compare two emoji snippet packs."""
    theirs_pack = SnippetPack.read(theirs)
    mine_pack = SnippetPack.read(mine)
    result = compare_packs(theirs_pack, mine_pack)

    output: CompareOutputNormal | CompareOutputVerbose
    if verbose:
        output = _format_compare_verbose(result)
    else:
        output = _format_compare_normal(result)
    typer.echo(
        yaml.dump(output, allow_unicode=True, sort_keys=False), nl=False
    )
