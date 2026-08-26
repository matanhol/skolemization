"""One derivation step, whichever rule produced it.

The search treats resolution and factoring uniformly -- both consume clauses
already in the KB and produce one new clause -- so both arrive as this record.
"""

from dataclasses import dataclass
from typing import Tuple


RESOLUTION = "resolution"
FACTORING = "factoring"
PARAMODULATION = "paramodulation"


@dataclass(frozen=True)
class Inference:

    """A candidate step: what it used, what it matched, what it produced.

    ``parents`` holds one or two KB indices.  Two is the ordinary resolution
    case.  One means the step used a single clause -- either factoring, or a
    resolution of a clause against a renamed copy of itself -- and keeping it
    to one entry is what stops the subsumption check from visiting, and
    deleting, the same clause twice.

    ``literal1`` and ``literal2`` are the two literals the rule matched, drawn
    from the standardized-apart copies rather than from the KB clauses, so
    they read with the variable names the step actually unified.
    """

    kind: str
    parents: Tuple[int, ...]
    literal1: object
    literal2: object
    substitution: dict
    result: list

    # What the rule produced before ``t ≠ t`` literals were dropped from it,
    # or None when there were none to drop.  Kept so the narration can show
    # the step's own output and then the simplification, rather than a result
    # the reader cannot derive from the parents.
    before_dropping: object = None

    # For a paramodulation step: which side of the equation replaced which,
    # the subterm it landed on, and the literal on both sides of the swap.
    # None for the other two rules, which have nothing of the kind to report.
    replacement: object = None

    def parent_clauses(
        self,
        kb
    ):
        """The clauses this step consumed, in KB order."""

        return [
            kb[index]
            for index
            in self.parents
        ]

    def parent_size(
        self,
        kb
    ):
        """Total literals across the parents, for tie-breaking."""

        return sum(
            len(kb[index])
            for index
            in self.parents
        )
