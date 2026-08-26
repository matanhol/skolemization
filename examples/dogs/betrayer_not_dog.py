"""מסקנה שנובעת מההנחות:

קיים איקס שבוגד בכולם והוא לא כלב

    exists x ( (all y B(x,y)) and not D(x))
"""

from skolemization import prove

from .assumptions import BASE

conclusion = (
    "exists x, ((all y B(x,y)) and not D(x))"
)


if __name__ == "__main__":

    result = prove(
        BASE,
        conclusion
    )
