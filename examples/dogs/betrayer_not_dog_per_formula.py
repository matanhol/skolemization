"""אותה הוכחה בדיוק כמו ב-betrayer_not_dog, מסופרת בסדר אחר:

במקום שכל שלב ירוץ על כל הנוסחאות,

כל נוסחה עוברת לבדה את השלבים 2 עד 7,

מהצורה שבה נכתבה ועד ה-clauses שלה,

ורק אז מתחילים בנוסחה הבאה.

ה-clauses שיוצאים בסוף זהים -- רק הסיפור שונה.
"""

from skolemization import (
    config,
    prove,
)

from .assumptions import BASE

conclusion = (
    "exists x, ((all y B(x,y)) and not D(x))"
)


if __name__ == "__main__":

    config.ONE_FORMULA_AT_A_TIME = True

    result = prove(
        BASE,
        conclusion
    )
