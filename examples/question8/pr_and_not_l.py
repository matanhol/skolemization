"""שאלה 8 -- המסקנה:

exists x (Pr(x) and not L(x))
"""

from skolemization import prove

from .assumptions import ASSUMPTIONS

conclusion = (
    "exists x (Pr(x) and not L(x))"
)


if __name__ == "__main__":

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
