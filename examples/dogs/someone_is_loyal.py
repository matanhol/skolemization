"""מסקנה שלא נובעת מההנחות:

קיים איקס שנאמן לווי
"""

COMMENTARY_EN = """A conclusion that does not follow from the assumptions:

there is an x that is loyal to a y

The only assumption that can produce F is assumption 1, and it produces it only
for a dog -- and no assumption says any dog exists. Assumption 2 can consume an
F but never create one. So loyalty is never asserted of anything.
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
