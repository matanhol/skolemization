"""שאלה 3 -- שתי הנוסחאות שנבדקות, כמופע של Equivalence.

זהו רק מופע אחד של הבדיקה הכללית: אפשר להחליף כאן כל שתי נוסחאות
ולקבל את אותה בדיקה בדיוק.
"""

COMMENTARY_EN = """Question 3 -- the two formulas under test, as an instance of Equivalence.

This is only one instance of the general check: any two formulas at all can be
put here and get exactly the same check.
"""


from skolemization import Equivalence

from .formulas import (
    PHI1,
    PHI2,
)


def question():

    """The equivalence this example asks about."""

    return Equivalence(
        PHI1,
        PHI2
    )
