"""Rendering formulas, clauses and the whole knowledge base."""

from . import config
from .formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Implies,
    Not,
    Or,
    atom_str,
    is_equality,
    negated_equality_str,
)
from .output import (
    say,
    say_block,
)


# What gets a bracket.
#
# Not what precedence would settle -- what the structure says, so that a reader
# who has never memorised the table still knows what binds to what:
#
#   1. a quantifier brackets its whole scope, even a scope of one atom:
#      ∃y (P(y, x));
#   2. a quantifier standing as an operand is closed off as well, so its reach
#      cannot be misread:  ∀x (Q(x) ∧ (∃y (P(y, x))));
#   3. where the connective changes, both sides are bracketed unless a side is
#      a single predicate.  Only a run of one connective may go without:
#      (P(x) ∨ Q(x)) ∨ (R(z) ∧ S(y)), but P(x) ∨ Q(x) ∨ R(x).  A chain of → is
#      not a run, because → does not associate;
#   4. ¬ brackets a connective and nothing else: ¬(A ∧ B), but ¬P(x).
#
# Nothing is bracketed for the parser's sake, and nothing is kept because the
# author wrote it: the brackets are recomputed from the tree every time, so a
# step that flattens the tree loses them.  Dropping ∀x in step 5 takes its
# scope bracket with it.

BINARY_CONNECTIVES = {
    Implies: "→",
    Or: "∨",
    And: "∧",
}

ASSOCIATIVE_CONNECTIVES = (
    And,
    Or,
)


# How a bracket is drawn.
#
# P(x) and g1(x) are an *application*, not a grouping, so the ordinary one-row
# ( ) belongs to them and no grouping bracket may be that small.  Under
# config.TALL_BRACKETS a grouping bracket is stacked out of these pieces
# instead -- three rows innermost and two more for every level outwards, so the
# outermost is the tallest and all of them are bigger than a predicate's.

BRACKET_PIECES = {
    "(": ("⎛", "⎜", "⎝"),
    ")": ("⎞", "⎟", "⎠"),
}

SHORTEST_BRACKET = 3

BRACKET_GROWTH = 2


def formula_str(f):

    """Render a formula tree with the usual logical symbols.

    Only the brackets the structure calls for -- see the rules above -- so the
    ones written into an assumption to keep the parser honest do not come back
    out, and the ones the author left to precedence are put in::

        typed     all x Q(x) and exists y P(y,x)
        printed   ∀x (Q(x) ∧ (∃y (P(y, x))))

    The result is a *block*: one line while ``config.TALL_BRACKETS`` is off,
    several when it is on, with the formula itself on the middle row.  Callers
    print it with :func:`narration.formula_block` rather than dropping it into
    the middle of a sentence.

    Raises TypeError on anything that is not a formula node, which is how a
    pipeline bug -- a ``Literal`` reaching here, say -- announces itself.
    """

    pieces = formula_pieces(
        f,
        0
    )

    if not config.TALL_BRACKETS:

        return "".join(
            text
            for text, _
            in pieces
        )

    return stacked(
        pieces
    )


def formula_pieces(
    f,
    depth,
    parent=None
):

    """The formula as (text, bracket depth or None) pieces, left to right.

    A piece carrying a depth is one bracket character; everything else is
    ordinary text.  Keeping them apart is what lets the same rendering be
    printed flat or drawn at full height.

    ``parent`` is the connective this node hangs off, or None where nothing
    encloses it -- at the top, or directly inside a bracket that has already
    been placed.  It is what rule 2 is decided by.
    """

    if isinstance(f, Atom):

        return [
            (atom_str(f), None)
        ]

    if isinstance(f, Not):

        # A negated equality is spelled the way the literal spells it.
        if (
            isinstance(f.x, Atom)
            and
            is_equality(f.x)
        ):

            return [
                (
                    negated_equality_str(
                        f.x.args[0],
                        f.x.args[1]
                    ),
                    None
                )
            ]

        if type(f.x) in BINARY_CONNECTIVES:

            return (
                [("¬", None)]
                + bracketed(
                    formula_pieces(
                        f.x,
                        depth + 1
                    ),
                    depth
                )
            )

        return (
            [("¬", None)]
            + formula_pieces(
                f.x,
                depth,
                parent
            )
        )

    if isinstance(
        f,
        (ForAll, Exists)
    ):

        return quantifier_pieces(
            f,
            depth,
            parent
        )

    if type(f) not in BINARY_CONNECTIVES:
        raise TypeError(f)

    symbol = BINARY_CONNECTIVES[
        type(f)
    ]

    pieces = []

    for index, child in enumerate(
        (f.a, f.b)
    ):

        if index:

            pieces.append(
                (f" {symbol} ", None)
            )

        if (
            type(child) in BINARY_CONNECTIVES
            and
            brackets_the_sides(f)
        ):

            pieces += bracketed(
                formula_pieces(
                    child,
                    depth + 1
                ),
                depth
            )

            continue

        pieces += formula_pieces(
            child,
            depth,
            f
        )

    return pieces


def brackets_the_sides(f):

    """Does this connective bracket its operands -- rule 3?

    It does whenever the connective *changes* here: an operand built from a
    different connective, or any operand at all under ``→``, which does not
    associate and so has no runs.  A run of one associative connective is the
    only thing that goes without, which is what keeps a clause flat.
    """

    if type(f) not in ASSOCIATIVE_CONNECTIVES:

        return any(
            type(child) in BINARY_CONNECTIVES
            for child
            in (f.a, f.b)
        )

    return any(
        type(child) in BINARY_CONNECTIVES
        and
        type(child) is not type(f)
        for child
        in (f.a, f.b)
    )


def quantifier_pieces(
    f,
    depth,
    parent
):

    """``∀x (...)`` or ``∃x (...)`` -- rules 1 and 2.

    The scope always takes a bracket, however small it is, because that bracket
    is the only thing saying where the quantifier stops.  Standing as an
    operand the quantifier takes a second one around itself, so a reader does
    not have to work out whether it reaches past its neighbour.
    """

    symbol = (
        "∀"
        if isinstance(f, ForAll)
        else "∃"
    )

    standing_alone = parent is None

    scope = (
        depth
        if standing_alone
        else depth + 1
    )

    pieces = (
        [(f"{symbol}{f.var} ", None)]
        + bracketed(
            formula_pieces(
                f.body,
                scope + 1
            ),
            scope
        )
    )

    if standing_alone:
        return pieces

    return bracketed(
        pieces,
        depth
    )


def bracketed(
    pieces,
    depth
):

    """``pieces`` with a bracket pair of level ``depth`` around them."""

    return (
        [("(", depth)]
        + pieces
        + [(")", depth)]
    )


def stacked(pieces):

    """The formula drawn on a grid, every grouping bracket at its own height.

    The formula sits on the middle row and each bracket reaches symmetrically
    above and below it, which is why a height is always odd: three rows for the
    innermost level, two more for every level further out.  A bracket belonging
    to ``P(x)`` is not a grouping and stays on the middle row with the text.
    """

    characters = []

    for text, depth in pieces:

        if depth is None:

            characters += [
                (character, None)
                for character
                in text
            ]

            continue

        characters.append(
            (text, depth)
        )

    deepest = max(
        (
            depth
            for _, depth
            in characters
            if depth is not None
        ),
        default=-1
    ) + 1

    if not deepest:

        return "".join(
            character
            for character, _
            in characters
        )

    rows = bracket_height(
        0,
        deepest
    )

    middle = rows // 2

    canvas = [
        [" "] * len(characters)
        for _
        in range(rows)
    ]

    for column, (character, depth) in enumerate(
        characters
    ):

        if depth is None:

            canvas[middle][column] = character

            continue

        height = bracket_height(
            depth,
            deepest
        )

        top, extension, bottom = BRACKET_PIECES[
            character
        ]

        first = middle - height // 2

        last = first + height - 1

        canvas[first][column] = top

        canvas[last][column] = bottom

        for row in range(
            first + 1,
            last
        ):

            canvas[row][column] = extension

    return "\n".join(
        "".join(row).rstrip()
        for row
        in canvas
    )


def bracket_height(
    depth,
    deepest
):

    """How many rows a bracket at this level is drawn over."""

    return (
        SHORTEST_BRACKET
        + BRACKET_GROWTH
        * (deepest - 1 - depth)
    )


def clause_str(clause):

    """Render a clause as a disjunction.  The empty clause is □."""

    if len(clause) == 0:
        return "□"

    return " ∨ ".join(
        str(literal)
        for literal in clause
    )


def clause_as_formula(clause):

    """One clause as a formula line: the flat ``∀x ∀y `` prefix, then its reading.

    A clause is a disjunction, but that is not how anyone states the fact it
    stands for.  The negative literals are the *conditions* and the positive
    ones the *consequences*, so the reading is an implication where there are
    both, a denial where there are only conditions, and a plain disjunction
    where there are only consequences.  The counter-model block wants that
    reading -- one terse fact per line -- rather than a clause list.

    Only the body is built as a formula tree and handed to the ordinary
    machinery, so the bracket rules, the ``≠`` spelling and
    ``config.TALL_BRACKETS`` all still hold inside it, and the result may be
    several rows for :func:`output.say_block` to print.  The quantifier prefix
    is *not* part of that tree: written as formulas the variables would nest,
    ``∀x (∀y (...))``, and a block of facts each buried one bracket deeper than
    the last is exactly what makes the old prose unreadable.

    The empty clause is □, as in :func:`clause_str` -- though a counter-model
    never has one to show, since deriving it is what would have refuted the KB.
    """

    if len(clause) == 0:
        return "□"

    names = []

    def collect(term):

        """Note this term's variables, in order of first appearance.

        Nested rather than shared: ``counterexample.variables_of`` is already
        the top-level name for this job, and the notebook flattens every module
        into one namespace, where a second definition would silently win.
        """

        if term.is_var:

            name = str(term)

            if name not in names:
                names.append(name)

            return

        for argument in term.args:
            collect(argument)

    def chain(
        connective,
        atoms
    ):

        """``atoms`` folded to the left, the nesting the printer draws flat."""

        folded = atoms[0]

        for atom in atoms[1:]:

            folded = connective(
                folded,
                atom
            )

        return folded

    for literal in clause:

        for argument in literal.atom.args:
            collect(argument)

    conditions = [
        literal.atom
        for literal in clause
        if literal.negated
    ]

    consequences = [
        literal.atom
        for literal in clause
        if not literal.negated
    ]

    if not conditions:

        body = chain(
            Or,
            consequences
        )

    elif not consequences:

        body = Not(
            chain(
                And,
                conditions
            )
        )

    else:

        body = Implies(
            chain(
                And,
                conditions
            ),
            chain(
                Or,
                consequences
            )
        )

    # Only a binary connective needs closing off after the prefix: ¬(...)
    # already brackets whatever it denies, and an atom cannot be misread.

    if type(body) in BINARY_CONNECTIVES:

        pieces = bracketed(
            formula_pieces(
                body,
                1
            ),
            0
        )

    else:

        pieces = formula_pieces(
            body,
            0
        )

    prefix = "".join(
        f"∀{name} "
        for name in names
    )

    if prefix:

        pieces = (
            [(prefix, None)]
            + pieces
        )

    if not config.TALL_BRACKETS:

        return "".join(
            text
            for text, _
            in pieces
        )

    return stacked(
        pieces
    )


def show_formulas(
    formulas,
    title="KB"
):

    """Print the formulas under a caption, numbered F1, F2, ...

    The counterpart of :func:`show_kb` for the stages before clausification,
    so a step can close by showing the whole knowledge base in the same framing
    the clause KB gets later.
    """

    say(
        "\n"
        + "-" * 70
    )

    say(title)

    say(
        "-" * 70
    )

    for i, formula in enumerate(
        formulas,
        1
    ):

        say_block(
            f"F{i}: ",
            formula_str(
                formula
            )
        )

    say(
        "-" * 70
    )


def show_kb(
    kb,
    title="KB"
):

    """Print the whole knowledge base under a caption, numbered C1, C2, ..."""

    say(
        "\n"
        + "-" * 70
    )

    say(title)

    say(
        "-" * 70
    )

    for i, clause in enumerate(
        kb,
        1
    ):

        say(
            f"C{i}: "
            f"{clause_str(clause)}"
        )

    say(
        "-" * 70
    )
