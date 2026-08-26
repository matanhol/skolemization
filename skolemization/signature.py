"""Checking that every symbol is used consistently.

The input language has no declarations, so nothing forces ``P`` to mean the
same thing in two formulas.  Write ``P(x,y)`` once and ``P(x)`` elsewhere and
the two atoms simply never unify -- ``unify_atoms`` compares arity, finds a
mismatch, and returns None.  No error is raised anywhere; the search just
quietly cannot connect them, saturates, and reports
SATURATED_NO_CONTRADICTION, which reads as "your conclusion does not follow".

So the typo becomes a confident wrong answer.  This module walks the parsed
formulas first and refuses to continue when a name is used two ways.
"""

from dataclasses import dataclass

from .formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
)


PREDICATE = "predicate"
FUNCTION = "function"
VARIABLE = "variable"
CONSTANT = "constant"


class SignatureError(Exception):
    """A symbol is used in two incompatible ways."""


@dataclass(frozen=True)
class Use:

    """One way a name was used, and where it was written."""

    kind: str
    arity: int
    source: str

    def describe(self):
        """Phrase this use the way the error message wants it."""

        if self.kind in (VARIABLE, CONSTANT):
            return f"a {self.kind}"

        return (
            f"a {self.kind} of "
            f"{self.arity} argument"
            + ("" if self.arity == 1 else "s")
        )


@dataclass(frozen=True)
class Signature:

    """Every name in the problem, and how each one is used."""

    uses: dict

    @property
    def names(self):
        """Every name that appears, whatever its role.

        This is what the Skolem namer must avoid, so that an invented witness
        can never capture a symbol the user wrote themselves.
        """

        return set(self.uses)


def signature_of(
    formulas,
    sources
):

    """Collect the signature of ``formulas``, or raise on a conflict.

    ``sources`` is the matching source text of each formula, used only to make
    the error message point at something the reader recognises.
    """

    uses = {}

    for formula, source in zip(
        formulas,
        sources
    ):

        _walk_formula(
            formula,
            source,
            uses
        )

    return Signature(
        uses
    )


def _record(
    uses,
    name,
    use
):

    """Note one use of ``name``, refusing it if it contradicts an earlier one."""

    previous = uses.get(
        name
    )

    if previous is None:

        uses[name] = use

        return

    if (
        previous.kind == use.kind
        and
        previous.arity == use.arity
    ):

        return

    raise SignatureError(
        f"'{name}' is used in two different ways.\n"
        f"    as {previous.describe()}, in: {previous.source}\n"
        f"    as {use.describe()}, in: {use.source}\n"
        f"Every symbol must mean one thing throughout: a predicate or function "
        f"keeps the same number of arguments everywhere, and a name cannot be "
        f"two kinds of thing at once.\n"
        f"Nothing would report this later -- atoms of different arity simply "
        f"never unify, so the search would saturate and look like a negative "
        f"answer."
    )


def _walk_formula(
    formula,
    source,
    uses
):

    """Record every name in one formula."""

    if isinstance(
        formula,
        Atom
    ):

        _record(
            uses,
            formula.pred,
            Use(
                PREDICATE,
                len(formula.args),
                source
            )
        )

        for argument in formula.args:

            _walk_term(
                argument,
                source,
                uses
            )

        return

    if isinstance(
        formula,
        Not
    ):

        _walk_formula(
            formula.x,
            source,
            uses
        )

        return

    if isinstance(
        formula,
        (And, Or, Implies)
    ):

        _walk_formula(
            formula.a,
            source,
            uses
        )

        _walk_formula(
            formula.b,
            source,
            uses
        )

        return

    if isinstance(
        formula,
        (ForAll, Exists)
    ):

        _record(
            uses,
            formula.var,
            Use(
                VARIABLE,
                0,
                source
            )
        )

        _walk_formula(
            formula.body,
            source,
            uses
        )

        return

    raise TypeError(formula)


def _walk_term(
    term,
    source,
    uses
):

    """Record a term and, recursively, its arguments."""

    if term.is_var:

        kind = VARIABLE

    elif term.args:

        kind = FUNCTION

    else:

        kind = CONSTANT

    _record(
        uses,
        term.name,
        Use(
            kind,
            len(term.args),
            source
        )
    )

    for argument in term.args:

        _walk_term(
            argument,
            source,
            uses
        )
