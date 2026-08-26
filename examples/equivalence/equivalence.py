"""שני הכיוונים יחד, ופסק הדין על השקילות.

אם שתי הגרירות מוכחות אז φ1 ≡ φ2.
אם לפחות אחת לא הוכחה, ה-solver לא הוכיח שקילות.

כל העבודה נעשית ב-Equivalence שבחבילה עצמה;
כאן רק מספקים את שתי הנוסחאות.
"""

COMMENTARY_EN = """Both directions together, and the verdict on equivalence.

If both entailments are proved then φ1 ≡ φ2.
If at least one of them is not proved, the solver has not proved equivalence.

All the work happens in Equivalence, inside the package itself;
here we only supply the two formulas.
"""


from .question import question


def main():

    """Check the two formulas of שאלה 3 for equivalence."""

    return question().check()


if __name__ == "__main__":

    main()
