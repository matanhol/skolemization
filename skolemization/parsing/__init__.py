"""Source text in, formula trees out.

    aliases.py     every accepted spelling, and the canonical token it becomes
    tokenizer.py   text -> canonical tokens
    parser.py      canonical tokens -> formula tree

Accepted spellings, case-insensitively and with any spacing between the words
of a multi-word form:

    forall      forall / for all / all / ∀
    exists      exists / exist / there exists / there exist / ∃ / ?
    not         not / ¬ / ~ / !
    and         and / ∧ / && / &
    or          or / ∨ / || / |
    ->          implies / → / --> / -> / =>

Note that ``!`` is negation, not a quantifier.  The symbols the narration
prints (∀ ∃ ¬ ∧ ∨ →) are all accepted as input too, so output can be pasted
back in.

A quantifier carries across a list of variables, so these all say the same
thing::

    all x, y, z P(x,y,z)
    all x y z P(x,y,z)
    all x, all y, all z P(x,y,z)

and a different quantifier just starts its own list::

    there exist x, y, all z B(x,y,z)      ->   ∃x ∃y ∀z B(x, y, z)

To add a spelling, edit ``aliases.py`` and nothing else.
"""

from .parser import Parser
from .tokenizer import tokenize

__all__ = [
    "Parser",
    "tokenize",
]
