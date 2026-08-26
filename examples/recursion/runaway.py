"""1. הדירוג הישן: החיפוש בורח לאיברים מקוננים.

STRATEGY = "shortest_general_first" -- קודם אורך הפסוקית, אחר כך
"בלי הצבה", ורק אז משקל האיברים. אף אחד מהמפתחות האלה לא מבחין בין
S(g2(c)) לבין S(g2(g1(g2(g1(g2(c)))))): שתיהן פסוקית באורך אחד.

התוצאה: כל צעד מייצר את הדבר הבא בשרשרת, מעט יותר עמוק, לנצח.

כאן הגבול מונמך ל-12 צעדים כדי שאפשר יהיה לקרוא את זה -- עם הגבול
הרגיל, 150 צעדים, הסולבר מגיע לאיברים בעומק **מאה** ומחזיר UNKNOWN
אחרי כמעט דקה.

המיקוד ב-witness מכובה בכוונה: הוא מקבע x := c ומסתיר את התופעה.
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

    config.STRATEGY = "shortest_general_first"
    config.FOCUS_ON_WITNESS = False
    config.MAX_RESOLUTION_STEPS = 12

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
