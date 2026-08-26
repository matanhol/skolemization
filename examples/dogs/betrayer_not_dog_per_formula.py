"""אותה הוכחה בדיוק כמו ב-betrayer_not_dog, מסופרת בסדר אחר:

במקום שכל שלב ירוץ על כל הנוסחאות,

כל נוסחה עוברת לבדה את השלבים 2 עד 7,

מהצורה שבה נכתבה ועד ה-clauses שלה,

ורק אז מתחילים בנוסחה הבאה.

ה-clauses שיוצאים בסוף זהים -- רק הסיפור שונה.
"""

COMMENTARY_EN = """Exactly the same proof as in betrayer_not_dog, told in a different order:

instead of each step sweeping across all the formulas,

each formula goes through steps 2 to 7 on its own,

from the form it was written in down to its clauses,

and only then do we start on the next formula.

The clauses that come out at the end are identical -- only the story differs.
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
