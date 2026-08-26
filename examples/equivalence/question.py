"""שאלה 3 -- שתי הנוסחאות שנבדקות, כמופע של Equivalence.

זהו רק מופע אחד של הבדיקה הכללית: אפשר להחליף כאן כל שתי נוסחאות
ולקבל את אותה בדיקה בדיוק.
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
