"""Applying a substitution to a term or to a whole formula."""

from .formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
    Term,
)


def substitute_term(
    term,
    substitution
):

    """Replace variables in a term according to ``substitution``.

    Names absent from the substitution, and function symbols, are left alone.
    """

    if (
        term.is_var
        and
        term.name in substitution
    ):

        return substitute_term(
            substitution[
                term.name
            ],
            substitution
        )

    if term.args:

        return Term(
            term.name,
            tuple(
                substitute_term(
                    arg,
                    substitution
                )
                for arg
                in term.args
            ),
            False
        )

    return term


def substitute_formula(
    f,
    substitution
):

    """Apply a substitution throughout a formula.

    A quantifier drops its own variable from the substitution before descending,
    so a binding never reaches into the scope that rebinds it.
    """

    if isinstance(
        f,
        Atom
    ):

        return Atom(
            f.pred,
            tuple(
                substitute_term(
                    arg,
                    substitution
                )
                for arg
                in f.args
            )
        )

    if isinstance(
        f,
        Not
    ):

        return Not(
            substitute_formula(
                f.x,
                substitution
            )
        )

    if isinstance(
        f,
        And
    ):

        return And(
            substitute_formula(
                f.a,
                substitution
            ),
            substitute_formula(
                f.b,
                substitution
            )
        )

    if isinstance(
        f,
        Or
    ):

        return Or(
            substitute_formula(
                f.a,
                substitution
            ),
            substitute_formula(
                f.b,
                substitution
            )
        )

    if isinstance(
        f,
        Implies
    ):

        return Implies(
            substitute_formula(
                f.a,
                substitution
            ),
            substitute_formula(
                f.b,
                substitution
            )
        )

    if isinstance(
        f,
        ForAll
    ):

        smaller_sub = {
            k: v
            for k, v
            in substitution.items()
            if k != f.var
        }

        return ForAll(
            f.var,
            substitute_formula(
                f.body,
                smaller_sub
            )
        )

    if isinstance(
        f,
        Exists
    ):

        smaller_sub = {
            k: v
            for k, v
            in substitution.items()
            if k != f.var
        }

        return Exists(
            f.var,
            substitute_formula(
                f.body,
                smaller_sub
            )
        )

    raise TypeError(f)
