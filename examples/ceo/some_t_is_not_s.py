"""המסקנה: יש מי שניסה ולא הצליח

exists x (T(x) and not S(x))

רץ עם ברירות המחדל, ומוכיח ב-7 צעדים.

הסתירה נסגרת דרך השוויון, וכך היא נראית בפלט:

מ-C7 ומ-C3 מקבלים S(c2), ומ-C2 נובע c2 = c. אותו הדבר עבור c3.
השוויון c2 = c מוצב בתוך C5 והופך אותו ל-c ≠ c3, ואז c3 = c מוצב
שוב ומתקבל c ≠ c -- ליטרל שהוא שקר בעצמו, נמחק מיד
(clauses.drop_false_equalities), ומה שנשאר הוא הפסוקית הריקה.

שימו לב שאף אחד משלושת הצעדים האלה אינו אקסיומת שוויון: זה כלל
ההיסק מציב שווה בשווה בתוך האיברים.
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
