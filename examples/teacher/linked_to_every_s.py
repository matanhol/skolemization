"""המסקנה שנמסרה עם השאלה

קיים x שהוא P, וכל S מקושר אליו.

רץ עם ברירות המחדל של החבילה כפי שהן -- הדירוג
"shallowest_general_first" והמיקוד ב-witness דלוק -- ומוכיח ב-6
צעדים.

כדאי לקרוא את שלב המיקוד בפלט: ההצבה x := c מקבעת את העצם שעליו
מדברים, ומכאן ואילך אין לאיברים לאן לגדול. בלי המיקוד הזה אותה
שאלה בדיוק בורחת, וזה מה ש-examples/recursion מראה.
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
