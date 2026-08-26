"""A single resolution step between two clauses."""

from .clauses import (
    clause_is_tautology,
    clean_clause_variables,
    standardize_clause,
)
from .formulas import visible_variable_name
from .substitution import substitute_term
from .unification import (
    apply_substitution_literal,
    unify_atoms,
)


def resolve_two_clauses(
    clause1,
    clause2,
    keep_tautologies=False
):

    """Every resolvent obtainable from one pair of clauses.

    The pair is standardized apart first so their variables cannot collide.  Each
    result is (literal from the left, literal from the right, the unifier, the
    resolvent); tautological resolvents are dropped rather than returned.

    ``keep_tautologies`` returns them anyway, which only the saturation account
    wants: it has to say *why* a pair yields nothing, and "the resolvent is a
    tautology" is a different reason from "nothing unifies".
    """

    left = (
        standardize_clause(
            clause1
        )
    )

    right = (
        standardize_clause(
            clause2
        )
    )

    possibilities = []

    for i, lit1 in enumerate(
        left
    ):

        for j, lit2 in enumerate(
            right
        ):

            if (
                lit1.negated
                ==
                lit2.negated
            ):

                continue

            substitution = (
                unify_atoms(
                    lit1.atom,
                    lit2.atom
                )
            )

            if substitution is None:
                continue

            resolvent = []

            for k, literal in enumerate(
                left
            ):

                if k != i:

                    resolvent.append(
                        apply_substitution_literal(
                            literal,
                            substitution
                        )
                    )

            for k, literal in enumerate(
                right
            ):

                if k != j:

                    resolvent.append(
                        apply_substitution_literal(
                            literal,
                            substitution
                        )
                    )

            unique = []

            for literal in resolvent:

                if literal not in unique:

                    unique.append(
                        literal
                    )

            if (
                clause_is_tautology(
                    unique
                )
                and
                not keep_tautologies
            ):

                continue

            clean_resolvent = (
                clean_clause_variables(
                    unique
                )
            )

            possibilities.append(
                (
                    lit1,
                    lit2,
                    substitution,
                    clean_resolvent
                )
            )

    return possibilities


def meaningful_substitutions(
    substitution
):

    """
    Internal:
        __v230_x := g1(__v231_y)

    Visible:
        x := g1(y)

    Pure variable-to-variable bookkeeping is not printed.
    """

    result = []
    seen = set()

    for variable, value in substitution.items():

        final_value = (
            substitute_term(
                value,
                substitution
            )
        )

        # Don't show internal variable -> variable mappings.
        if final_value.is_var:
            continue

        shown_variable = (
            visible_variable_name(
                variable
            )
        )

        shown_value = str(
            final_value
        )

        key = (
            shown_variable,
            shown_value
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            (
                shown_variable,
                shown_value
            )
        )

    return result
