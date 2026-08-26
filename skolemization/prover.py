"""The public entry point."""

from . import config
from . import narration
from .axioms import add_relation_axioms
from .parsing import aliases
from .parsing.tokenizer import tokenize
from .focus import (
    focus_kb_on_witness,
    kb_contains_witness,
)
from .preprocessing import preprocess
from .search import run_resolution_search


def prove(
    assumptions,
    conclusion,
    symmetric_relations=None,
    transitive_relations=None,
    reflexive_relations=None
):

    """Try to derive ``conclusion`` from ``assumptions``, narrating as it goes.

    Returns "PROVED", "SATURATED_NO_CONTRADICTION" or "UNKNOWN".
    """

    (
        extended_assumptions,
        generated_axioms
    ) = add_relation_axioms(
        assumptions,
        set(symmetric_relations or []),
        set(transitive_relations or []),
        set(reflexive_relations or [])
    )

    narration.relation_axioms(
        generated_axioms
    )

    (
        extended_assumptions,
        generated_axioms
    ) = _add_reflexivity(
        extended_assumptions,
        generated_axioms
    )

    narration.working_assumptions(
        extended_assumptions
    )

    narration.conclusion(
        conclusion
    )

    prepared = (
        preprocess(
            extended_assumptions,
            conclusion,
            axiom_assumptions=_axiom_positions(
                extended_assumptions,
                generated_axioms
            )
        )
    )

    original_kb = prepared.clauses

    if config.FOCUS_ON_WITNESS:

        settled = (
            _try_focusing(
                original_kb,
                prepared
            )
        )

        if settled is not None:
            return settled

    (
        status,
        final_kb
    ) = run_resolution_search(
        original_kb,
        narration.general_search_title(),
        supported=prepared.conclusion_clauses
    )

    narration.final_status(
        status
    )

    return status


def _add_reflexivity(
    assumptions,
    generated_axioms
):

    """The one axiom paramodulation still needs: ``x = x``.

    The rule rewrites equals for equals, which is everything except the very
    last move of an equality proof -- closing a literal like ``c ≠ c``.  That
    takes a resolution against reflexivity, so with the rule on it is supplied
    here rather than left to the reader.  Added only when the problem actually
    mentions equality, and only once.
    """

    if config.EQUALITY_RULE == "none":

        return (
            assumptions,
            generated_axioms
        )

    if not any(
        _mentions_equality(
            text
        )
        for text
        in assumptions
    ):

        return (
            assumptions,
            generated_axioms
        )

    axiom = "all x (x = x)"

    narration.reflexivity_for_equality(
        axiom
    )

    return (
        list(assumptions) + [axiom],
        list(generated_axioms) + [
            (
                "reflexive",
                aliases.EQUALITY,
                axiom
            )
        ]
    )


def _mentions_equality(
    text
):

    """Does this assumption actually use ``=``?

    Asked of the tokenizer rather than of the string, because ``"=" in text``
    is also true of ``=>`` -- an accepted spelling of implication -- and of
    ``!=``.  With the equality rule on by default that would quietly add
    ``x = x`` to problems that never mention equality at all.
    """

    return any(
        token in (
            aliases.EQUALS,
            aliases.NOT_EQUALS
        )
        for token
        in tokenize(
            text
        )
    )


def _axiom_positions(
    extended_assumptions,
    generated_axioms
):

    """Where in the assumption list the generated relation axioms ended up.

    ``add_relation_axioms`` appends them, so they are the tail -- counted off
    the end rather than off the caller's list, which need not be a sequence.
    """

    return range(
        len(extended_assumptions)
        -
        len(generated_axioms),
        len(extended_assumptions)
    )


def _try_focusing(
    kb,
    prepared
):

    """Run the focused attempt, if focusing on a witness means anything here.

    It means nothing in two cases.  Skolemization may have invented no constant
    at all, and then there is no witness to focus on; or it may have invented
    several, and then ``x := c`` is a guess between ``c``, ``c2``, ``c3`` rather
    than a reading of the problem -- so the prover says so and goes straight to
    the general search instead of pinning ``x`` to whichever came first.
    """

    witnesses = prepared.witnesses

    if len(witnesses) > 1:

        narration.focus_skipped_many_witnesses(
            witnesses
        )

        return None

    if not kb_contains_witness(
        kb,
        prepared.witness
    ):

        return None

    return _focused_attempt(
        kb,
        prepared.witness,
        prepared.axiom_clauses,
        prepared.conclusion_clauses
    )


def _focused_attempt(
    kb,
    witness,
    axiom_clauses=frozenset(),
    conclusion_clauses=frozenset()
):

    """Run the witness-focused search.

    Returns a final status when that settles the question, or None when the
    caller should fall through to the general search.  The focus is only a
    heuristic, so failing to prove anything here means nothing on its own.
    """

    (
        status,
        final_kb
    ) = run_resolution_search(
        focus_kb_on_witness(
            kb,
            witness,
            axiom_clauses
        ),
        narration.focused_search_title(
            witness
        ),

        # Say so, because a saturated focused KB is worth explaining but must
        # not be read as an answer: the account words its conclusion
        # differently for a KB that was pinned to the witness.
        focused=True,

        # focus_kb_on_witness returns the same clauses in the same order, so
        # the conclusion's positions carry over untouched.
        supported=conclusion_clauses
    )

    if status == "PROVED":

        narration.final_status(
            status
        )

        return status

    if not config.FALLBACK_TO_GENERAL:

        narration.final_status_unframed(
            status
        )

        return status

    narration.focused_search_failed(
        witness
    )

    return None
