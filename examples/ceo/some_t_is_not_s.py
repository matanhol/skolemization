"""המסקנה: יש מי שניסה ולא הצליח

exists x (T(x) and not S(x))

רץ עם ברירות המחדל, ומוכיח ב-7 צעדים.

הסתירה נסגרת דרך השוויון, וכך היא נראית בפלט:

מ-C7 ומ-C3 מקבלים S(c2), ומ-C2 נובע c2 = c1. אותו הדבר עבור c3.
השוויון c2 = c1 מוצב בתוך C5 והופך אותו ל-c1 ≠ c3, ואז c3 = c1
מוצב שוב ומתקבל c1 ≠ c1 -- ליטרל שהוא שקר בעצמו, נמחק מיד
(clauses.drop_false_equalities), ומה שנשאר הוא הפסוקית הריקה.

שימו לב שאף אחד משלושת הצעדים האלה אינו אקסיומת שוויון: זה כלל
ההיסק מציב שווה בשווה בתוך האיברים.
"""

COMMENTARY_EN = """The conclusion: someone applied and did not succeed

exists x (T(x) and not S(x))

Runs with the defaults, and proves in 7 steps.

The contradiction is closed through the equality, and this is how it
looks in the output:

from C7 and C3 we get S(c2), and from C2 it follows that c2 = c1. The
same for c3. The equality c2 = c1 is substituted into C5 and turns it
into c1 ≠ c3, then c3 = c1 is substituted again and c1 ≠ c1 comes
out -- a literal that is false in itself, deleted on sight
(clauses.drop_false_equalities), and what is left is the empty clause.

Note that not one of those three steps is an equality axiom: it is the
inference rule substituting equals for equals inside the terms.
"""


from skolemization import prove

from .assumptions import ASSUMPTIONS

conclusion = (
    "exists x (T(x) and not S(x))"
)


if __name__ == "__main__":

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
