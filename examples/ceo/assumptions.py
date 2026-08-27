"""דוגמת המנכ"ל

הנחות:

1. Exists x (S(x) and (all y (S(y) --> (y=x))))

2. Exists x exists y (T(x) and T(y) and not (x=y))

מסקנה:

exists x (T(x) and not S(x))


קריאה: T(x) הוא "x ניסה לקבל את תפקיד המנכ"ל", ו-S(x) הוא "x
הצליח לקבל אותו".

ההנחה הראשונה אומרת שהצליח בדיוק אחד: קיים מי שהצליח, וכל מי
שהצליח שווה לו. ההנחה השנייה אומרת שלפחות שניים שונים ניסו.
המסקנה: יש מי שניסה ולא הצליח.

הטיעון עצמו קצר: אילו שני המנסים היו מצליחים, כל אחד מהם היה שווה
למי שהצליח -- ולכן הם היו שווים זה לזה, בסתירה לכך שהם שונים.


אחרי ההצרנה ה-KB הוא:

C1: S(c1)

C2: ¬S(y) ∨ y = c1

C3: T(c2)

C4: T(c3)

C5: c2 ≠ c3

C6: x = x

C7: ¬T(x) ∨ S(x)


שתי נקודות ששווה לעקוב אחריהן בפלט:

C6 לא נכתבה על ידי אף אחד. ברירת המחדל היא
EQUALITY_RULE = "paramodulation", והשאלה מזכירה את הסימן =, ולכן
הסולבר מוסיף בעצמו את אקסיומת הרפלקסיביות ומסביר למה. שאר תכונות
השוויון -- סימטריה, טרנזיטיביות וקונגרואנציה -- לא נכתבות כאן
בכלל: כלל ההיסק עושה את עבודתן.

ה-Skolemization יצרה שלושה witnesses -- c1, c2 ו-c3 -- ולכן שלב
המיקוד מדולג. ההצבה x := c1 היא ניחוש בין שלושה עצמים שונים, ואין
סיבה להעדיף אחד מהם, כך שהחיפוש רץ ישר על ה-KB הכללי.
"""

COMMENTARY_EN = """The CEO example

Assumptions:

1. Exists x (S(x) and (all y (S(y) --> (y=x))))

2. Exists x exists y (T(x) and T(y) and not (x=y))

Conclusion:

exists x (T(x) and not S(x))


Reading: T(x) is "x applied for the CEO post", and S(x) is "x
succeeded in getting it".

The first assumption says that exactly one succeeded: someone
succeeded, and everyone who succeeded is equal to him. The second says
that at least two different people applied. The conclusion: someone
applied and did not succeed.

The argument itself is short: if both applicants had succeeded, each
of them would be equal to the one who succeeded -- and so they would
be equal to each other, contradicting the fact that they differ.


After clausification the KB is:

C1: S(c1)

C2: ¬S(y) ∨ y = c1

C3: T(c2)

C4: T(c3)

C5: c2 ≠ c3

C6: x = x

C7: ¬T(x) ∨ S(x)


Two things worth following in the output:

C6 was written by nobody. The default is
EQUALITY_RULE = "paramodulation", and the question mentions the sign
=, so the solver adds the reflexivity axiom itself and explains why.
The remaining properties of equality -- symmetry, transitivity and
congruence -- are not written here at all: the inference rule does
their work.

Skolemization produced three witnesses -- c1, c2 and c3 -- so the
witness-focus stage is skipped. The substitution x := c1 would be a
guess between three different objects, and there is no reason to
prefer any one of them, so the search runs straight on the general KB.
"""


ASSUMPTIONS = [
    "Exists x (S(x) and (all y (S(y) --> (y=x))))",
    "Exists x exists y (T(x) and T(y) and not (x=y))"
]
