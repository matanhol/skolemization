"""שאלה 8 -- המסקנה:

exists x (Pr(x) and not L(x))
"""

COMMENTARY_EN = """Question 8 -- the conclusion:

exists x (Pr(x) and not L(x))

Read it back into words: some programmer does not know logic. The
argument runs backwards through the two implications. Assumption 3
hands us a programmer who gets no bonus; by assumption 2 he cannot be
writing correct code; by assumption 1 he cannot be both a programmer
and a logic-knower -- and a programmer he is, so logic he does not
know.
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
