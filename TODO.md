# TODO

- Create snippet pack class for MacOS text expansions
- compare to joel's
- Remove needless keywords that have another keyword for the same emoji as
  prefix
- Correctly process country flags
- Download cldr database: https://raw.githubusercontent.com/yui019/emoji-names/refs/heads/main/cldr_annotations_en.xml
- Reuse download cache mechanism
- For improved search, get search keywords from cldr annotations
  - Only for snippets already defined (no adding snippets)
  - Remove plural ("s", "'s", "es"), variants ("er" or worker, "ty" of royalty)
  - Remove keywords already present in trigger: "oil drum" -> "oil" and "drum"

