"""Step 6: conjunctive normal form.

P ∨ (Q ∧ R) becomes (P ∨ Q) ∧ (P ∨ R), repeatedly, until the formula is
a conjunction of disjunctions.
"""

from ..formulas import (
    And,
    Or,
)
from ..rewrite import (
    DISTRIBUTE,
    record,
)


def distribute_or(
    a,
    b,
    rewrites=None
):

    """Push one ∨ under the ∧s below it.

    ``P ∨ (Q ∧ R)`` becomes ``(P ∨ Q) ∧ (P ∨ R)``, and the mirror case when the
    conjunction is on the left.  Appends one :class:`Rewrite` per distribution,
    if given a list.
    """

    if isinstance(
        a,
        And
    ):

        record(
            rewrites,
            DISTRIBUTE,
            Or(a, b),
            And(
                Or(a.a, b),
                Or(a.b, b)
            )
        )

        return And(
            distribute_or(
                a.a,
                b,
                rewrites
            ),
            distribute_or(
                a.b,
                b,
                rewrites
            )
        )

    if isinstance(
        b,
        And
    ):

        record(
            rewrites,
            DISTRIBUTE,
            Or(a, b),
            And(
                Or(a, b.a),
                Or(a, b.b)
            )
        )

        return And(
            distribute_or(
                a,
                b.a,
                rewrites
            ),
            distribute_or(
                a,
                b.b,
                rewrites
            )
        )

    return Or(
        a,
        b
    )


def to_cnf(
    f,
    rewrites=None
):

    """Step 6: rewrite an NNF formula as a conjunction of disjunctions."""

    if isinstance(
        f,
        And
    ):

        return And(
            to_cnf(
                f.a,
                rewrites
            ),
            to_cnf(
                f.b,
                rewrites
            )
        )

    if isinstance(
        f,
        Or
    ):

        return distribute_or(
            to_cnf(
                f.a,
                rewrites
            ),
            to_cnf(
                f.b,
                rewrites
            ),
            rewrites
        )

    return f
