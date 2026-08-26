"""שאלה 3 סעיף א

נתון ההיגד:

"(all x all y

((P(x) and P(y)) -> x=y)))

and

exists x P(x)"


והשאלה האם הוא גורר את המסקנה:

"exists x

(P(x)

and

(all y (P(y) -> y=x)))

במילים:

יש איזו פונקציה בוליאנית שמקיימת

p(x) and p(y) -> x=y

כלומר היא מקבלת ערך אמת רק על ערך מסוים, על כל היתר היא מקבלת ערך שקר


וגם ידוע שקיים x ש p מקבלת ערך אמת עליו

צריך להוכיח:

קיים x כך ש p מקבלת ערך אמת עליו

כך שלכל y

אם p(y)

אז y=x


כלומר

קיים x

כך ש p מקבלת עליו אמת

וגם

p מקיימת את התכונה הנ"ל ביחס אליו ספציפית

זה נובע מההנחות

---------


נשים לב שצריך להוסיף במפורש את העובדה שיחס שוויון הוא סימטרי


אחרת הוא לא ידע ש

x=y, y=x

 זה אותו דבר


הוספתי גם את המידע שיחס השוויון הוא טרזנטיבי ורפלקסיבי

(למרות שזה לא נדרש כאן)

for good measure

כשמגדירים לסולבר שיחס מסוים מקיים תכונה מסוימת, הוא מוסיף ל

Knowledge base

היגד מתאים

לדוגמה אם מגדירים לו שהיחס סימטרי,

הוא מוסיף את ההיגד:

all x all y (Eq(x,y) -> Eq(y,x))
"""

COMMENTARY_EN = """Question 3a

The premise is:

"(all x all y

((P(x) and P(y)) -> x=y)))

and

exists x P(x)"


and the question is whether it entails the conclusion:

"exists x

(P(x)

and

(all y (P(y) -> y=x)))

In words:

there is some boolean function satisfying

p(x) and p(y) -> x=y

that is, it comes out true on one particular value only, and false on
everything else


and it is also known that there exists an x on which p comes out true

what has to be proved:

there exists an x on which p comes out true

such that for every y

if p(y)

then y=x


that is

there exists an x

on which p is true

and

p has that property with respect to that x specifically

this follows from the assumptions

---------


Note that the fact that the equality relation is symmetric has to be
stated explicitly


otherwise the solver will not know that

x=y, y=x

 are the same thing


I also supplied the information that the equality relation is transitive
and reflexive

(even though that is not needed here)

for good measure

when you declare to the solver that some relation has some property, it
adds to the

Knowledge base

a matching statement

for example, if you declare that the relation is symmetric,

it adds the statement:

all x all y (Eq(x,y) -> Eq(y,x))
"""


ASSUMPTIONS = [
    "all x all y ((P(x) and P(y)) -> Eq(x,y))",
    "exists x P(x)"
]


# ------------------------------------------------
# אותן הנחות בדיוק, כתובות עם סימן השוויון עצמו
#
# כאן לא מגדירים שום תכונה של היחס: את השוויון
# מטפל כלל היסק, ולא אקסיומות
# ------------------------------------------------

WITH_EQUALITY_SIGN = [
    "all x all y ((P(x) and P(y)) -> x = y)",
    "exists x P(x)"
]


# ------------------------------------------------
# Properties of relations
# ------------------------------------------------

EQ_SYMMETRIC = {
    "Eq"
}

EQ_TRANSITIVE = {
    "Eq"
}

EQ_REFLEXIVE = {
    "Eq"
}
