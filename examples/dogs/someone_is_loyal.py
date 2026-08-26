"""מסקנה שלא נובעת מההנחות:

קיים איקס שנאמן לווי
"""

from skolemization import prove

from .assumptions import BASE

conclusion = (
    "exists x, exists y, F(x,y)"
)


if __name__ == "__main__":

    result = prove(
        BASE,
        conclusion
    )
