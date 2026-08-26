"""Step 5: drop the ∀ prefixes.

After skolemization every remaining variable is universally quantified,
so the quantifiers carry no information and the bare body will do.
"""

from ..formulas import (
    And,
    ForAll,
    Or,
)
from ..rewrite import (
    DROP_FORALL,
    record,
)


def remove_forall(
    f,
    rewrites=None
):

    """Step 5: drop the ∀ prefixes, keeping the bare body.

    Appends one :class:`Rewrite` per quantifier dropped, if given a list.
    """

    if isinstance(
        f,
        ForAll
    ):

        record(
            rewrites,
            DROP_FORALL,
            f,
            f.body
        )

        return remove_forall(
            f.body,
            rewrites
        )

    if isinstance(
        f,
        And
    ):

        return And(
            remove_forall(
                f.a,
                rewrites
            ),
            remove_forall(
                f.b,
                rewrites
            )
        )

    if isinstance(
        f,
        Or
    ):

        return Or(
            remove_forall(
                f.a,
                rewrites
            ),
            remove_forall(
                f.b,
                rewrites
            )
        )

    return f
