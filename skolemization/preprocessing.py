"""The seven narrated steps that turn assumptions into a clause set.

Steps 2, 3 and 6 have the same shape -- announce, transform each formula,
show before and after -- so they share ``_mapped_step``.  Step 4 is that plus
an explanation of each witness, and steps 1, 5 and 7 only display.

That is the whole-KB order: each step across every formula.  With
``config.ONE_FORMULA_AT_A_TIME`` the same work is told the other way round --
one formula carried through steps 2-7 before the next one starts, in
``_walk_each_formula`` -- and the two produce the same clauses in the same
order.  Step 1 is whole-KB either way.
"""

from dataclasses import dataclass

from . import config
from . import narration
from .formulas import Not
from .parsing import Parser
from .signature import signature_of
from .steps.clausify import extract_clauses
from .steps.cnf import to_cnf
from .steps.forall import remove_forall
from .steps.implications import remove_implications
from .steps.nnf import to_nnf
from .sorts import (
    sorts_of_formulas,
    variable_universes,
)
from .steps.skolemize import (
    SkolemNames,
    skolemize,
)


@dataclass(frozen=True)
class Preprocessed:

    """What the pipeline hands to the search."""

    clauses: list
    names: object
    axiom_clauses: frozenset = frozenset()
    conclusion_clauses: frozenset = frozenset()

    # The parsed input, kept for anything that has to talk about the question
    # rather than about the clauses -- counterexample.py evaluates these in the
    # model it builds, which is how a counter-model is checked rather than
    # asserted.
    assumption_formulas: tuple = ()
    conclusion_formula: object = None

    @property
    def witness(self):
        """The name skolemization gives its first constant."""

        return self.names.witness

    @property
    def witnesses(self):
        """Every witness constant skolemization invented, in order."""

        return self.names.witnesses


def preprocess(
    assumptions,
    conclusion,
    axiom_assumptions=()
):

    """Parse, check the signature, negate the conclusion, and clausify.

    Returns a :class:`Preprocessed`, not a bare clause list: the Skolem names
    are chosen here from the problem's vocabulary, and the focused search needs
    to know which witness they settled on.

    ``axiom_assumptions`` are the positions, in ``assumptions``, of the ones
    ``prove`` generated from declared relation properties rather than the user
    writing them.  Nothing here treats them differently -- they are clausified
    like everything else -- but the result records which clauses came out of
    them, because the focused pass must leave those general (focus.py).
    """

    formulas, sources = (
        _parse_all(
            assumptions,
            conclusion
        )
    )

    # Before anything is printed: a symbol used two ways means the search
    # cannot connect where the reader expects, so refuse rather than narrate a
    # confident wrong answer.
    signature = (
        signature_of(
            formulas,
            sources
        )
    )

    names = (
        SkolemNames(
            signature.names
        )
    )

    axiom_formulas = frozenset(
        axiom_assumptions
    )

    _listed_step(
        1,
        formulas
    )

    if config.ONE_FORMULA_AT_A_TIME:

        (
            clauses,
            axiom_clauses,
            conclusion_clauses
        ) = _walk_each_formula(
            formulas,
            names,
            axiom_formulas
        )

        return Preprocessed(
            clauses,
            names,
            axiom_clauses,
            conclusion_clauses,
            tuple(formulas[:-1]),
            formulas[-1].x
        )

    no_implications = (
        _mapped_step(
            2,
            formulas,
            remove_implications,
            note=narration.implication_rule
        )
    )

    nnf = (
        _mapped_step(
            3,
            no_implications,
            to_nnf
        )
    )

    universes = sorts_of_formulas(
        nnf
    )

    names.plan(
        nnf,
        universes
    )

    skolemized = (
        _skolemization_step(
            nnf,
            names,
            universes
        )
    )

    without_forall = (
        _mapped_step(
            5,
            skolemized,
            remove_forall
        )
    )

    cnf = (
        _mapped_step(
            6,
            without_forall,
            to_cnf,
            note=narration.cnf_rule
        )
    )

    (
        clauses,
        axiom_clauses,
        conclusion_clauses
    ) = _clauses_step(
        cnf,
        axiom_formulas
    )

    return Preprocessed(
        clauses,
        names,
        axiom_clauses,
        conclusion_clauses,
        tuple(formulas[:-1]),
        formulas[-1].x
    )


def _parse_all(
    assumptions,
    conclusion
):

    """Parse everything, negating the conclusion.  Prints nothing.

    Returns the formulas and, alongside them, the text each came from -- the
    signature check quotes it when a symbol is used two ways.
    """

    formulas = []
    sources = []

    for text in assumptions:

        formulas.append(
            Parser(
                text
            ).parse()
        )

        sources.append(
            text
        )

    formulas.append(
        Not(
            Parser(
                conclusion
            ).parse()
        )
    )

    sources.append(
        conclusion
    )

    return (
        formulas,
        sources
    )


def _listed_step(
    number,
    formulas
):

    """A step whose whole output is the resulting formula list."""

    narration.step_header(
        number
    )

    narration.formula_list(
        formulas
    )

    narration.step_kb(
        formulas
    )

    return formulas


def _mapped_step(
    number,
    formulas,
    transform,
    note=None
):

    """Apply ``transform`` to each formula, showing it before and after.

    A formula the transform leaves alone is not narrated at all -- a
    before/after pair of identical text only buries the ones that did change.
    The closing KB lists every formula regardless, so nothing is lost.
    """

    narration.step_header(
        number
    )

    if note is not None:
        note()

    result = []
    changed = 0

    for i, formula in enumerate(
        formulas,
        1
    ):

        rewrites = []

        new_formula = (
            transform(
                formula,
                rewrites=rewrites
            )
        )

        if (
            new_formula != formula
            or
            config.SHOW_UNCHANGED_FORMULAS
        ):

            changed += 1

            narration.formula_before(
                i,
                formula
            )

            narration.rewrites(
                rewrites
            )

            narration.formula_after(
                new_formula
            )

        result.append(
            new_formula
        )

    if not changed:
        narration.nothing_changed()

    narration.step_kb(
        result
    )

    return result


def _skolemization_step(
    formulas,
    names,
    universes
):

    """Step 4, which explains each witness between the before and the after.

    One ``SkolemNames`` for the whole KB, so constants and functions are
    numbered once across every formula rather than restarting each time.
    """

    narration.step_header(
        4
    )

    result = []

    for i, formula in enumerate(
        formulas,
        1
    ):

        explanations = []

        new_formula = (
            skolemize(
                formula,
                names,
                explanations=explanations,
                universes=variable_universes(
                    formula,
                    universes
                )
            )
        )

        narration.formula_before(
            i,
            formula
        )

        narration.skolem_explanations(
            explanations
        )

        narration.formula_after(
            new_formula
        )

        result.append(
            new_formula
        )

    narration.step_kb(
        result
    )

    return result


def _walk_each_formula(
    formulas,
    names,
    axiom_formulas=frozenset()
):

    """Steps 2-7, one formula at a time -- ``config.ONE_FORMULA_AT_A_TIME``.

    The other order of the same work: instead of a step sweeping the whole KB,
    a formula is carried from its written form down to its own clauses before
    the next one starts.  It comes out identical, because every transform is a
    function of one formula and the shared ``SkolemNames`` is still consumed in
    formula order, so the witnesses land where they always did.

    Returns what ``_clauses_step`` returns, for the same reason.
    """

    clauses = []

    axiom_clauses = set()

    conclusion_clauses = set()

    # The witnesses have to be named the same way in both orders, and naming
    # them needs the whole KB: which universes there are, and how many
    # witnesses each will want.  So the NNF of every formula is computed up
    # front -- pure functions, no narration -- and only then does the walk
    # begin.  Without this the first formula would be skolemized before the
    # last one had been looked at, and the two orders would drift apart.
    upcoming = [
        to_nnf(
            remove_implications(
                formula
            )
        )
        for formula
        in formulas
    ]

    universes = sorts_of_formulas(
        upcoming
    )

    names.plan(
        upcoming,
        universes
    )

    for i, formula in enumerate(
        formulas,
        1
    ):

        narration.walk_header(
            i,
            len(formulas),
            formula
        )

        current = (
            _walk_step(
                2,
                formula,
                remove_implications,
                note=narration.implication_rule
            )
        )

        current = (
            _walk_step(
                3,
                current,
                to_nnf
            )
        )

        current = (
            _walk_skolem_step(
                current,
                names,
                universes
            )
        )

        current = (
            _walk_step(
                5,
                current,
                remove_forall
            )
        )

        current = (
            _walk_step(
                6,
                current,
                to_cnf,
                note=narration.cnf_rule
            )
        )

        from_this_formula = (
            extract_clauses(
                current
            )
        )

        narration.walk_clauses(
            i,
            from_this_formula
        )

        produced = range(
            len(clauses),
            len(clauses)
            +
            len(from_this_formula)
        )

        if i - 1 in axiom_formulas:

            axiom_clauses.update(
                produced
            )

        # The negated conclusion is the last formula -- see _parse_all.
        if i == len(formulas):

            conclusion_clauses.update(
                produced
            )

        clauses.extend(
            from_this_formula
        )

    narration.clause_kb(
        clauses
    )

    return (
        clauses,
        frozenset(
            axiom_clauses
        ),
        frozenset(
            conclusion_clauses
        )
    )


def _walk_step(
    number,
    formula,
    transform,
    note=None
):

    """One step of one formula's walk.

    Unlike ``_mapped_step``, a step that changes nothing still announces
    itself: in this order the steps are a chain, and a silent one would read as
    a step that never ran rather than as a step with nothing to do.
    """

    narration.walk_step(
        number
    )

    if note is not None:
        note()

    rewrites = []

    new_formula = (
        transform(
            formula,
            rewrites=rewrites
        )
    )

    if (
        new_formula == formula
        and
        not config.SHOW_UNCHANGED_FORMULAS
    ):

        narration.formula_unchanged()

        return new_formula

    narration.formula_state_before(
        formula
    )

    narration.rewrites(
        rewrites
    )

    narration.formula_after(
        new_formula
    )

    return new_formula


def _walk_skolem_step(
    formula,
    names,
    universes
):

    """Step 4 of one formula's walk, explaining each witness it invents."""

    narration.walk_step(
        4
    )

    explanations = []

    new_formula = (
        skolemize(
            formula,
            names,
            explanations=explanations,
            universes=variable_universes(
                formula,
                universes
            )
        )
    )

    narration.formula_state_before(
        formula
    )

    narration.skolem_explanations(
        explanations
    )

    narration.formula_after(
        new_formula
    )

    return new_formula


def _clauses_step(
    formulas,
    axiom_formulas=frozenset()
):

    """Step 7: read the clauses off the CNF.

    Returns the clauses and, with them, two sets of positions: the ones that
    came out of a generated relation axiom, and the ones that came out of the
    negated conclusion -- one formula can yield several clauses, so both have
    to be tracked as it happens rather than counted afterwards.
    """

    clauses = []

    axiom_clauses = set()

    conclusion_clauses = set()

    for i, formula in enumerate(
        formulas
    ):

        from_this_formula = (
            extract_clauses(
                formula
            )
        )

        produced = range(
            len(clauses),
            len(clauses)
            +
            len(from_this_formula)
        )

        if i in axiom_formulas:

            axiom_clauses.update(
                produced
            )

        # The negated conclusion is the last formula -- see _parse_all.
        if i == len(formulas) - 1:

            conclusion_clauses.update(
                produced
            )

        clauses.extend(
            from_this_formula
        )

    narration.step_header(
        7
    )

    narration.clause_kb(
        clauses
    )

    return (
        clauses,
        frozenset(
            axiom_clauses
        ),
        frozenset(
            conclusion_clauses
        )
    )
