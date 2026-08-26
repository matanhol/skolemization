"""Reading the shape of a counter-model out of a saturated knowledge base.

A refutation is not the only thing a resolution search can produce.  When it
runs dry the other half of the completeness theorem applies: a clause set
saturated under a complete calculus with no □ in it *is* satisfiable, and the
usual proof is constructive.  So ``SATURATED_NO_CONTRADICTION`` is not "I gave
up" -- there is a model in there, and the clauses that came from the **negated
conclusion** say what it has to look like.

This module walks the pipeline backwards.  Take those clauses, let the units
the search found simplify them, and then undo the steps::

    7  the clauses become a conjunction of disjunctions
    6  skipped -- undoing distribution is not unique, and CNF reads fine
    5  the free variables are closed universally
    4  SKIPPED ON PURPOSE -- the Skolem witnesses stay
    3  skipped -- negation normal form reads fine
    2  ¬A ∨ B folds back into A → B, where that reads better
    1  negating the whole thing says what the conclusion would have needed

Step 4 is the one that must not be undone.  Un-Skolemizing would turn ``c4``
back into a quantifier and hand back something close to the conclusion; keeping
it makes the result a statement about a named witness, which is what a
counter-model is::

    ¬P(c4) ∧ ∀x ∀y ¬Q(x, y)          "c4 is not P, and Q is empty"

Nothing here decides anything: it is an account, printed after the answer is
already fixed, under ``config.EXPLAIN_COUNTEREXAMPLE``.
"""

from .formulas import (
    And,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
)
from .steps.nnf import to_nnf
from .subsumption import (
    clause_subsumes,
    match_literal,
)


def simplify_against_units(
    clauses,
    kb
):

    """The conclusion's clauses, reduced by the one-literal clauses of ``kb``.

    A unit may be **instantiated** to cancel a literal; the clause may not.
    That asymmetry is the whole rule and it is what makes this sound: a unit is
    universally quantified, so using ``¬Q(x, y)`` as ``¬Q(c4, c5)`` is
    universal instantiation and free, while binding a variable of the *clause*
    would replace it with something stronger than what the search proved.

    ``subsumption.resolve_with_unit`` refuses both, because the sweep it serves
    is rewriting the KB in place and must not narrow a clause it keeps.  Here
    the clauses are being read, not kept, so the weaker guard is the right one.
    """

    units = [
        clause[0]
        for clause
        in kb
        if len(clause) == 1
    ]

    reduced = []

    for clause in clauses:

        remaining = list(
            clause
        )

        changed = True

        while changed:

            changed = False

            for unit in units:

                for literal in list(
                    remaining
                ):

                    if not _unit_cancels(
                        unit,
                        literal
                    ):

                        continue

                    remaining.remove(
                        literal
                    )

                    changed = True

        if remaining:

            reduced.append(
                remaining
            )

    return _drop_subsumed(
        reduced
    )


def _unit_cancels(
    unit,
    literal
):

    """Does this unit, instantiated, cancel this literal?

    Opposite signs, and the unit's atom matches the literal's one way round --
    the unit's variables may be bound, the literal's may not.
    """

    if unit.negated == literal.negated:
        return False

    flipped = type(unit)(
        unit.atom,
        literal.negated
    )

    return match_literal(
        flipped,
        literal,
        {}
    ) is not None


def _drop_subsumed(
    clauses
):

    """Keep only the strongest of the clauses that survived."""

    survivors = []

    for clause in clauses:

        if any(
            clause_subsumes(
                other,
                clause
            )
            for other
            in survivors
        ):

            continue

        survivors = [
            other
            for other
            in survivors
            if not clause_subsumes(
                clause,
                other
            )
        ]

        survivors.append(
            clause
        )

    return survivors


def as_formula(
    clauses
):

    """The clauses read back as one formula -- steps 7, 5 and 2 in reverse.

    The universal closure is what step 5 dropped; the implication is what step
    2 removed.  Step 4 is deliberately not undone, so every Skolem constant
    stays exactly where it is.
    """

    if not clauses:
        return None

    # Each conjunct is closed over its *own* variables, not the conjunction
    # over all of them: ¬P(c4) has no business sitting under a ∀x ∀y it never
    # mentions, and the reading is the point here.
    conjuncts = [
        _close_universally(
            _clause_as_formula(
                clause
            )
        )
        for clause
        in clauses
    ]

    formula = conjuncts[0]

    for conjunct in conjuncts[1:]:

        formula = And(
            formula,
            conjunct
        )

    return formula


def _clause_as_formula(
    clause
):

    """One clause: ``A ∧ B → C`` when it has both signs, a disjunction otherwise."""

    negative = [
        literal
        for literal
        in clause
        if literal.negated
    ]

    positive = [
        literal
        for literal
        in clause
        if not literal.negated
    ]

    if not negative or not positive:

        return _join(
            [
                _literal_as_formula(
                    literal
                )
                for literal
                in clause
            ],
            Or
        )

    return Implies(
        _join(
            [
                literal.atom
                for literal
                in negative
            ],
            And
        ),
        _join(
            [
                literal.atom
                for literal
                in positive
            ],
            Or
        )
    )


def _literal_as_formula(
    literal
):

    """``P(x)`` or ``¬P(x)``, as a formula node."""

    if literal.negated:

        return Not(
            literal.atom
        )

    return literal.atom


def _join(
    parts,
    connective
):

    """Fold a list into one formula with ``connective``, left to right."""

    formula = parts[0]

    for part in parts[1:]:

        formula = connective(
            formula,
            part
        )

    return formula


def _close_universally(
    formula
):

    """Put back the ∀ that step 5 removed, one per free variable."""

    for variable in reversed(
        _free_variables(
            formula
        )
    ):

        formula = ForAll(
            variable,
            formula
        )

    return formula


def _free_variables(
    formula
):

    """Every variable the formula mentions, in the order it first appears."""

    found = []

    def walk_term(term):

        if term.is_var:

            if term.name not in found:

                found.append(
                    term.name
                )

            return

        for argument in term.args:

            walk_term(
                argument
            )

    def walk(node):

        if isinstance(
            node,
            (ForAll, Exists)
        ):

            walk(
                node.body
            )

            return

        if isinstance(node, Not):

            walk(
                node.x
            )

            return

        if isinstance(
            node,
            (And, Or, Implies)
        ):

            walk(
                node.a
            )

            walk(
                node.b
            )

            return

        for argument in node.args:

            walk_term(
                argument
            )

    walk(
        formula
    )

    return found


def what_the_conclusion_needed(
    formula
):

    """The negation of the shape, as a positive statement.

    Undoing step 1.  Pushed into negation normal form with the package's own
    ``to_nnf``, so ``¬(¬P(c4) ∧ ∀x ∀y ¬Q(x, y))`` comes out as
    ``P(c4) ∨ ∃x ∃y Q(x, y)`` -- what would have had to be true for the
    conclusion to follow.
    """

    return to_nnf(
        Not(
            formula
        )
    )
