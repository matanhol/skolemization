"""מסקנה ש **לא** נובעת מההנחות:

קיים כלב
"""

COMMENTARY_EN = """A conclusion that does **not** follow from the assumptions:

there is a dog

The only assumption that mentions D is assumption 1, and it is a conditional:
it says what a dog would have, never that anything is a dog. A world with no
dogs at all satisfies all three assumptions, so there is nothing for the
refutation to work with.
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
