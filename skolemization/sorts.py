"""Which universe each argument place belongs to.

A first-order problem is written as if everything lived in one universe, but it
rarely means that: ``F(x, y)`` relates two kinds of thing, and the witness a
skolemization invents for the second place is not the same kind of thing as one
invented for the first.  Nothing in the syntax says so, and everything in the
reading does.

The universes are inferred, by the only rule there is: **two places hold the
same kind of thing when something is written in both**.  A variable shared
between ``D(x)`` and ``F(x, y)`` merges ``D·1`` with ``F·1``; a term occurring
in two places merges those; a function's result belongs to whichever place it
is written into.  Places never linked stay apart, which is what keeps
``F(x, y)`` two universes unless the problem says otherwise.

This runs *before* step 4, so skolemization can name a witness after the
universe it belongs to (steps/skolemize.py), and again afterwards on the
clauses, so counterexample.py can group what it prints.
"""

from .formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
)


# A function's result is a place too, so it can be merged with the argument
# places the function is written into.

RESULT = "result"


class Sorts:

    """Argument positions, merged into universes -- a union-find."""

    def __init__(self):

        self.parent = {}

    def find(self, node):

        """The universe a position belongs to."""

        self.parent.setdefault(
            node,
            node
        )

        while self.parent[node] != node:

            self.parent[node] = self.parent[
                self.parent[node]
            ]

            node = self.parent[node]

        return node

    def merge(self, one, other):

        """Say that these two positions hold the same kind of thing."""

        one = self.find(one)

        other = self.find(other)

        if one != other:

            self.parent[other] = one

    def universes(self):

        """Every universe, as a map from its representative to its positions."""

        grouped = {}

        for node in self.parent:

            grouped.setdefault(
                self.find(node),
                []
            ).append(
                node
            )

        return {
            root: sorted(members)
            for root, members
            in grouped.items()
        }


def sorts_of_clauses(clauses):

    """Infer the universes from where each variable and term is written.

    Runs over the clauses *as they entered the search*, not only the survivors:
    a link made by a clause that was later subsumed is still a fact about the
    vocabulary.
    """

    sorts = Sorts()

    for clause in clauses:

        occurrences = {}

        for literal in clause:

            for index, argument in enumerate(
                literal.atom.args
            ):

                _place_term(
                    argument,
                    (literal.atom.pred, index),
                    sorts,
                    occurrences
                )

        for places in occurrences.values():

            for other in places[1:]:

                sorts.merge(
                    places[0],
                    other
                )

    return sorts


def _place_term(
    term,
    position,
    sorts,
    occurrences
):

    """Record that ``term`` is written at ``position``, and recurse into it."""

    sorts.find(
        position
    )

    key = (
        term.name
        if term.is_var
        else term_key(term)
    )

    occurrences.setdefault(
        key,
        []
    ).append(
        position
    )

    if term.is_var:
        return

    if term.args:

        # The function's result is whatever this position holds; its arguments
        # are sorted by their own places in it.
        sorts.merge(
            position,
            (term.name, RESULT)
        )

        for index, argument in enumerate(
            term.args
        ):

            _place_term(
                argument,
                (term.name, index),
                sorts,
                occurrences
            )


def term_key(term):

    """A term as a hashable key -- ``g1(c)`` and ``g1(c)`` are the same thing."""

    if not term.args:
        return term.name

    return (
        term.name,
        tuple(
            term_key(argument)
            for argument
            in term.args
        )
    )


def is_ground(term):

    """Does this term mention no variable at all?"""

    if term.is_var:
        return False

    return all(
        is_ground(argument)
        for argument
        in term.args
    )


def position_label(position):

    """``P·1`` for an argument place, ``g1·→`` for a function's result."""

    symbol, index = position

    if index == RESULT:
        return f"{symbol}·→"

    return f"{symbol}·{index + 1}"


def sorts_of_formulas(formulas):

    """Infer the universes from formulas, before any witness exists.

    Same rule as over clauses, but a formula's quantifiers make the scoping
    explicit: variables are local to the formula they appear in, so the merges
    are made per formula and shared ground terms carry links between them.
    """

    sorts = Sorts()

    for formula in formulas:

        occurrences = {}

        _walk_atoms(
            formula,
            sorts,
            occurrences
        )

        for places in occurrences.values():

            for other in places[1:]:

                sorts.merge(
                    places[0],
                    other
                )

    return sorts


def _walk_atoms(
    formula,
    sorts,
    occurrences
):

    """Find every atom in a formula and place its arguments."""

    if isinstance(formula, Atom):

        for index, argument in enumerate(
            formula.args
        ):

            _place_term(
                argument,
                (formula.pred, index),
                sorts,
                occurrences
            )

        return

    if isinstance(formula, Not):

        _walk_atoms(
            formula.x,
            sorts,
            occurrences
        )

        return

    if isinstance(
        formula,
        (ForAll, Exists)
    ):

        _walk_atoms(
            formula.body,
            sorts,
            occurrences
        )

        return

    _walk_atoms(
        formula.a,
        sorts,
        occurrences
    )

    _walk_atoms(
        formula.b,
        sorts,
        occurrences
    )


def variable_universes(
    formula,
    sorts
):

    """Which universe each variable of this formula belongs to.

    What skolemization asks: the ∃ being eliminated stands for an element of
    *some* universe, and which one is decided by the places its variable is
    written in.
    """

    occurrences = {}

    _walk_atoms(
        formula,
        Sorts(),
        occurrences
    )

    return {
        name: sorts.find(places[0])
        for name, places
        in occurrences.items()
    }
