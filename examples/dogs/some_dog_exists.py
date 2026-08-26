"""מסקנה ש **לא** נובעת מההנחות:

קיים כלב
"""

from skolemization import prove

from .assumptions import BASE

conclusion = (
    "exists x, D(x)"
)


if __name__ == "__main__":

    result = prove(
        BASE,
        conclusion
    )
