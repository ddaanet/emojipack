# TODO

- comparison: add categories
  - found (exact content match)
  - added emoji presentation marker
  - removed space (unicorn)
- Repeat following check until no emoji appears removed:
  - run comparison,
  - pick the first emoji removed from Joel's
  - find by keyword in my snippets
  - compare content
- Keyword comparison: for emojis in both, list added and removed keywords.
- Search words comparison: for emojis in both, list names, split words, do NOT
  remove punctuation, add snippet with affix to match Alfred search, list added
  and removed words.
- Generation: remove needless search words that have another search word for
  the same emoji as prefix
- Correctly process country flags
- Provide Joel compatibility packs
  1. Keyword coverage: Support all keywords from Joel. Snippet may change
     slightly (combined/unified). Produce list of missing keywords for
     regression testing.
  2. Search word coverage: for each emoji, ensure the keyword + name for each
     snippet in our pack includes all the words present in keyword + name in
     Joel's. Produce list of missing search words by emoji, for regression
     testing.
  3. uid stability: for each snippet, retrieve uid from Joel and reuse (unify
     emoji first). This one is not subject to regression. Extract list of uids
     by keyword, store in git, add CLI option --joels-uid to reuse them.
- Download cldr database
  <https://raw.githubusercontent.com/yui019/emoji-names/main/cldr_annotations_en.xml>
  - Filter out emojis that are not in snippets.
  - Remove plural ("s", "'s", "es"), variants ("er" or worker, "ty" of royalty,
    only if base word is in list: "fireworks" should not be singular)
  - Remove words that are present in matching snippets keywords and names.
    keyword "oil drum" -> omit search words "oil" and "drum"
  - Produce mapping of emoji (unified) to list of extra search words.
- Analysis of additional search word distribution. Consider strategies for
  removing keywords. Keep only the n first, remove the most frequently used,
  maybe other.
