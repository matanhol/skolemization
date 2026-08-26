"""מסקנה ש **לא** נובעת מההנחות:

קיים כלב שבוגד בכולם

כלומר: קיים x שבוגד בכולם והוא כלב
"""

COMMENTARY_EN = """A conclusion that does **not** follow from the assumptions:

there is a dog that betrays everyone

that is: there is an x that betrays everyone and is a dog

Assumption 3 does hand us a betrayer, so half of the conclusion is there for
the taking. Nothing, however, ties that betrayer to D: assumption 1 only says
what follows *if* something is a dog, and no assumption ever asserts that
anything is one. So the search runs dry rather than reaching □.
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
