"""Substituting equals for equals, as an inference rule.

Equality is not built into resolution, so a prover has to get it from
somewhere.  The usual course answer is to write the equality axioms -- and
there are more of them than people expect: reflexivity, symmetry, transitivity,
*and* a congruence axiom for every predicate and every function::

    (x = y ∧ P(x)) → P(y)          for every predicate
    x = y → f(x) = f(y)            for every function

Miss the congruence family and the prover is not reasoning about equality at
all, only about some equivalence relation: ``P(c)`` and ``c = y`` will not give
you ``P(y)``.

Paramodulation replaces all of that with one rule::

    C1:  s = t  ∨  rest1
    C2:  ... u ...              u any non-variable subterm, σ = mgu(s, u)
    ----------------------------------------------------------------
         (C2 with that u replaced by t  ∨  rest1) σ

Because it rewrites *inside terms*, below the predicates, it covers every
symbol at once -- including the Skolem functions invented in step 4, which no
axiom generator could have known about.  Resolution, factoring, this rule and
the single axiom ``x = x`` are refutation-complete for first-order logic with
equality.

The price is how prolific it is: every equation, in both directions, against
every subterm position.  ``config.EQUALITY_RULE = "superposition"`` fences it
in with the term ordering (ordering.py) so equations are only used downhill,
which is the restriction real provers are built on.
"""

from dataclasses import dataclass

from . import config
from .clauses import (
    clause_is_tautology,
    clean_clause_variables,
    standardize_clause,
)
from .formulas import (
    Atom,
    Literal,
    Term,
    is_equality,
)
from .ordering import greater
from .unification import (
    apply_substitution_literal,
    unify_terms,
)


@dataclass(frozen=True)
class Replacement:

    """What one rewriting actually did, for the narration to report.

    The rule knows all of this while it works and would otherwise throw it
    away, leaving a reader to reconstruct the step from its result: an equation
    ``s = t`` can be used either way round, the literal is printed whole so
    nothing points at the occurrence that matched, and a binding gives no hint
    which of the two clauses its variable came from.

    ``source`` and ``target`` are the two sides of the equation *in the
    direction used here*; ``subterm`` is the occurrence inside the rewritten
    literal that ``source`` unified with; ``before`` and ``after`` are that
    literal on both sides of the swap, with the unifier applied.
    """

    source: object
    target: object
    subterm: object
    before: object
    after: object


def subterm_positions(
    term,
    path=()
):

    """Every subterm of a term, with the path that reaches it.

    A path is the sequence of argument indices to follow, so ``()`` is the term
    itself and ``(0, 1)`` is the second argument of its first argument.
    """

    yield (
        path,
        term
    )

    for index, argument in enumerate(
        term.args
    ):

        yield from subterm_positions(
            argument,
            path + (index,)
        )


def replace_at(
    term,
    path,
    replacement
):

    """Rebuild ``term`` with ``replacement`` at ``path``."""

    if not path:
        return replacement

    arguments = list(
        term.args
    )

    arguments[path[0]] = (
        replace_at(
            arguments[path[0]],
            path[1:],
            replacement
        )
    )

    return Term(
        term.name,
        tuple(arguments),
        term.is_var
    )


def equations(clause):

    """The positive equalities of a clause, each in both directions.

    Yields (index of the literal, left, right).  Under
    ``EQUALITY_RULE = "superposition"`` a direction that would rewrite a term
    into a bigger one is dropped -- that is the whole of the restriction.

    A direction whose *source* is a variable is refused in either rule, because
    it cannot do any work.  ``c = y`` used as ``y ⟶ c`` matches the first
    subterm it meets, binds ``y`` to it, and puts the equation's other side back
    -- under that same binding the equation becomes ``c = c``, so what comes out
    is the clause that was rewritten plus the leftovers, weaker than a clause
    already in the KB.  The standard calculus excludes it as well (a variable is
    never the maximal side of an equation), and the ordering below cannot: it
    leaves ``c`` and ``y`` incomparable, so ``greater`` says False both ways and
    lets the direction through.
    """

    ordered = (
        config.EQUALITY_RULE
        ==
        "superposition"
    )

    for index, literal in enumerate(
        clause
    ):

        if literal.negated:
            continue

        if not is_equality(
            literal.atom
        ):

            continue

        left, right = literal.atom.args

        for source, target in (
            (left, right),
            (right, left)
        ):

            if source.is_var:
                continue

            if ordered and greater(
                target,
                source
            ):

                continue

            yield (
                index,
                source,
                target
            )


def paramodulants(
    from_clause,
    into_clause
):

    """Every clause obtainable by rewriting inside ``into_clause``.

    Each result is (the equality literal used, the literal rewritten, the
    unifier, the resulting clause) -- the same shape ``resolve_two_clauses``
    and ``factor_clause`` return, so the search treats all three rules alike --
    plus a fifth element, the :class:`Replacement` describing what was swapped
    for what and where.

    Variables are never rewritten into: a variable stands for every term
    already, so paramodulating into one adds nothing but noise, and leaving
    them alone costs no completeness.
    """

    left = standardize_clause(
        from_clause
    )

    right = standardize_clause(
        into_clause
    )

    results = []

    for index, source, target in equations(
        left
    ):

        for position, literal in enumerate(
            right
        ):

            for argument, path, subterm in _rewritable(
                literal
            ):

                substitution = (
                    unify_terms(
                        source,
                        subterm
                    )
                )

                if substitution is None:
                    continue

                rewritten = (
                    _rewrite_literal(
                        literal,
                        argument,
                        path,
                        target
                    )
                )

                clause = (
                    _assemble(
                        left,
                        index,
                        right,
                        position,
                        rewritten,
                        substitution
                    )
                )

                if clause is None:
                    continue

                results.append(
                    (
                        left[index],
                        literal,
                        substitution,
                        clause,
                        Replacement(
                            source,
                            target,
                            subterm,
                            apply_substitution_literal(
                                literal,
                                substitution
                            ),
                            apply_substitution_literal(
                                rewritten,
                                substitution
                            )
                        )
                    )
                )

    return results


def _rewritable(literal):

    """Every non-variable subterm of a literal: (argument index, path, term)."""

    for argument, term in enumerate(
        literal.atom.args
    ):

        for path, subterm in subterm_positions(
            term
        ):

            if subterm.is_var:
                continue

            yield (
                argument,
                path,
                subterm
            )


def _rewrite_literal(
    literal,
    argument,
    path,
    replacement
):

    """The literal with one subterm swapped for the equation's other side."""

    arguments = list(
        literal.atom.args
    )

    arguments[argument] = (
        replace_at(
            arguments[argument],
            path,
            replacement
        )
    )

    return Literal(
        Atom(
            literal.atom.pred,
            tuple(arguments)
        ),
        literal.negated
    )


def _assemble(
    left,
    index,
    right,
    position,
    rewritten,
    substitution
):

    """The finished clause: what is left of both parents, under the unifier.

    Returns None when the result is a tautology, which is no use to anyone.
    """

    clause = []

    for other, literal in enumerate(
        right
    ):

        clause.append(
            apply_substitution_literal(
                rewritten
                if other == position
                else literal,
                substitution
            )
        )

    for other, literal in enumerate(
        left
    ):

        if other == index:
            continue

        clause.append(
            apply_substitution_literal(
                literal,
                substitution
            )
        )

    unique = []

    for literal in clause:

        if literal not in unique:

            unique.append(
                literal
            )

    if clause_is_tautology(
        unique
    ):

        return None

    return clean_clause_variables(
        unique
    )
