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
from .counterexample import (
    LARGEST_DOMAIN,
    describe,
    finite_model,
    why,
    witnesses_by_universe,
)
from .sorts import sorts_of_clauses
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

    if (
        status == "SATURATED_NO_CONTRADICTION"
        and
        config.EXPLAIN_COUNTEREXAMPLE
    ):

        _build_countermodel(
            final_kb,
            prepared
        )

    narration.final_status(
        status
    )

    return status


def _build_countermodel(
    final_kb,
    prepared
):

    """Read the model out of a saturated KB, and check it against the question.

    A model of the surviving clauses is a model of the original ones -- the
    only thing ever deleted is a clause its survivors imply -- so it satisfies
    the assumptions and the negated conclusion, which is exactly what a
    counter-example is.  That is guaranteed in theory and *checked* here, by
    evaluating the parsed question in the structure: a wrong verdict would mean
    the model, the saturation or the evaluator is broken, and it is printed
    rather than smoothed over.

    A set of support refuses: that search never tried the inferences among the
    assumptions, so its running dry says nothing about satisfiability.
    """

    if config.SET_OF_SUPPORT:

        narration.countermodel_refused(
            False
        )

        return

    model, given_up = finite_model(
        final_kb
    )

    if model is None:

        narration.countermodel_not_found(
            LARGEST_DOMAIN
        )

        return

    # The finite model is never printed.  It is the proof that what follows is
    # satisfiable rather than merely plausible; what the reader gets is the
    # description, with the universals left standing.
    sorts = sorts_of_clauses(
        prepared.clauses
    )

    elements = _witness_elements(
        model,
        final_kb
    )

    checks = []

    for formula in prepared.assumption_formulas:

        checks.append(
            _checked(
                formula,
                model,
                elements,
                False
            )
        )

    checks.append(
        _checked(
            prepared.conclusion_formula,
            model,
            elements,
            True
        )
    )

    narration.countermodel(
        witnesses_by_universe(
            final_kb,
            sorts
        ),
        describe(
            final_kb,
            prepared.predicate_order
        ),
        checks,
        all(
            verdict != is_conclusion
            for _, verdict, is_conclusion, _
            in checks
        )
    )


def _witness_elements(
    model,
    clauses
):

    """Which domain element each Skolem constant denotes.

    The finite model is never printed -- it is the proof that the description
    is satisfiable -- but an explanation that points at an element points at it
    by the name the reader already has.
    """

    names = {}

    for clause in clauses:

        for literal in clause:

            for argument in literal.atom.args:

                if argument.is_var or argument.args:
                    continue

                names.setdefault(
                    model.constants.get(
                        argument.name
                    ),
                    argument.name
                )

    return names


def _checked(
    formula,
    model,
    elements,
    is_conclusion
):

    """One formula, its verdict, and why -- with elements named as witnesses.

    The model's elements are integers and the model is never printed, so the
    only handle the reader has on one is the witness name the clauses gave it
    (``c1``); an element the clauses never named prints as ``?``, and carries
    no explanation of its own, there being no name to instantiate a body with.

    The naming is ``why``'s to do, not ours, which is why ``elements`` is
    handed down rather than applied to what comes back.  A reason that names an
    element also shows its quantifier's body *instantiated at that element* --
    ``P(c3)``, not ``P(x)`` -- and that formula can only be built where the
    formulas are built, with the name already in hand.  Renaming afterwards
    would mean carrying a binding down the whole reason tree and doing formula
    surgery here, in the module that knows least about it.
    """

    verdict, reason = why(
        formula,
        model,
        elements
    )

    return (
        formula,
        verdict,
        is_conclusion,
        reason
    )


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
