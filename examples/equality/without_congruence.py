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
