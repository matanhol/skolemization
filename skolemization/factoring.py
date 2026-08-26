"""The factoring rule: merging two literals inside one clause.

Resolution works across two clauses and needs opposite signs.  Factoring works
within one clause and needs the *same* sign: unify two literals, and once they
are identical they collapse into one.

    P(x) ∨ P(y)     --  {y := x}  -->     P(x)

The lengths are the whole point.  A resolution step yields
``|C1| + |C2| - 2`` literals, so two 2-literal parents keep producing 2-literal
resolvents forever and nothing ever approaches the empty clause.  Factoring is
the only rule here that shortens a clause on its own::

    P(x) ∨ P(y)     factors to    P(x)
    ¬P(x) ∨ ¬P(y)   factors to    ¬P(x)
    P(x), ¬P(x)     resolve to    □          1 + 1 - 2 = 0

Which is why binary resolution *plus* factoring is refutation-complete while
binary resolution alone is not.  Without this module the prover reports
SATURATED_NO_CONTRADICTION on knowledge bases that are plainly unsatisfiable.
"""

from .clauses import (
    clause_is_tautology,
    clean_clause_variables,
    standardize_clause,
)
from .unification import (
    apply_substitution_literal,
    unify_atoms,
)


def factor_clause(
    clause
):

    """Every factor obtainable from one clause.

    Each result is (first literal, second literal, the unifier, the factor),
    the same shape ``resolve_two_clauses`` returns, so the search can treat
    both rules alike.  Tautological factors are dropped rather than returned.
    """

    literals = (
        standardize_clause(
            clause
        )
    )

    factors = []

    for i, first in enumerate(
        literals
    ):

        for j, second in enumerate(
            literals
        ):

            if j <= i:
                continue

            # Same sign -- that is what separates factoring from resolution.
            if (
                first.negated
                !=
                second.negated
            ):

                continue

            substitution = (
                unify_atoms(
                    first.atom,
                    second.atom
                )
            )

            if substitution is None:
                continue

            merged = _merge(
                literals,
                substitution
            )

            if clause_is_tautology(
                merged
            ):

                continue

            factors.append(
                (
                    first,
                    second,
                    substitution,
                    clean_clause_variables(
                        merged
                    )
                )
            )

    return factors


def _merge(
    literals,
    substitution
):

    """Apply the unifier to every literal, keeping one copy of each.

    The two literals that were unified come out identical, so dropping
    duplicates is what actually performs the merge -- and it shortens the
    clause by at least one literal every time.
    """

    merged = []

    for literal in literals:

        instantiated = (
            apply_substitution_literal(
                literal,
                substitution
            )
        )

        if instantiated not in merged:

            merged.append(
                instantiated
            )

    return merged
