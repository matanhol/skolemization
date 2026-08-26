"""שאלה 8

הנחות:
1. כל מתכנת שיודע לוגיקה כותב קוד נכון
2. כל מי שכותב קוד נכו מקבל בונוס
3ֿֿ. קיים מתכנת שלא מקבל בונוס

מסקנה:
קיים מתכנת שלא יודע לוגיקה

הצרנה:
נגדיר:
Pr(x): x is a programmer
L(x): x knows logics
C(x): x writes code correctly
B(x): x gets bonus


Assumptions:

1. all x ((Pr(x) and L(x)) -> C(x))

2. all x (C(x) -> B(x))

3. exists x (Pr(x) and not B(x))

"""

ASSUMPTIONS = [
    "all x ((Pr(x) and L(x)) -> C(x))",
    "all x (C(x) -> B(x))",
    "exists x (Pr(x) and not B(x))"
]
