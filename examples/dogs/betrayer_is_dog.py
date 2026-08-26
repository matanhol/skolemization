"""מסקנה ש **לא** נובעת מההנחות:

קיים כלב שבוגד בכולם

כלומר: קיים x שבוגד בכולם והוא כלב
"""

from skolemization import prove

from .assumptions import BASE

conclusion = (
    "exists x, ((all y B(x,y)) and D(x))"
)


if __name__ == "__main__":

    result = prove(
        BASE,
        conclusion
    )
