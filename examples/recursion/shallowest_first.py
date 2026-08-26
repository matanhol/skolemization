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
