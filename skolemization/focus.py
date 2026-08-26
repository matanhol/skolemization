"""Heuristic: try the search with every variable pinned to the witness.

Sound but incomplete, and the distinction matters.  Replacing a universally
quantified variable by a ground term is just universal instantiation, so every
focused clause is entailed by the clause it came from -- a proof found here is
a real proof.  What is lost is generality: the focused KB *replaces* the
original rather than extending it, so a proof needing some other instance
becomes unreachable.  That is why a negative result here means nothing, and why
prover.py falls back to the untouched KB.

Two things are deliberately left out of the guess:

* **The relation axioms** keep their variables -- see ``focus_kb_on_witness``.
* **Problems with more than one witness** do not get a focused pass at all.
  With ``c`` and ``c2`` both naming "something that exists", ``x := c`` is a
  coin toss rather than a strategy, so prover.py does not run this at all.

The witness is whatever name skolemization settled on, usually ``c`` but not
when the problem itself uses that name -- see steps/skolemize.py.
"""

from . import narration
from .formulas import Term
from .unification import apply_substitution_literal


# The variable the focus pass pins.  Clause variables are renamed to x, y, z,
# ... for storage, so there is usually an x -- but a formula written with other
# names keeps them, and then this heuristic finds nothing to substitute and the
# whole pass is a duplicate of the general search.
FOCUSED_VARIABLE = "x"


def term_contains_witness(
    term,
    witness
):

    """Does this term mention the witness constant, at any depth?"""

    if (
        not term.is_var
        and
        term.name == witness
        and
        not term.args
    ):

        return True

    return any(
        term_contains_witness(
            arg,
            witness
        )
        for arg
        in term.args
    )


def kb_contains_witness(
    kb,
    witness
):

    """Did skolemization put a witness anywhere in the KB?"""

    for clause in kb:

        for literal in clause:

            for arg in literal.atom.args:

                if term_contains_witness(
                    arg,
                    witness
                ):

                    return True

    return False


def instantiate_variable_with_witness(
    clause,
    witness,
    variable_name=FOCUSED_VARIABLE
):

    """Substitute the witness for one variable throughout a clause."""

    substitution = {
        variable_name:
        Term(
            witness,
            (),
            False
        )
    }

    return [
        apply_substitution_literal(
            literal,
            substitution
        )
        for literal
        in clause
    ]


def focus_kb_on_witness(
    kb,
    witness,
    protected=frozenset()
):

    """Return the KB with the focused variable replaced by the witness.

    ``protected`` holds the positions of clauses that must stay general -- the
    relation axioms.  Pinning those to the witness defeats the reason they were
    added: ``¬Eq(x,y) ∨ Eq(y,x)`` says the relation is symmetric, while
    ``¬Eq(c,y) ∨ Eq(y,c)`` says only that it is symmetric about ``c``, which is
    not what was declared and not enough to close the proofs the axiom exists
    for.  Leaving them alone also keeps the pass sound, since instantiating
    fewer clauses cannot entail more.

    Only the variable named by ``FOCUSED_VARIABLE`` is substituted, so if the
    source formulas used other names this returns the KB unchanged and the
    whole focused pass is a wasted duplicate of the general one.
    """

    narration.focus_header(
        witness,
        FOCUSED_VARIABLE
    )

    if protected:

        narration.focus_keeps_axioms()

    result = []

    for i, clause in enumerate(
        kb,
        1
    ):

        if i - 1 in protected:

            narration.focus_clause_kept(
                i,
                clause
            )

            result.append(
                list(
                    clause
                )
            )

            continue

        new_clause = (
            instantiate_variable_with_witness(
                clause,
                witness
            )
        )

        narration.focus_clause(
            i,
            clause,
            new_clause
        )

        result.append(
            new_clause
        )

    narration.focused_kb(
        result,
        witness
    )

    return result
