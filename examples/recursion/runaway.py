"""1. הדירוג הישן: החיפוש בורח לאיברים מקוננים.

STRATEGY = "shortest_general_first" -- קודם אורך הפסוקית, אחר כך
"בלי הצבה", ורק אז משקל האיברים. אף אחד מהמפתחות האלה לא מבחין בין
S(h(c)) לבין S(h(g(h(g(h(c)))))): שתיהן פסוקית באורך אחד.

התוצאה: כל צעד מייצר את הדבר הבא בשרשרת, מעט יותר עמוק, לנצח.

כאן הגבול מונמך ל-12 צעדים כדי שאפשר יהיה לקרוא את זה -- עם הגבול
הרגיל, 150 צעדים, הסולבר מגיע לאיברים בעומק **מאה** ומחזיר UNKNOWN
אחרי כמעט דקה.

המיקוד ב-witness מכובה בכוונה: הוא מקבע x := c ומסתיר את התופעה.
"""

COMMENTARY_EN = """1. The old ranking: the search runs away into nested terms.

STRATEGY = "shortest_general_first" -- clause length first, then "needs no
assignment", and only then term weight. Not one of those keys can tell
S(h(c)) from S(h(g(h(g(h(c)))))): both are a clause of length one.

The result: every step produces the next link in the chain, a little deeper,
forever.

Here the limit is lowered to 12 steps so that this stays readable -- with the
usual limit of 150 steps the solver reaches terms of depth **one hundred** and
returns UNKNOWN after nearly a minute.

The witness focus is off on purpose: it pins x := c and hides the phenomenon.
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
