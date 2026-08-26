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

COMMENTARY_EN = """The same question and the same rule, but in the version real provers are built on.

Paramodulation substitutes equals for equals in both directions: x in
place of y, and y in place of x alike. Half of that work undoes the other
half, and the search goes round in circles.

Superposition adds an ordering on terms and permits substituting only
"downhill" -- always replacing a larger term by a smaller one, never the
other way about.

That is exactly the difference between the two examples, and it is
measured:

the same answer, but the number of candidates weighed at each step is
several times smaller.

This is how E, Vampire and SPASS work.
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
