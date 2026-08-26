"""Every spelling the parser accepts, in one table.

This is the only place spellings are written down.  Both the tokenizer's regex
and its lookup are derived from the tables below, so adding a spelling here is
the whole job -- there is nothing else to touch::

    WORDS[AND].append("&&&")      # accepted immediately

Two rules apply to everything here:

* **Case is ignored.**  ``all``, ``All`` and ``ALL`` are the same word.  Only
  keywords are case-folded; predicate and variable names keep their case, so
  ``P(x)`` and ``p(x)`` remain different predicates.
* **Spacing is ignored.**  A multi-word spelling tolerates any run of
  whitespace between its words, newlines included, because the words are
  matched after tokenizing rather than as raw text.  ``FoR   aLL`` is
  ``for all`` is ``forall``.
"""


# ================================================================
# CANONICAL TOKENS
# ================================================================
#
# What the parser itself matches on.  Every spelling below collapses to one
# of these before the parser ever sees it.

FORALL = "forall"
EXISTS = "exists"
NOT = "not"
AND = "and"
OR = "or"
IMPLIES = "->"
EQUALS = "="
NOT_EQUALS = "!="


# The predicate an ``x = y`` becomes.  Nothing else can be called this -- a
# name must match NAME_RE -- so equality can never collide with a predicate the
# problem defines, and everything downstream treats it as an ordinary binary
# predicate.  ``formulas.EQUALITY`` is the same string, spelled again there so
# that the printer does not have to import the parser; keep the two in step.

EQUALITY = "="


# ================================================================
# SPELLINGS
# ================================================================

WORDS = {
    FORALL: [
        "forall",
        "for all",
        "all",
    ],
    EXISTS: [
        "exists",
        "exist",
        "there exists",
        "there exist",
    ],
    NOT: [
        "not",
    ],
    AND: [
        "and",
    ],
    OR: [
        "or",
    ],
    IMPLIES: [
        "implies",
    ],
}


# ``!`` is negation -- the usual programming-language reading -- not a
# quantifier.  ``?`` stays existential, matching the ``∃`` it stands in for.

SYMBOLS = {
    FORALL: [
        "∀",
    ],
    EXISTS: [
        "∃",
        "?",
    ],
    NOT: [
        "¬",
        "~",
        "!",
    ],
    AND: [
        "∧",
        "&&",
        "&",
    ],
    OR: [
        "∨",
        "||",
        "|",
    ],
    IMPLIES: [
        "→",
        "-->",
        "->",
        "=>",
    ],
    EQUALS: [
        "=",
    ],
    NOT_EQUALS: [
        "≠",
        "!=",
        "/=",
    ],
}


# Structural tokens.  No aliases, and the parser matches them literally.

PUNCTUATION = [
    "(",
    ")",
    ",",
    ":",
]


# ================================================================
# DERIVED LOOKUPS
# ================================================================

def _word_lookup():
    """Map each word spelling, split and lowercased, to its canonical token."""

    table = {}

    for canonical, spellings in WORDS.items():

        for spelling in spellings:

            table[
                tuple(
                    spelling.lower().split()
                )
            ] = canonical

    return table


def _symbol_lookup():
    """Map each symbol spelling to its canonical token."""

    return {
        spelling: canonical
        for canonical, spellings
        in SYMBOLS.items()
        for spelling
        in spellings
    }


WORD_ALIASES = _word_lookup()

SYMBOL_ALIASES = _symbol_lookup()

# The canonical tokens as a set, for telling a keyword from a name.  A bare
# word that is not in here is a predicate or a variable.

CANONICAL_TOKENS = (
    set(WORDS)
    |
    set(SYMBOLS)
)

# How many tokens the longest multi-word spelling spans, so the tokenizer
# knows how far ahead to look.

LONGEST_PHRASE = max(
    len(words)
    for words
    in WORD_ALIASES
)


def matchable_symbols():
    """Symbols and punctuation, longest first.

    Order matters: the tokenizer alternates over these, so ``-->`` has to be
    offered before ``->`` and ``&&`` before ``&``, or the shorter spelling
    would win and leave a stray character behind.
    """

    return sorted(
        set(SYMBOL_ALIASES)
        |
        set(PUNCTUATION),
        key=len,
        reverse=True
    )
