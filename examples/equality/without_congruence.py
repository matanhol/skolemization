"""1. הכישלון: Eq עם תכונות היחס, בלי אקסיומת קונגרואנציה.

מגדירים ל-Eq רפלקסיביות, סימטריה וטרנזיטיביות -- יחס שקילות מלא --
ובכל זאת המסקנה לא מוכחת.

החיפוש יכול להגיע עד l = g, ושם הוא נעצר: אין שום דבר שמחבר בין
היחס Eq לבין הפרדיקט K.

ויש גם מודל נגדי: עולם שבו שולח המכתב והגנן שקולים זה לזה, לגנן יש
מפתח ולשולח המכתב אין -- מקיים את כל ההנחות ומפריך את המסקנה.
הסולבר לא טועה כאן; ההיגד באמת לא נובע מההנחות שנתנו לו.

צורת הכישלון היא UNKNOWN ולא SATURATED: עם אקסיומת הטרנזיטיביות
ב-KB אפשר לייצר שוויונות חדשים בלי סוף, ולכן החיפוש לעולם לא רווי --
הוא פשוט מגיע לגבול הצעדים. גבול גבוה יותר לא היה משנה את התשובה.

השוו ל-with_congruence, שבו מוסיפים אקסיומה אחת והמסקנה מוכחת.
"""

COMMENTARY_EN = """1. The failure: Eq with the relation properties, without a congruence axiom.

Eq is declared reflexive, symmetric and transitive -- a full equivalence
relation -- and even so the conclusion is not proved.

The search can get as far as l = g, and there it stops: there is nothing
at all connecting the relation Eq to the predicate K.

There is a counter-model, too: a world in which the letter-sender and the
gardener are equivalent to each other, the gardener holds a key and the
letter-sender does not -- it satisfies every assumption and refutes the
conclusion. The solver is not going wrong here; the statement genuinely
does not follow from the assumptions it was handed.

The shape of the failure is UNKNOWN and not SATURATED: with the
transitivity axiom in the KB, new equalities can be generated without end,
so the search is never saturated -- it simply reaches the step limit. A
higher limit would not have changed the answer.

Compare with with_congruence, where one axiom is added and the conclusion
is proved.
"""


from skolemization import (
    config,
    prove,
)

from .assumptions import WITHOUT_CONGRUENCE

conclusion = (
    "exists x exists y "
    "(L(x) and G(y) and Eq(x,y) and K(x))"
)


if __name__ == "__main__":

    config.SHOW_FULL_KB_EACH_STEP = False

    result = prove(
        WITHOUT_CONGRUENCE,
        conclusion,
        symmetric_relations={"Eq"},
        transitive_relations={"Eq"},
        reflexive_relations={"Eq"}
    )
