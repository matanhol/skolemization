"""חיפוש שבורח לאיברים מקוננים

השאלה:

הנחות:

1. exists x (P(x) and (all y (exists z P(z) and L(y,z)) --> L(y,x)))

2. all y (S(y) --> exists z P(z) and L(y,z))

מסקנה:

exists x (P(x) and all y (S(y) --> L(y,x)))


אחרי ההצרנה ה-KB הוא:

C1: P(c)

C2: ¬P(z) ∨ ¬L(y, z) ∨ L(y, c)

C3: ¬S(y) ∨ P(g(y))

C4: ¬S(y) ∨ L(y, g(y))

C5: ¬P(x) ∨ S(h(x))

C6: ¬P(x) ∨ ¬L(h(x), x)


ושימו לב ל-C3 ול-C5 ביחד: מ-P משהו מקבלים S של h שלו, ומ-S משהו
מקבלים P של g שלו. כלומר כל עובדה חדשה מייצרת עובדה חדשה עמוקה
יותר, בלי סוף:

P(c)  ⟶  S(h(c))  ⟶  P(g(h(c)))  ⟶  S(h(g(h(c))))  ⟶  ...

כל אחת מהן היא clause באורך אחד, כללית, ובלי צורך בהצבה ממשית --
כלומר כל מפתחות הדירוג האחרים אוהבים אותה. רק העומק מבדיל ביניהן.


שתי הדוגמאות כאן הן אותה שאלה בדיוק:

runaway            -- הדירוג הישן, בלי מפתח העומק.  בורח.

shallowest_first   -- ברירת המחדל היום.  6 צעדים, ואף איבר לא מקונן.


נקודה שקל לפספס: המיקוד ב-witness מסתיר את הבעיה. הוא מקבע x := c,
ואז אין לאיברים לאן לגדול. לכן שתי הדוגמאות מכבות אותו -- אחרת
השאלה נפתרת מיד ולא רואים כלום.
"""

COMMENTARY_EN = """A search that runs away into nested terms

The question:

assumptions:

1. exists x (P(x) and (all y (exists z P(z) and L(y,z)) --> L(y,x)))

2. all y (S(y) --> exists z P(z) and L(y,z))

conclusion:

exists x (P(x) and all y (S(y) --> L(y,x)))


After clausification the KB is:

C1: P(c)

C2: ¬P(z) ∨ ¬L(y, z) ∨ L(y, c)

C3: ¬S(y) ∨ P(g(y))

C4: ¬S(y) ∨ L(y, g(y))

C5: ¬P(x) ∨ S(h(x))

C6: ¬P(x) ∨ ¬L(h(x), x)


Now look at C3 and C5 together: from P of something you get S of its h, and
from S of something you get P of its g. So every new fact manufactures a new
fact one level deeper, without end:

P(c)  ⟶  S(h(c))  ⟶  P(g(h(c)))  ⟶  S(h(g(h(c))))  ⟶  ...

Each of these is a clause of length one, general, and needs no real
assignment -- which is to say every other ranking key likes it. Only depth
tells them apart.


The two examples here are the very same question:

runaway            -- the old ranking, without the depth key.  It runs away.

shallowest_first   -- today's default.  6 steps, and no term nests.


A point that is easy to miss: the witness focus hides the problem. It pins
x := c, and then the terms have nowhere to grow. So both examples switch it
off -- otherwise the question is settled at once and there is nothing to see.
"""


ASSUMPTIONS = [
    "exists x (P(x) and "
    "(all y (exists z P(z) and L(y,z)) --> L(y,x)))",

    "all y (S(y) --> exists z P(z) and L(y,z))"
]
