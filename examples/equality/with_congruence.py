"""2. אותה שאלה, ועוד אקסיומה אחת: הקונגרואנציה של K.

עכשיו המסקנה מוכחת, וההוכחה משתמשת בשלושה דברים שונים:

בסימטריה, כדי להפוך את f = l ל-l = f;

בטרנזיטיביות, כדי לשרשר ל-l = g;

ובקונגרואנציה, כדי להעביר את K מהגנן לשולח המכתב.

הורדת הקונגרואנציה -- ראו without_congruence -- והמסקנה כבר לא מוכחת.

שני דברים נמדדו כאן וכדאי לשים לב אליהם:

**המחיר בצעדים.** 343 צעדים, ולכן גבול הצעדים מוגדל כאן. כלל ההיסק
עושה את אותה עבודה ב-16.

**הרפלקסיביות מזיקה.** אם מוסיפים גם reflexive_relations, החיפוש
לא מסיים גם ב-400 צעדים: האקסיומה Eq(x,x) מתאחדת כמעט עם כל שוויון
ומציפה את החיפוש. היא גם לא נחוצה כאן, ולכן היא לא מוגדרת.

והמחיר האמיתי הוא לא מספר הצעדים אלא האקסיומה עצמה: היא נכתבה ל-K
בלבד. לכל פרדיקט נוסף בשפה צריך אחת משלו, לכל פונקציה גם, וגם
לפונקציות ה-Skolem שנוצרות רק בשלב 4 -- שעליהן אי אפשר לכתוב
אקסיומה מראש, כי כשכותבים את ההנחות הן עוד לא קיימות.
"""

COMMENTARY_EN = """2. The same question, and one more axiom: congruence for K.

Now the conclusion is proved, and the proof uses three different things:

symmetry, to turn f = l into l = f;

transitivity, to chain that on to l = g;

and congruence, to carry K over from the gardener to the letter-sender.

Take the congruence away -- see without_congruence -- and the conclusion
is no longer proved.

Two things were measured here and are worth attention:

**The cost in steps.** 343 steps, which is why the step limit is raised
here. The inference rule does the same work in 16.

**Reflexivity does harm.** If reflexive_relations is declared as well, the
search does not finish even at 400 steps: the axiom Eq(x,x) unifies with
almost every equality and floods the search. It is also not needed here,
and so it is not declared.

And the real cost is not the number of steps but the axiom itself: it was
written for K alone. Every further predicate in the language needs one of
its own, every function does too, and so do the Skolem functions that come
into being only in step 4 -- for which no axiom can be written in advance,
because at the time the assumptions are written they do not yet exist.
"""


from skolemization import (
    config,
    prove,
)

from .assumptions import WITH_CONGRUENCE

conclusion = (
    "exists x exists y "
    "(L(x) and G(y) and Eq(x,y) and K(x))"
)


if __name__ == "__main__":

    config.MAX_RESOLUTION_STEPS = 400
    config.SHOW_FULL_KB_EACH_STEP = False

    result = prove(
        WITH_CONGRUENCE,
        conclusion,
        symmetric_relations={"Eq"},
        transitive_relations={"Eq"}
    )
