"""Step 2: P → Q becomes ¬P ∨ Q."""

from ..rewrite import (
    IMPLICATION,
    record,
)
from ..formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
)


def remove_implications(
    f,
    rewrites=None
):

    """Step 2: rewrite ``a -> b`` as ``¬a ∨ b``, throughout the formula.

    Appends one :class:`Rewrite` per implication removed, if given a list.
    """

    if isinstance(
        f,
        Atom
    ):
        return f

    if isinstance(
        f,
        Not
    ):

        return Not(
            remove_implications(
                f.x,
                rewrites
            )
        )

    if isinstance(
        f,
        And
    ):

        return And(
            remove_implications(
                f.a,
                rewrites
            ),
            remove_implications(
                f.b,
                rewrites
            )
        )

    if isinstance(
        f,
        Or
    ):

        return Or(
            remove_implications(
                f.a,
                rewrites
            ),
            remove_implications(
                f.b,
                rewrites
            )
        )

    if isinstance(
        f,
        Implies
    ):

        record(
            rewrites,
            IMPLICATION,
            f,
            Or(
                Not(f.a),
                f.b
            )
        )

        return Or(
            Not(
                remove_implications(
                    f.a,
                    rewrites
                )
            ),
            remove_implications(
                f.b,
                rewrites
            )
        )

    if isinstance(
        f,
        ForAll
    ):

        return ForAll(
            f.var,
            remove_implications(
                f.body,
                rewrites
            )
        )

    if isinstance(
        f,
        Exists
    ):

        return Exists(
            f.var,
            remove_implications(
                f.body,
                rewrites
            )
        )

    raise TypeError(f)
