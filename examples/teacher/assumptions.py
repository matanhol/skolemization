"""הדוגמה של המרצה

הנחות:

1. exists x (P(x) and (all y (exists z P(z) and L(y,z)) --> L(y,x)))

2. all y (S(y) --> exists z P(z) and L(y,z))

מסקנה:

exists x (P(x) and all y (S(y) --> L(y,x)))


בקריאה חופשית: ההנחה הראשונה אומרת שיש עצם x שהוא P, וכל y שמקושר
ל-P כלשהו מקושר גם ל-x. השנייה אומרת שכל S מקושר ל-P כלשהו. המסקנה
מחברת ביניהן: אותו x הוא P, וכל S מקושר אליו.


אחרי ההצרנה ה-KB הוא:

C1: P(c)

C2: ¬P(z) ∨ ¬L(y, z) ∨ L(y, c)

C3: ¬S(y) ∨ P(g(y))

C4: ¬S(y) ∨ L(y, g(y))

C5: ¬P(x) ∨ S(h(x))

C6: ¬P(x) ∨ ¬L(h(x), x)


שווה לשים לב מאיפה מגיעות שתי פונקציות ה-Skolem: g מן ה-∃z שבתוך
ההנחה השנייה, ו-h מן ה-∃ שנוצר כששוללים את המסקנה. שתיהן תלויות
במשתנה אוניברסלי, ולכן הן פונקציות ולא קבועים.

השאלה הזאת חוזרת ב-examples/recursion, שם היא מוצגת שוב עם דירוג
אחר ובלי המיקוד ב-witness -- ואז החיפוש בורח לאיברים מקוננים ולא
מסיים. כאן היא רצה כפי שנמסרה, עם ברירות המחדל.
"""

COMMENTARY_EN = """The lecturer's own example

Assumptions:

1. exists x (P(x) and (all y (exists z P(z) and L(y,z)) --> L(y,x)))

2. all y (S(y) --> exists z P(z) and L(y,z))

Conclusion:

exists x (P(x) and all y (S(y) --> L(y,x)))


Read loosely: the first assumption says there is an object x which is
P, and that every y linked to some P is linked to x as well. The
second says that every S is linked to some P. The conclusion joins
them: that same x is P, and every S is linked to it.


After clausification the KB is:

C1: P(c)

C2: ¬P(z) ∨ ¬L(y, z) ∨ L(y, c)

C3: ¬S(y) ∨ P(g(y))

C4: ¬S(y) ∨ L(y, g(y))

C5: ¬P(x) ∨ S(h(x))

C6: ¬P(x) ∨ ¬L(h(x), x)


It is worth seeing where the two Skolem functions come from: g from
the ∃z inside the second assumption, and h from the ∃ created when
the conclusion is negated. Both depend on a universal variable, which
is why they are functions and not constants.

This question comes back in examples/recursion, where it is shown
again under a different ranking and with the witness focus off -- and
there the search runs away into nested terms and never finishes. Here
it runs exactly as it was handed in, with the defaults.
"""


ASSUMPTIONS = [
    "exists x (P(x) and "
    "(all y (exists z P(z) and L(y,z)) --> L(y,x)))",

    "all y (S(y) --> exists z P(z) and L(y,z))"
]
