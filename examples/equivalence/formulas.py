"""שאלה 3

ננסה להוכיח/להפריך בשיטת הרברנד
המשמעות ששני פסוקים שקולים לוגית היא

phi1<-->phi2

כלומר

phi1 -> phi2

and

phi2 -> phi1

כלומר יש כאן "גם" של שתי (הנחות, מסקנה)

אם שתי הטענות נכונות אז הם שקולים לוגית

אם לפחות אחת מהם לא נכונה אז הם אינם שקולים לוגית
"""

COMMENTARY_EN = """Question 3

We will try to prove or refute by Herbrand's method.
The meaning of two formulas being logically equivalent is

phi1<-->phi2

that is

phi1 -> phi2

and

phi2 -> phi1

so what we have here is the "and" of two (assumptions, conclusion) pairs

if both claims hold then they are logically equivalent

if at least one of them does not hold then they are not logically equivalent
"""


PHI1 = (
    "(all x (P(x) -> exists y Q(x,y))) "
    "-> exists x exists y Q(x,y)"
)

PHI2 = (
    "(exists x (P(x) -> exists y Q(x,y))) "
    "-> exists x exists y Q(x,y)"
)
