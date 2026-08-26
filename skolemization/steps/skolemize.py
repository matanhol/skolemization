"""Step 4: replace existentials by witnesses.

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

    """Hands out Skolem names, numbered consistently across one KB.

    Constants are ``<letter>``, ``<letter>2``, ``<letter>3``, ...; functions
    are ``<letter>1``, ``<letter>2``, ...  Both letters are picked to avoid the
    problem's own vocabulary, so the defaults ``c`` and ``g`` only survive when
    nothing in the input uses them.
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

    def constant_name(
        self,
        number
    ):

        """What the ``number``-th constant is called: ``c``, ``c2``, ``c3``."""

        if number == 1:
            return self.constant_letter

        return (
            f"{self.constant_letter}"
            f"{number}"
        )

    @property
    def witness(self):
        """The name the first Skolem constant gets.

        focus.py hunts for this term; it is ``c`` unless the problem took it.
        """

        return self.constant_letter

    @property
    def witnesses(self):
        """Every constant handed out so far, in the order they were invented.

        focus.py asks how many there are: with ``c`` and ``c2`` both standing
        for "something that exists", there is no reason to guess that a
        universal variable means the first one.
        """

        return tuple(
            self.constant_name(
                number
            )
            for number
            in range(
                1,
                self.constant_counter + 1
            )
        )

    def new_function(
        self,
        universal_variables
    ):

        """A fresh function applied to the universals the ∃ sits under."""

        self.function_counter += 1

        return Term(
            f"{self.function_letter}"
            f"{self.function_counter}",
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

    def new_constant(self):

        """A fresh constant: the bare letter first, then numbered."""

        self.constant_counter += 1

        return Term(
            self.constant_name(
                self.constant_counter
            ),
            (),
            False
        )


def skolemize(
    f,
    names,
    universal_variables=(),
    explanations=None
):

    """Step 4: replace each ∃ by a witness depending on the ∀s enclosing it.

    Under no universal the witness is a constant; under some, a function of
    exactly those variables.  Every replacement is appended to ``explanations`` as
    (variable, replacement, universals), which is what the narration reports.
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
                explanations
            ),
            skolemize(
                f.b,
                names,
                universal_variables,
                explanations
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
                explanations
            ),
            skolemize(
                f.b,
                names,
                universal_variables,
                explanations
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
                explanations
            )
        )

    if isinstance(
        f,
        Exists
    ):

        if universal_variables:

            replacement = (
                names.new_function(
                    universal_variables
                )
            )

        else:

            replacement = (
                names.new_constant()
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
            explanations
        )

    raise TypeError(f)
