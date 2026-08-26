"""Clause bookkeeping: variable renaming, canonical keys, tautologies.

Two layers of variable names are in play.  ``standardize_clause`` renames
variables apart to ``__v<N>_<orig>`` before every resolution attempt;
``clean_clause_variables`` renames the survivors back to x, y, z, ... for
storage.  The ugly internal names are never displayed, because
``Term.__str__`` runs them through ``visible_variable_name``.

Never compare clauses by their printed form -- use ``canonical_clause``,
which is invariant under variable renaming.
"""

import itertools

from .formulas import (
    Atom,
    Literal,
    Term,
    is_equality,
    visible_variable_name,
)


_fresh_counter = itertools.count()


def standardize_clause(
    clause
):

    """Rename every variable apart, behind a fresh ``__v<N>_`` prefix.

    Two clauses being resolved must not share variable names, or unification would
    tie together variables that merely happen to be spelled alike.  These names
    never reach the output -- ``Term.__str__`` strips the prefix back off.
    """

    prefix = (
        f"__v"
        f"{next(_fresh_counter)}_"
    )

    mapping = {}

    def rename_term(term):

        """Map each variable to its prefixed twin, recursing into arguments."""

        if term.is_var:

            if term.name not in mapping:

                original_name = (
                    visible_variable_name(
                        term.name
                    )
                )

                mapping[
                    term.name
                ] = Term(
                    prefix
                    + original_name,
                    (),
                    True
                )

            return mapping[
                term.name
            ]

        return Term(
            term.name,
            tuple(
                rename_term(
                    arg
                )
                for arg
                in term.args
            ),
            False
        )

    result = []

    for literal in clause:

        result.append(
            Literal(
                Atom(
                    literal.atom.pred,
                    tuple(
                        rename_term(
                            arg
                        )
                        for arg
                        in literal.atom.args
                    )
                ),
                literal.negated
            )
        )

    return result


def clean_clause_variables(
    clause
):

    """
    Convert surviving internal variables to clean names:

        x, y, z, u, v, w, x7, ...

    This is for storing the new clause in the visible KB.
    """

    mapping = {}

    preferred = [
        "x",
        "y",
        "z",
        "u",
        "v",
        "w"
    ]

    counter = 0

    def clean_term(term):

        """Pick a display name: the original if free, else x, y, z, u, v, w, x7, ..."""

        nonlocal counter

        if term.is_var:

            if term.name not in mapping:

                original = (
                    visible_variable_name(
                        term.name
                    )
                )

                # Prefer original name if available and unused.
                used_names = {
                    t.name
                    for t
                    in mapping.values()
                }

                if (
                    original not in used_names
                    and
                    not original.startswith("__")
                ):

                    new_name = original

                elif counter < len(
                    preferred
                ):

                    while (
                        counter
                        <
                        len(preferred)
                        and
                        preferred[counter]
                        in used_names
                    ):
                        counter += 1

                    if counter < len(
                        preferred
                    ):

                        new_name = (
                            preferred[
                                counter
                            ]
                        )

                        counter += 1

                    else:

                        new_name = (
                            f"x{counter + 1}"
                        )

                        counter += 1

                else:

                    new_name = (
                        f"x{counter + 1}"
                    )

                    counter += 1

                mapping[
                    term.name
                ] = Term(
                    new_name,
                    (),
                    True
                )

            return mapping[
                term.name
            ]

        return Term(
            term.name,
            tuple(
                clean_term(
                    arg
                )
                for arg
                in term.args
            ),
            False
        )

    result = []

    for literal in clause:

        result.append(
            Literal(
                Atom(
                    literal.atom.pred,
                    tuple(
                        clean_term(
                            arg
                        )
                        for arg
                        in literal.atom.args
                    )
                ),
                literal.negated
            )
        )

    return result


def canonical_clause(
    clause
):

    """
    Alpha-equivalent clauses should count as the same clause.

    Example:
        P(x) ∨ Q(y)
        P(u) ∨ Q(v)

    are treated as identical.
    """

    mapping = {}
    counter = 0

    def canonical_term(term):

        """Render a term with variables numbered by first appearance."""

        nonlocal counter

        if term.is_var:

            if term.name not in mapping:

                counter += 1

                mapping[
                    term.name
                ] = (
                    f"V{counter}"
                )

            return mapping[
                term.name
            ]

        if term.args:

            return (
                term.name
                + "("
                + ",".join(
                    canonical_term(
                        arg
                    )
                    for arg
                    in term.args
                )
                + ")"
            )

        return term.name

    ordered_literals = sorted(
        clause,
        key=lambda literal: (
            literal.negated,
            literal.atom.pred,
            str(literal)
        )
    )

    result = []

    for literal in ordered_literals:

        sign = (
            "~"
            if literal.negated
            else "+"
        )

        result.append(
            sign
            + literal.atom.pred
            + "("
            + ",".join(
                canonical_term(
                    arg
                )
                for arg
                in literal.atom.args
            )
            + ")"
        )

    return tuple(
        sorted(result)
    )


def is_trivial_equality(
    literal
):

    """Is this literal ``t = t`` or ``t ≠ t`` -- true or false on sight?

    Both are worth spotting.  ``c = c`` says nothing (it is an instance of
    reflexivity), so a clause holding it is true whatever else it says.  ``c ≠
    c`` says something false, so it can never help a clause be true and is
    simply dropped -- and a clause of nothing but ``c ≠ c`` is the empty clause.
    """

    return (
        is_equality(
            literal.atom
        )
        and
        literal.atom.args[0]
        ==
        literal.atom.args[1]
    )


def drop_false_equalities(
    clause
):

    """Remove every ``t ≠ t`` from a clause, since each of them is false.

    A disjunction is not helped by a disjunct that cannot hold, so this loses
    nothing -- and when it empties the clause, what is left is □.
    """

    return [
        literal
        for literal
        in clause
        if not (
            literal.negated
            and
            is_trivial_equality(
                literal
            )
        )
    ]


def clause_is_tautology(
    clause
):

    """Is the clause trivially true?

    Two ways it can be: it holds a literal and its negation, or it holds an
    equality of something with itself.
    """

    for literal in clause:

        if (
            not literal.negated
            and
            is_trivial_equality(
                literal
            )
        ):

            return True

    for i, first in enumerate(
        clause
    ):

        for j, second in enumerate(
            clause
        ):

            if i == j:
                continue

            if (
                first.negated
                !=
                second.negated
                and
                first.atom
                ==
                second.atom
            ):

                return True

    return False
