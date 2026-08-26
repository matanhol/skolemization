"""Step 7: read the clauses off the CNF.

Each conjunct becomes one clause -- a flat list of literals -- which is
the form the resolution search works in.
"""

from ..display import formula_str
from ..formulas import (
    And,
    Atom,
    Literal,
    Not,
    Or,
)


def flatten_or(f):

    """Collect one CNF conjunct into a flat list of literals.

    Raises ValueError if the formula is not a disjunction of possibly-negated
    atoms, which would mean an earlier step left work undone.
    """

    if isinstance(
        f,
        Or
    ):

        return (
            flatten_or(
                f.a
            )
            +
            flatten_or(
                f.b
            )
        )

    if isinstance(
        f,
        Atom
    ):

        return [
            Literal(
                f,
                False
            )
        ]

    if (
        isinstance(
            f,
            Not
        )
        and
        isinstance(
            f.x,
            Atom
        )
    ):

        return [
            Literal(
                f.x,
                True
            )
        ]

    raise ValueError(
        "Expected clause, got: "
        + formula_str(f)
    )


def extract_clauses(f):

    """Step 7: split the CNF at its ∧s, reading each conjunct off as a clause."""

    if isinstance(
        f,
        And
    ):

        return (
            extract_clauses(
                f.a
            )
            +
            extract_clauses(
                f.b
            )
        )

    return [
        flatten_or(
            f
        )
    ]
