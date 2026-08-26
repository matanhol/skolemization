"""מסקנה שנובעת מההנחות:

קיים איקס שבוגד בכולם והוא לא כלב

    exists x ( (all y B(x,y)) and not D(x))
"""

COMMENTARY_EN = """A conclusion that does follow from the assumptions:

there is an x that betrays everyone and is not a dog

    exists x ( (all y B(x,y)) and not D(x))

The argument to watch for in the output: assumption 3 gives a betrayer, and he
betrays *everyone* -- so in particular he betrays the very owner assumption 1
would give him. Were he a dog, he would be loyal to that owner, and assumption
2 turns loyalty into "does not betray". The two collide, so the betrayer cannot
be a dog, and he is the witness the conclusion asks for.
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
