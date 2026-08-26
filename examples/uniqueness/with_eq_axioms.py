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

COMMENTARY_EN = """Question 3a

Note that the fact that the equality relation is symmetric has to be added
explicitly (and transitive and reflexive too, for good measure).

The conclusion uses Eq(y,x) while the assumption supplies Eq(x,y), so
without symmetry no contradiction will be found -- see without_eq_axioms.


A note on the search strategy:

the default is "shallowest_general_first" -- depth of terms before
anything else, so that the search does not run away into nested terms
(see examples/recursion).

Here, of all places, that preference does damage: the equality axioms
build deep terms (transitivity and congruence do precisely that), and
under that ranking the search does not finish within 150 steps. Under the
previous ranking, without the depth key, the proof is found in 7 steps.

That is measured, and it is why this example picks a strategy explicitly:
there is no one ranking that always wins, and that is exactly the lesson.
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
