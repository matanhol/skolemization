"""Step 4: replace existentials by witnesses.

Witnesses are named after the **universe** they belong to, which is why sorts
are inferred before this step (sorts.py).  ``F(x, y)`` relates two kinds of
thing, and a witness invented for the second place is not the same kind of
thing as one invented for the first -- so they should not look alike.  One
witness in a universe gets the bare letter, several get numbers::

    one universe, one witness      c
    one universe, three witnesses  c1, c2, c3
    two universes                  c ... and d, or d1, d2


Witnesses are invented names, so they must not collide with names the user
wrote.  They would not merely look confusing -- they would change the answer.
Skolemizing ``all x exists y R(x,y)`` into ``R(x, g1(x))`` when the problem
already mentions ``g1`` silently identifies the invented function with the
user's, and proves things that do not follow.

So the family of names is chosen against the problem's own vocabulary: see
``choose_letter``.
"""

import re

from ..formulas import (
    And,
    Atom,
    Exists,
    ForAll,
    Not,
    Or,
    Term,
)
from ..sorts import variable_universes
from ..substitution import substitute_formula


# Preferences, in order.  Constants traditionally start at c and functions at
# g; the rest are fallbacks for when those families are already spoken for.

CONSTANT_LETTERS = "cdefghijklmnopqrstuvwxyz"
FUNCTION_LETTERS = "ghijklmnopqrstuvwxyzabcdef"


def choose_letter(
    preferences,
    occupied
):

    """The first preferred letter whose whole family is free.

    A family is every name the generator could produce from a letter -- ``c``,
    ``c1``, ``c2``, and so on -- so one occupied member rules out the letter
    entirely.  Writing ``g`` blocks ``g1``; writing ``g1`` blocks ``g2`` just
    the same.  The point is that a reader seeing ``g1`` and ``g2`` should never
    have to wonder whether one of them was theirs.
    """

    for letter in preferences:

        family = re.compile(
            rf"^{letter}\d*$"
        )

        if not any(
            family.match(name)
            for name
            in occupied
        ):

            return letter

    raise ValueError(
        "every candidate letter is already used by the problem; "
        "rename something to free one up"
    )


class SkolemNames:

    """Hands out Skolem names, one letter family per universe.

    A universe's witnesses share a letter: the bare letter when it needs only
    one, numbers when it needs several.  Letters are picked to avoid the
    problem's own vocabulary, so the defaults ``c`` for constants and ``g`` for
    functions only survive when nothing in the input uses them.

    ``plan`` must be called before any name is handed out -- "one witness or
    several" cannot be decided while inventing the first one.
    """

    def __init__(
        self,
        occupied=()
    ):

        """Choose both letter families, then start the counters at zero.

        The constant letter is chosen first and then counted as occupied, so
        the two families can never be the same -- which would have them
        collide at ``c2``.
        """

        occupied = set(
            occupied
        )

        self.constant_letter = (
            choose_letter(
                CONSTANT_LETTERS,
                occupied
            )
        )

        self.function_letter = (
            choose_letter(
                FUNCTION_LETTERS,
                occupied
                |
                {self.constant_letter}
            )
        )

        self.function_counter = 0
        self.constant_counter = 0

        # universe -> (letter, how many it needs, how many handed out)
        self.constant_plan = {}
        self.function_plan = {}

        # The constants actually invented, in order -- focus.py reads these.
        self.handed_out = []

        self.occupied = occupied

    def plan(
        self,
        formulas,
        sorts
    ):

        """Work out, before naming anything, what each universe will need.

        Walks the formulas as they stand after step 3 and counts the ∃ that
        step 4 will eliminate, per universe and split by what each becomes: a
        constant when nothing universal encloses it, a function otherwise.
        """

        constants = {}

        functions = {}

        for formula in formulas:

            universes = variable_universes(
                formula,
                sorts
            )

            _count_existentials(
                formula,
                universes,
                False,
                constants,
                functions
            )

        # Nothing is reserved up front: the first universe should get ``c``,
        # which is what a reader expects, and the flat fallback letters chosen
        # in __init__ are only for a caller that never planned.
        self.constant_plan = self._letters(
            constants,
            CONSTANT_LETTERS,
            set()
        )

        self.function_plan = self._letters(
            functions,
            FUNCTION_LETTERS,
            {
                letter
                for letter, _, _
                in self.constant_plan.values()
            }
        )

    def _letters(
        self,
        counts,
        preferences,
        taken
    ):

        """A letter for each universe, in the order the universes are met."""

        plan = {}

        for universe, needed in counts.items():

            letter = choose_letter(
                preferences,
                set(self.occupied) | taken
            )

            taken = set(taken) | {letter}

            plan[universe] = [
                letter,
                needed,
                0
            ]

        return plan

    def constant_name(
        self,
        number
    ):

        """What the ``number``-th constant is called, ignoring universes.

        The fallback for a KB nobody planned -- a caller that skolemizes
        without calling :meth:`plan` first, which the tests do.
        """

        if number == 1:
            return self.constant_letter

        return (
            f"{self.constant_letter}"
            f"{number}"
        )

    def _name_in(
        self,
        plan,
        universe,
        fallback
    ):

        """The next name in this universe's family, or the flat fallback."""

        if universe not in plan:
            return fallback()

        letter, needed, handed = plan[
            universe
        ]

        plan[universe][2] = handed + 1

        if needed == 1:
            return letter

        return (
            f"{letter}"
            f"{handed + 1}"
        )

    @property
    def witness(self):
        """The name the first Skolem constant got, or what it would get.

        focus.py hunts for this term.  Before anything has been handed out
        there is nothing to report but the letter the flat fallback would use.
        """

        if self.handed_out:
            return self.handed_out[0]

        return self.constant_letter

    @property
    def witnesses(self):
        """Every constant handed out so far, in the order they were invented.

        Recorded rather than recomputed, because the names now depend on which
        universe each witness belongs to and how many that universe needed.

        focus.py asks how many there are: with two constants both standing for
        "something that exists", there is no reason to guess that a universal
        variable means the first one.
        """

        return tuple(
            self.handed_out
        )

    def new_function(
        self,
        universal_variables,
        universe=None
    ):

        """A fresh function applied to the universals the ∃ sits under.

        Named in the universe of what it *returns*, since that is the kind of
        thing ``g(x)`` denotes.
        """

        self.function_counter += 1

        def flat():

            return (
                f"{self.function_letter}"
                f"{self.function_counter}"
            )

        return Term(
            self._name_in(
                self.function_plan,
                universe,
                flat
            ),
            tuple(
                Term(
                    variable,
                    (),
                    True
                )
                for variable
                in universal_variables
            ),
            False
        )

    def new_constant(
        self,
        universe=None
    ):

        """A fresh constant, in the family of the universe it stands for."""

        self.constant_counter += 1

        def flat():

            return self.constant_name(
                self.constant_counter
            )

        name = self._name_in(
            self.constant_plan,
            universe,
            flat
        )

        self.handed_out.append(
            name
        )

        return Term(
            name,
            (),
            False
        )


def _count_existentials(
    formula,
    universes,
    under_universal,
    constants,
    functions
):

    """Count the witnesses each universe will need, without inventing any.

    An ∃ under a ∀ becomes a function of it; an ∃ that stands free becomes a
    constant.  Counting first is what lets a universe with one witness call it
    ``c`` instead of ``c1``.
    """

    if isinstance(formula, Exists):

        universe = universes.get(
            formula.var
        )

        counts = (
            functions
            if under_universal
            else constants
        )

        counts[universe] = counts.get(
            universe,
            0
        ) + 1

        _count_existentials(
            formula.body,
            universes,
            under_universal,
            constants,
            functions
        )

        return

    if isinstance(formula, ForAll):

        _count_existentials(
            formula.body,
            universes,
            True,
            constants,
            functions
        )

        return

    if isinstance(formula, Not):

        _count_existentials(
            formula.x,
            universes,
            under_universal,
            constants,
            functions
        )

        return

    if isinstance(
        formula,
        (And, Or)
    ):

        _count_existentials(
            formula.a,
            universes,
            under_universal,
            constants,
            functions
        )

        _count_existentials(
            formula.b,
            universes,
            under_universal,
            constants,
            functions
        )


def skolemize(
    f,
    names,
    universal_variables=(),
    explanations=None,
    universes=None
):

    """Step 4: replace each ∃ by a witness depending on the ∀s enclosing it.

    Under no universal the witness is a constant; under some, a function of
    exactly those variables.  Every replacement is appended to ``explanations`` as
    (variable, replacement, universals), which is what the narration reports.

    ``universes`` maps this formula's variables to the universe each belongs
    to, so the witness can be named after it (sorts.py).  Without it the names
    fall back to one flat family, which is what a caller skolemizing a formula
    on its own gets.
    """

    if explanations is None:
        explanations = []

    if isinstance(
        f,
        (Atom, Not)
    ):

        return f

    if isinstance(
        f,
        And
    ):

        return And(
            skolemize(
                f.a,
                names,
                universal_variables,
                explanations,
                universes
            ),
            skolemize(
                f.b,
                names,
                universal_variables,
                explanations,
                universes
            )
        )

    if isinstance(
        f,
        Or
    ):

        return Or(
            skolemize(
                f.a,
                names,
                universal_variables,
                explanations,
                universes
            ),
            skolemize(
                f.b,
                names,
                universal_variables,
                explanations,
                universes
            )
        )

    if isinstance(
        f,
        ForAll
    ):

        return ForAll(
            f.var,
            skolemize(
                f.body,
                names,
                universal_variables
                +
                (f.var,),
                explanations,
                universes
            )
        )

    if isinstance(
        f,
        Exists
    ):

        universe = (
            universes.get(f.var)
            if universes
            else None
        )

        if universal_variables:

            replacement = (
                names.new_function(
                    universal_variables,
                    universe
                )
            )

        else:

            replacement = (
                names.new_constant(
                    universe
                )
            )

        explanations.append(
            (
                f.var,
                replacement,
                universal_variables
            )
        )

        new_body = (
            substitute_formula(
                f.body,
                {
                    f.var:
                    replacement
                }
            )
        )

        return skolemize(
            new_body,
            names,
            universal_variables,
            explanations,
            universes
        )

    raise TypeError(f)
