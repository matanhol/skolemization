"""2. ברירת המחדל: עומק האיברים הוא המפתח הראשון.

STRATEGY = "shallowest_general_first" מדרג קודם כל לפי כמה עמוק
מקונן האיבר העמוק ביותר בתוצאה, ורק אחר כך לפי אורך הפסוקית, לפי
"בלי הצבה" ולפי משקל.

השרשרת מ-runaway פשוט אף פעם לא נבחרת: S(g2(g1(g2(c)))) עמוק יותר
מכל דבר אחר שזמין באותו רגע, ולכן הוא מחכה -- ומעולם לא מגיע תורו.

6 צעדים, ואף איבר בהוכחה לא מקונן יותר מרמה אחת. אותה שאלה, אותו
סולבר, מפתח דירוג אחד נוסף.

המיקוד ב-witness מכובה גם כאן, כדי שההשוואה ל-runaway תהיה הוגנת;
עם המיקוד דלוק גם הדירוג הישן מוכיח (ב-7 צעדים), כי ההצבה x := c
ממילא לא נותנת לאיברים לגדול.
"""

COMMENTARY_EN = """2. The default: term depth is the first key.

STRATEGY = "shallowest_general_first" ranks first by how deeply the deepest
term in the result nests, and only after that by clause length, by "needs no
assignment", and by weight.

The chain from runaway is simply never picked: S(g2(g1(g2(c)))) is deeper than
anything else on offer at that moment, so it waits -- and its turn never comes.

6 steps, and no term in the proof nests more than one level. Same question,
same solver, one extra ranking key.

The witness focus is off here too, so that the comparison with runaway is a
fair one; with the focus on, even the old ranking proves it (in 7 steps),
because the substitution x := c does not let the terms grow in any case.
"""


from skolemization import (
    config,
    prove,
)

from .assumptions import ASSUMPTIONS

conclusion = (
    "exists x (P(x) and "
    "all y (S(y) --> L(y,x)))"
)


if __name__ == "__main__":

    config.FOCUS_ON_WITNESS = False

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
