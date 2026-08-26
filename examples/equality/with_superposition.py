"""4. אותו כלל, בגרסה שממנה בנויים הסולברים האמיתיים.

Paramodulation מציב שווה בשווה לשני הכיוונים -- גם את l במקום f וגם
את f במקום l. חצי מהעבודה הזאת מבטלת את החצי השני.

Superposition מוסיפה סדר על האיברים ומרשה להציב רק "במורד": תמיד
להחליף איבר גדול באיבר קטן ממנו, אף פעם לא להפך.

9 צעדים לעומת 16. אותה תשובה בדיוק, בכמעט חצי מהעבודה -- וככל
שהשאלה גדלה, ההבדל הזה הוא ההבדל בין סולבר שעובד לסולבר שנתקע.

כך עובדים Vampire ,E ו-SPASS.
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

    config.EQUALITY_RULE = "superposition"
    config.SHOW_FULL_KB_EACH_STEP = False

    result = prove(
        WITH_EQUALITY_SIGN,
        conclusion
    )
