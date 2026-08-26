"""המסקנה שנמסרה עם השאלה

קיים x שהוא P, וכל S מקושר אליו.

רץ עם ברירות המחדל של החבילה כפי שהן -- הדירוג
"shallowest_general_first" והמיקוד ב-witness דלוק -- ומוכיח ב-6
צעדים.

כדאי לקרוא את שלב המיקוד בפלט: ההצבה x := c מקבעת את העצם שעליו
מדברים, ומכאן ואילך אין לאיברים לאן לגדול. בלי המיקוד הזה אותה
שאלה בדיוק בורחת, וזה מה ש-examples/recursion מראה.
"""

COMMENTARY_EN = """The conclusion as it was handed in with the question

There is an x which is P, and every S is linked to it.

Runs with the package defaults exactly as they stand -- the
"shallowest_general_first" ranking and the witness focus on -- and
proves in 6 steps.

It is worth reading the focus stage in the output: the substitution
x := c pins down the object being talked about, and from there on the
terms have nowhere to grow. Without that focus this very same question
runs away, and that is what examples/recursion shows.
"""


from skolemization import prove

from .assumptions import ASSUMPTIONS

conclusion = (
    "exists x (P(x) and "
    "all y (S(y) --> L(y,x)))"
)


if __name__ == "__main__":

    result = prove(
        ASSUMPTIONS,
        conclusion
    )
