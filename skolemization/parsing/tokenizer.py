"""Text in, canonical tokens out.

Every accepted spelling collapses here, so the parser only ever sees the
canonical forms listed in aliases.py.  Anything that is not a spelling passes
through untouched, which is how predicate and variable names survive with
their case intact.
"""

import re

from . import aliases


TOKEN_RE = re.compile(
    r"\s*("
    + "|".join(
        re.escape(symbol)
        for symbol
        in aliases.matchable_symbols()
    )
    + r"|[A-Za-z_][A-Za-z0-9_]*)"
)


def tokenize(text):
    """Split ``text`` into canonical tokens.

    Whitespace never survives tokenizing, which is what makes multi-word
    spellings insensitive to spacing: by the time phrases are matched,
    ``FoR   aLL`` and ``for all`` are both the token pair ("for", "all").
    """

    raw = TOKEN_RE.findall(
        text
    )

    result = []

    position = 0

    while position < len(raw):

        phrase = _phrase_at(
            raw,
            position
        )

        if phrase is not None:

            canonical, length = phrase

            result.append(
                canonical
            )

            position += length

            continue

        token = raw[position]

        result.append(
            aliases.SYMBOL_ALIASES.get(
                token,
                token
            )
        )

        position += 1

    return result


def _phrase_at(
    raw,
    position
):

    """The word spelling starting at ``position``, as (canonical, length).

    Longest first, so ``for all`` is preferred over the ``all`` inside it.
    Returns None when no spelling starts here -- including the common case of
    an ordinary identifier.
    """

    longest = min(
        aliases.LONGEST_PHRASE,
        len(raw) - position
    )

    for length in range(
        longest,
        0,
        -1
    ):

        words = tuple(
            token.lower()
            for token
            in raw[position:position + length]
        )

        if words in aliases.WORD_ALIASES:

            return (
                aliases.WORD_ALIASES[words],
                length
            )

    return None
