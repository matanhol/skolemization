"""שני הכיוונים יחד, ופסק הדין על השקילות.

אם שתי הגרירות מוכחות אז φ1 ≡ φ2.
אם לפחות אחת לא הוכחה, ה-solver לא הוכיח שקילות.

כל העבודה נעשית ב-Equivalence שבחבילה עצמה;
כאן רק מספקים את שתי הנוסחאות.
"""

from .question import question


def main():

    """Check the two formulas of שאלה 3 for equivalence."""

    return question().check()


if __name__ == "__main__":

    main()
