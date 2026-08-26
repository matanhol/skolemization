"""Are two formulas logically equivalent?

Equivalence is two entailments, so this runs two ordinary proofs::

    φ1 ≡ φ2      iff      φ1 ⊨ φ2   and   φ2 ⊨ φ1

Both directions are narrated in full, then the verdict.  Note what a negative
means: the solver failing to prove a direction is not a proof that the
direction is false, so ``equivalent`` being False says only that equivalence
was not established -- see the note on SATURATED_NO_CONTRADICTION in
search.py.

    from skolemization import Equivalence

    Equivalence(
        "all x P(x)",
        "not (exists x (not P(x)))",
    ).check()
"""

from dataclasses import dataclass

from . import narration
from .prover import prove


@dataclass(frozen=True)
class EquivalenceResult:

    """How each direction went."""

    forward: str
    backward: str

    @property
    def equivalent(self):
        """True only when both entailments were actually proved."""

        return (
            self.forward == "PROVED"
            and
            self.backward == "PROVED"
        )


class Equivalence:

    """A pair of formulas, and the question of whether they say the same thing.

    The names are what the narration prints (``φ1 ⊨ φ2``); give them something
    meaningful and the transcript reads as your own problem rather than as
    anonymous formulas.

    Relation properties pass straight through to :func:`prove`, so an
    equivalence stated in terms of ``Eq`` can declare it symmetric exactly the
    way a single proof would.
    """

    def __init__(
        self,
        first,
        second,
        first_name="φ1",
        second_name="φ2",
        symmetric_relations=None,
        transitive_relations=None,
        reflexive_relations=None
    ):

        """Hold the two formulas and how their relations behave."""

        self.first = first
        self.second = second

        self.first_name = first_name
        self.second_name = second_name

        self.symmetric_relations = symmetric_relations
        self.transitive_relations = transitive_relations
        self.reflexive_relations = reflexive_relations

    def forward(self):

        """Try ``first ⊨ second``, narrated as direction 1."""

        return self._entails(
            1,
            self.first,
            self.second,
            self.first_name,
            self.second_name
        )

    def backward(self):

        """Try ``second ⊨ first``, narrated as direction 2."""

        return self._entails(
            2,
            self.second,
            self.first,
            self.second_name,
            self.first_name
        )

    def check(self):

        """Run both directions, announce the verdict, and return the result."""

        result = EquivalenceResult(
            self.forward(),
            self.backward()
        )

        narration.equivalence_verdict(
            result,
            self.first_name,
            self.second_name
        )

        return result

    def _entails(
        self,
        index,
        assumption,
        conclusion,
        from_name,
        to_name
    ):

        """One direction: announce it, then hand the work to ``prove``."""

        narration.equivalence_direction(
            index,
            from_name,
            to_name
        )

        return prove(
            assumptions=[assumption],
            conclusion=conclusion,
            symmetric_relations=self.symmetric_relations,
            transitive_relations=self.transitive_relations,
            reflexive_relations=self.reflexive_relations
        )
