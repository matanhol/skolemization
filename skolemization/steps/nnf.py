"""Step 3: negation normal form -- push every ¬ inward to the atoms.

¬∀x becomes ∃x¬, ¬∃x becomes ∀x¬, and De Morgan does the rest, so the
only negations left sit directly on atoms.
"""

from ..formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Not,
    Or,
)
from ..rewrite import (
    DE_MORGAN_AND,
    DE_MORGAN_OR,
    DOUBLE_NEGATION,
    NOT_EXISTS,
    NOT_FORALL,
    record,
)


def to_nnf(
    f,
    negated=False,
    rewrites=None
):

    """Step 3: push every negation inward until it sits on an atom.

    De Morgan handles ``∧`` and ``∨``, ``¬∀x`` becomes ``∃x¬``, ``¬∃x`` becomes
    ``∀x¬``, and double negations cancel.

    The negation is carried down in ``negated`` rather than by rewriting ``Not``
    nodes, so a rule is recorded at the moment the flag is *consumed* -- when a
    negated ``And`` turns into an ``Or``, that is the De Morgan step, and it is
    recorded with the children exactly as they stood.
    """

    if isinstance(
        f,
        Atom
    ):

        if negated:
            return Not(f)

        return f

    if isinstance(
        f,
        Not
    ):

        if negated:

            record(
                rewrites,
                DOUBLE_NEGATION,
                Not(f),
                f.x
            )

        return to_nnf(
            f.x,
            not negated,
            rewrites
        )

    if isinstance(
        f,
        And
    ):

        if negated:

            record(
                rewrites,
                DE_MORGAN_AND,
                Not(f),
                Or(
                    Not(f.a),
                    Not(f.b)
                )
            )

            return Or(
                to_nnf(
                    f.a,
                    True,
                    rewrites
                ),
                to_nnf(
                    f.b,
                    True,
                    rewrites
                )
            )

        return And(
            to_nnf(
                f.a,
                False,
                rewrites
            ),
            to_nnf(
                f.b,
                False,
                rewrites
            )
        )

    if isinstance(
        f,
        Or
    ):

        if negated:

            record(
                rewrites,
                DE_MORGAN_OR,
                Not(f),
                And(
                    Not(f.a),
                    Not(f.b)
                )
            )

            return And(
                to_nnf(
                    f.a,
                    True,
                    rewrites
                ),
                to_nnf(
                    f.b,
                    True,
                    rewrites
                )
            )

        return Or(
            to_nnf(
                f.a,
                False,
                rewrites
            ),
            to_nnf(
                f.b,
                False,
                rewrites
            )
        )

    if isinstance(
        f,
        ForAll
    ):

        if negated:

            record(
                rewrites,
                NOT_FORALL,
                Not(f),
                Exists(
                    f.var,
                    Not(f.body)
                )
            )

            return Exists(
                f.var,
                to_nnf(
                    f.body,
                    True,
                    rewrites
                )
            )

        return ForAll(
            f.var,
            to_nnf(
                f.body,
                False,
                rewrites
            )
        )

    if isinstance(
        f,
        Exists
    ):

        if negated:

            record(
                rewrites,
                NOT_EXISTS,
                Not(f),
                ForAll(
                    f.var,
                    Not(f.body)
                )
            )

            return ForAll(
                f.var,
                to_nnf(
                    f.body,
                    True,
                    rewrites
                )
            )

        return Exists(
            f.var,
            to_nnf(
                f.body,
                False,
                rewrites
            )
        )

    raise TypeError(f)
