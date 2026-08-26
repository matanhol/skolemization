"""שאלה 3 סעיף א

נשים לב שצריך להוסיף במפורש את העובדה שיחס שוויון הוא סימטרי
(וגם טרזנטיבי ורפלקסיבי for good measure)

המסקנה משתמשת ב-Eq(y,x), בעוד ההנחה נותנת Eq(x,y),
ולכן בלי הסימטריה הוא לא יימצא סתירה -- ראו without_eq_axioms.


הערה על אסטרטגיית החיפוש:

ברירת המחדל היא "shallowest_general_first" -- קודם כל העומק של
האיברים, כדי שהחיפוש לא יברח לאיברים מקוננים (ראו examples/recursion).

דווקא כאן ההעדפה הזאת מזיקה: אקסיומות השוויון בונות איברים עמוקים
(טרנזיטיביות וקונגרואנציה בדיוק עושות את זה), ותחת הדירוג ההוא
החיפוש לא מסיים ב-150 צעדים. עם הדירוג הקודם, בלי מפתח העומק,
ההוכחה נמצאת ב-7 צעדים.

זה נמדד, וזאת הסיבה שהדוגמה הזאת בוחרת אסטרטגיה במפורש: אין דירוג
אחד שמנצח תמיד, וזה בדיוק הלקח.
"""

from skolemization import (
    config,
    prove,
)

from .assumptions import (
    ASSUMPTIONS,
    EQ_REFLEXIVE,
    EQ_SYMMETRIC,
    EQ_TRANSITIVE,
)

conclusion = (
    "exists x "
    "(P(x) and "
    "(all y (P(y) -> Eq(y,x))))"
)


if __name__ == "__main__":

    config.STRATEGY = "shortest_general_first"

    result = prove(
        ASSUMPTIONS,
        conclusion,
        symmetric_relations=EQ_SYMMETRIC,
        transitive_relations=EQ_TRANSITIVE,
        reflexive_relations=EQ_REFLEXIVE
    )
