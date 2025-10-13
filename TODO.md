# TODO

- Download database
  - Test download code, by patching requests. red
  - Download implementation. Is explicit raise_for_status needed?

    ```py
    def fetch_emoji_data(self) -> list[EmojiData]:
        """Fetch emoji data from iamcal/emoji-data repository."""
        url = (
          "https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json"
        )
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        response.json()
    ```
    green
  - Test caching in data dir. red
  - Implement caching. green.

- Iterate database with appropriate typing
  - Pick 😃 and 👍 from downloaded data as sample to patch `requests`.
  - Verify the loading code return two instances with the right values.
  - emoji, description, aliases, tags
- Alternately, combine

- Each database entry can produce:
  - Trigger phrases
  - Emoji (unified form)
  - Name, descriptive and simple
  - Additional keywords for search
  - emoji as hex code sequences (for uid generation)
- Create snippet pack class with appropriate type
  - Whatever goes in the plist
    - prefix and suffix
  - List of alfred snippets
    - keyword (under to space), name + search keywords, emoji, uuid, autoexpand
- Write snippet pack class to disk
- Create snippet pack class for MacOS text expansions
- compare to joel's
- Remove needless keywords that haveanother keyword for the same emoji as
  prefix
- Correctly process country flags
- Download cldr database: https://raw.githubusercontent.com/yui019/emoji-names/refs/heads/main/cldr_annotations_en.xml
- Reuse download cache mechanismff
- For improved search, get search keywords from cldr annotations
  - Only for snippets already defined (no adding snippets)
  - Remove plural ("s", "'s", "es"), variants ("er" or worker, "ty" of royalty)
  - Remove keywords already present in trigger: "oil drum" -> "oil" and "drum"

