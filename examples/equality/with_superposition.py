"""4. אותו כלל, בגרסה שממנה בנויים הסולברים האמיתיים.

Paramodulation מציב שווה בשווה לשני הכיוונים -- גם את l במקום f וגם
את f במקום l. חצי מהעבודה הזאת מבטלת את החצי השני.

Superposition מוסיפה סדר על האיברים ומרשה להציב רק "במורד": תמיד
להחליף איבר גדול באיבר קטן ממנו, אף פעם לא להפך.

9 צעדים לעומת 16. אותה תשובה בדיוק, בכמעט חצי מהעבודה -- וככל
שהשאלה גדלה, ההבדל הזה הוא ההבדל בין סולבר שעובד לסולבר שנתקע.

כך עובדים Vampire ,E ו-SPASS.
"""

COMMENTARY_EN = """4. The same rule, in the version real solvers are built out of.

Paramodulation substitutes equals for equals in both directions -- l in
place of f, and f in place of l as well. Half of that work undoes the
other half.

Superposition adds an ordering on terms and permits substituting only
"downhill": always replacing a term by one smaller than it, never the
other way round.

9 steps against 16. Exactly the same answer, for almost half the work --
and the bigger the question gets, the more that difference is the
difference between a solver that works and a solver that gets stuck.

This is how Vampire, E and SPASS work.
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
