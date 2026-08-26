"""What the prover says, in each language it says it in.

``narration.py`` owns the *layout* -- the banners, the indentation, which
bindings are worth printing, what a step's account looks like.  This package
owns the *wording*, one module per language, so adding a language is a second
table rather than a second narrator and the structure cannot drift between
them.

The catalogues are checked against each other at import: a key present in one
language and missing from another raises immediately, rather than turning into
a ``KeyError`` in the middle of a proof in whichever language nobody was
reading at the time.
"""

from .lookup import (
    direction,
    phrase,
    phrase_table,
)
