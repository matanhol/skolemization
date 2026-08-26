"""אותה שאלה ואותו כלל, אבל בגרסה שממנה בנויים הסולברים האמיתיים.

Paramodulation מציב שווה בשווה לשני הכיוונים: גם x במקום y וגם y
במקום x. חצי מהעבודה הזאת מבטלת את החצי השני, והחיפוש מסתובב סביב
עצמו.

Superposition מוסיפה סדר על האיברים ומרשה להציב רק "במורד" --
תמיד להחליף איבר גדול בקטן ממנו, אף פעם לא להפך.

זה בדיוק ההבדל בין שתי הדוגמאות, והוא נמדד:

אותה תשובה, אבל מספר האפשרויות שנשקלות בכל צעד קטן פי כמה.

כך עובדים Vampire ,E ו-SPASS.
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

    config.EQUALITY_RULE = "superposition"

    result = prove(
        WITH_EQUALITY_SIGN,
        conclusion
    )
