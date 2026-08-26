"""Terms, formulas and literals: the data model.

Includes the two small stringifiers the model itself depends on
(``Term.__str__`` needs ``visible_variable_name``, ``Literal.__str__``
needs ``atom_str``).  Everything else that prints lives in display.py.
"""

from dataclasses import dataclass
from typing import Tuple
import re

from . import config


def visible_variable_name(name):
    """
    Hide internal standardized variable names.

    Examples:

        __v230_x -> x
        __v17_y  -> y
        __v3_z   -> z

    Ordinary variable names remain unchanged.
    """

    match = re.match(
        r"^__v\d+_(.+)$",
        name
    )

    if match:
        return match.group(1)

    return name


@dataclass(frozen=True)
class Term:

    """A term: a variable, a constant, or a function applied to terms.

    ``is_var`` is the only thing separating the variable ``x`` from the constant
    ``c`` -- both are argument-less.  Frozen, so terms work as dict keys and set
    members, which the substitution and canonical-form machinery relies on.
    """

    name: str
    args: Tuple["Term", ...] = ()
    is_var: bool = False

    def __str__(self):

        """Render the term, hiding internal names (``__v12_x`` prints as ``x``)."""

        shown_name = (
            visible_variable_name(self.name)
            if self.is_var
            else self.name
        )

        if self.args:

            return (
                f"{shown_name}("
                + ", ".join(
                    str(arg)
                    for arg in self.args
                )
                + ")"
            )

        return shown_name


@dataclass(frozen=True)
class Atom:

    """A predicate applied to terms, such as ``P(x, f(y))``."""

    pred: str
    args: Tuple[Term, ...]


@dataclass(frozen=True)
class Not:

    """Negation of a formula.

    After NNF (step 3) it only ever wraps an ``Atom``, and step 7 folds those
    into negated literals.
    """

    x: object


@dataclass(frozen=True)
class And:

    """Conjunction.  Binary -- the parser nests longer chains to the left."""

    a: object
    b: object


@dataclass(frozen=True)
class Or:

    """Disjunction.  Binary and left-nested, like ``And``."""

    a: object
    b: object


@dataclass(frozen=True)
class Implies:

    """Implication.  Removed in step 2; no later stage handles it."""

    a: object
    b: object


@dataclass(frozen=True)
class ForAll:

    """Universal quantifier binding ``var`` in ``body``.  Dropped in step 5."""

    var: str
    body: object


@dataclass(frozen=True)
class Exists:

    """Existential quantifier binding ``var``.  Replaced by a witness in step 4."""

    var: str
    body: object


@dataclass(frozen=True)
class Literal:

    """An atom, possibly negated -- the unit a clause is built from."""

    atom: Atom
    negated: bool = False

    def __str__(self):

        """Render as ``P(x)``, ``¬P(x)``, ``x = y`` or ``x ≠ y``."""

        if (
            self.negated
            and
            is_equality(self.atom)
        ):

            return negated_equality_str(
                self.atom.args[0],
                self.atom.args[1]
            )

        prefix = (
            "¬"
            if self.negated
            else ""
        )

        return (
            prefix
            + atom_str(self.atom)
        )


# The predicate ``x = y`` parses into.  Written here rather than imported from
# parsing/aliases.py because formulas.py is below the parser in the import
# order -- the two spellings must stay in step, and parsing/aliases.py says so.

EQUALITY = "="


def is_equality(atom):
    """Is this atom an equality, and so printed infix?"""

    return (
        atom.pred == EQUALITY
        and
        len(atom.args) == 2
    )


# How a *negated* equality is spelled.  ``x != y``, ``x ≠ y`` and
# ``not (x = y)`` are one and the same tree -- the parser produces
# ``Not(Atom("=", ...))`` for all three -- so this is a choice about the output
# and nothing else.  ``config.NEGATED_EQUALITY`` picks between them.

NEGATED_EQUALITY_SPELLINGS = (
    "≠",
    "not",
)


def negated_equality_str(
    left,
    right
):

    """``x ≠ y`` or ``¬(x = y)``, per ``config.NEGATED_EQUALITY``.

    Every place that prints a disequality comes through here -- the literal,
    the formula printer and the narration -- so a transcript never mixes the
    two spellings.  An unrecognised setting raises rather than quietly
    printing one of them, the same way STRATEGY and EQUALITY_RULE do.
    """

    if config.NEGATED_EQUALITY not in NEGATED_EQUALITY_SPELLINGS:

        raise ValueError(
            f"unknown NEGATED_EQUALITY {config.NEGATED_EQUALITY!r}; "
            "expected one of "
            + ", ".join(
                repr(spelling)
                for spelling
                in NEGATED_EQUALITY_SPELLINGS
            )
        )

    if config.NEGATED_EQUALITY == "not":

        return (
            f"¬({left}"
            f" = "
            f"{right})"
        )

    return (
        f"{left}"
        f" ≠ "
        f"{right}"
    )


def atom_str(atom):

    """Render an atom as ``pred(arg, arg)``, or ``arg = arg`` for equality."""

    if is_equality(atom):

        return (
            f"{atom.args[0]}"
            f" = "
            f"{atom.args[1]}"
        )

    return (
        f"{atom.pred}("
        + ", ".join(
            str(arg)
            for arg in atom.args
        )
        + ")"
    )
