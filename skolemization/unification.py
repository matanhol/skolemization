"""Unification of terms and atoms, with the occurs check."""

from .formulas import (
    Atom,
    Literal,
    Term,
)
from .substitution import substitute_term


def occurs(
    variable,
    term,
    substitution
):

    """Does ``variable`` appear in ``term`` once the substitution is applied?

    The occurs check: it is what stops ``x`` unifying with ``f(x)`` and building
    an infinite term.
    """

    term = (
        substitute_term(
            term,
            substitution
        )
    )

    if term.is_var:

        return (
            term.name
            ==
            variable
        )

    return any(
        occurs(
            variable,
            arg,
            substitution
        )
        for arg
        in term.args
    )


def unify_variable(
    variable,
    term,
    substitution
):

    """Bind ``variable`` to ``term``, following bindings already made.

    Returns the extended substitution, or None if the occurs check fails.
    """

    if variable in substitution:

        return unify_terms(
            substitution[
                variable
            ],
            term,
            substitution
        )

    if (
        term.is_var
        and
        term.name in substitution
    ):

        return unify_terms(
            Term(
                variable,
                (),
                True
            ),
            substitution[
                term.name
            ],
            substitution
        )

    if (
        term.is_var
        and
        term.name == variable
    ):

        return substitution

    if occurs(
        variable,
        term,
        substitution
    ):

        return None

    result = dict(
        substitution
    )

    result[
        variable
    ] = term

    return result


def unify_terms(
    a,
    b,
    substitution=None
):

    """Unify two terms, returning a substitution making them equal, or None.

    ``substitution`` accumulates across the recursive calls; omit it to start.
    """

    if substitution is None:
        substitution = {}

    a = substitute_term(
        a,
        substitution
    )

    b = substitute_term(
        b,
        substitution
    )

    if a == b:
        return substitution

    if a.is_var:

        return unify_variable(
            a.name,
            b,
            substitution
        )

    if b.is_var:

        return unify_variable(
            b.name,
            a,
            substitution
        )

    if (
        a.name != b.name
        or
        len(a.args)
        !=
        len(b.args)
    ):

        return None

    for x, y in zip(
        a.args,
        b.args
    ):

        substitution = (
            unify_terms(
                x,
                y,
                substitution
            )
        )

        if substitution is None:
            return None

    return substitution


def unify_atoms(
    a,
    b
):

    """Unify two atoms argument-wise, or None if predicate or arity differ.

    This is what decides whether two literals can be resolved against each other.
    """

    if (
        a.pred != b.pred
        or
        len(a.args)
        !=
        len(b.args)
    ):

        return None

    substitution = {}

    for x, y in zip(
        a.args,
        b.args
    ):

        substitution = (
            unify_terms(
                x,
                y,
                substitution
            )
        )

        if substitution is None:
            return None

    return substitution


def apply_substitution_literal(
    literal,
    substitution
):

    """Rebuild a literal with the substitution applied, keeping its sign."""

    return Literal(
        Atom(
            literal.atom.pred,
            tuple(
                substitute_term(
                    arg,
                    substitution
                )
                for arg
                in literal.atom.args
            )
        ),
        literal.negated
    )
