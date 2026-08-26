"""אותה שאלה (3 סעיף א), אבל בלי אף אקסיומה של שוויון.

כאן כותבים

x = y

ולא Eq(x,y), ואת השוויון מטפל **כלל היסק** ולא אקסיומות:

Paramodulation -- הצבת שווה בשווה בתוך פסוקית.

למה זה עדיף?

שלוש האקסיומות (רפלקסיביות, סימטריה, טרנזיטיביות) הופכות את Eq
ליחס שקילות בלבד. שוויון דורש גם קונגרואנציה:

אם x = y אז לכל פרדיקט P מתקיים P(x) -> P(y),

ולכל פונקציה f מתקיים f(x) = f(y).

כלומר צריך אקסיומה לכל פרדיקט ולכל פונקציה בשפה --
כולל פונקציות ה-Skolem שנוצרות בשלב 4.

כלל ההיסק מחליף את כולן בבת אחת, כי הוא מציב בתוך האיברים עצמם.

האקסיומה היחידה שנשארת היא x = x, והסולבר מוסיף אותה לבד.

ראו גם with_superposition, שבו אותו כלל מוגבל לפי סדר איברים.
"""

from skolemization import (
    config,
    prove,
)

from .assumptions import WITH_EQUALITY_SIGN

conclusion = (
    "exists x "
    "(P(x) and "
    "(all y (P(y) -> y = x)))"
)


if __name__ == "__main__":

    config.EQUALITY_RULE = "paramodulation"

    result = prove(
        WITH_EQUALITY_SIGN,
        conclusion
    )
