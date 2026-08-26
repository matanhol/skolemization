"""3. אותה שאלה, עם הסימן = וכלל היסק במקום אקסיומות.

ההנחה היא ההנחה של השאלה, וזהו:

אין רפלקסיביות, אין סימטריה, אין טרנזיטיביות, ואין קונגרואנציה.

Paramodulation מציב שווה בשווה בתוך האיברים עצמם, ולכן הוא עושה את
עבודתן של שלוש התכונות **וגם** של הקונגרואנציה, לכל פרדיקט ולכל
פונקציה בשפה בבת אחת -- כאן זה K, בלי שאיש כתב עליו אקסיומה.

ההוכחה עצמה קצרה: f = l מציב את f בתוך f = g ונותן l = g; אחר כך
l = g מציב בתוך K(g) ונותן K(l); ומכאן שלוש רזולוציות סוגרות.

16 צעדים, לעומת 343 בדרך של האקסיומות.

האקסיומה היחידה שמתווספת היא x = x, והסולבר מוסיף אותה לבד ומסביר למה.
"""

from skolemization import (
    config,
    prove,
)

from .assumptions import WITH_EQUALITY_SIGN

conclusion = (
    "exists x exists y "
    "(L(x) and G(y) and x = y and K(x))"
)


if __name__ == "__main__":

    config.EQUALITY_RULE = "paramodulation"
    config.SHOW_FULL_KB_EACH_STEP = True

    result = prove(
        WITH_EQUALITY_SIGN,
        conclusion
    )
