"""שוויון: פריצה, טביעת אצבע, מכתב וגנן

הסיפור:

בבית נפרצה דלת. החקירה העלתה שלושה תיאורים של אדם ועובדה אחת:

1. מי שהשאיר את טביעת האצבע הוא מי ששלח את מכתב הסחיטה.

2. אותו אדם עצמו הוא הגנן.

3. לגנן יש מפתח לבית.

מסקנה:

מי ששלח את המכתב הוא הגנן, ובידו מפתח.


ההצרנה:

F(x): x השאיר את טביעת האצבע

L(x): x שלח את המכתב

G(x): x הגנן

K(x): x מחזיק במפתח


הנחה:

exists f exists l exists g

    (F(f) and f = l and f = g and L(l) and G(g) and K(g))

מסקנה:

exists x exists y (L(x) and G(y) and x = y and K(x))


שימו לב מה הופך את זה לשאלה על שוויון: שלושת התיאורים הם שלושה
**איברים** שונים בשפה, והחקירה אומרת ששניים מהם מציינים אותו אדם.
זה לא "אדם אחד עם שלוש תכונות" -- זה שלושה שמות ושתי זהויות.


ה-clauses שיוצאים:

C1: f = l        C4: G(g)

C2: f = g        C5: K(g)

C3: L(l)         C6: F(f)

C7: ¬L(x) ∨ ¬G(y) ∨ ¬Eq(x,y) ∨ ¬K(x)      (שלילת המסקנה)


ולמה צריך את שלוש התכונות **וגם** קונגרואנציה:

**סימטריה** -- שתי הזהויות נתונות כשמי-שהשאיר-טביעה נמצא ראשון
(f = l ו-f = g), ואילו אקסיומת הטרנזיטיביות דורשת שהאיבר המשותף
יהיה באמצע. לכן צריך להפוך אחת מהן: מ-f = l ל-l = f.

**טרנזיטיביות** -- מ-l = f ומ-f = g מקבלים l = g. את זה שום
אקסיומת קונגרואנציה לא תיתן: קונגרואנציה מזיזה פרדיקט לאורך שוויון,
היא לא מייצרת שוויון חדש. וזו בדיוק הסיבה שהמסקנה כאן דורשת את
השוויון עצמו ולא רק תכונה.

**קונגרואנציה** -- המסקנה רוצה גם שבידו של שולח המכתב יהיה מפתח,
והמפתח ידוע רק אצל הגנן. בלי קונגרואנציה השוויון l = g ידוע וחסר
תועלת: יחס שקילות מרשה ל-K להתקיים על g ולא להתקיים על l.

והמחיר גלוי לעין: את אקסיומת הקונגרואנציה צריך לכתוב עבור K --
כלומר צריך לדעת מראש איזה פרדיקט ירצו להזיז.


ארבע הדוגמאות הן אותה שאלה בדיוק:

without_congruence   -- Eq ותכונות היחס בלבד.  לא מוכיח.

with_congruence      -- ועוד אקסיומת קונגרואנציה של K.  343 צעדים.

with_paramodulation  -- הסימן = וכלל היסק, בלי אף אקסיומה.  16 צעדים.

with_superposition   -- אותו כלל, מוגבל לפי סדר איברים.  9 צעדים.
"""

COMMENTARY_EN = """Equality: a burglary, a fingerprint, a letter and a gardener

The story:

A door was forced open. The investigation produced three descriptions of a
person, and one fact:

1. Whoever left the fingerprint is whoever sent the blackmail letter.

2. That same person is the gardener.

3. The gardener holds a key to the house.

Conclusion:

Whoever sent the letter is the gardener, and holds a key.


The formalization:

F(x): x left the fingerprint

L(x): x sent the letter

G(x): x is the gardener

K(x): x holds a key


Assumption:

exists f exists l exists g

    (F(f) and f = l and f = g and L(l) and G(g) and K(g))

Conclusion:

exists x exists y (L(x) and G(y) and x = y and K(x))


Notice what makes this a question about equality: the three descriptions
are three different **terms** of the language, and the investigation says
that two of them denote the same person. This is not "one person with
three properties" -- it is three names and two identities.


The clauses that come out:

C1: f = l        C4: G(g)

C2: f = g        C5: K(g)

C3: L(l)         C6: F(f)

C7: ¬L(x) ∨ ¬G(y) ∨ ¬Eq(x,y) ∨ ¬K(x)      (the negated conclusion)


And why all three properties are needed **as well as** congruence:

**Symmetry** -- both identities are given with the fingerprint-leaver
written first (f = l and f = g), whereas the transitivity axiom wants the
shared term in the middle. So one of them has to be turned around: from
f = l to l = f.

**Transitivity** -- from l = f and f = g we get l = g. No congruence
axiom will ever hand you that: congruence moves a predicate along an
equality, it does not manufacture a new equality. And that is precisely
why the conclusion here demands the equality itself and not just a
property.

**Congruence** -- the conclusion also wants the letter-sender to hold a
key, and the key is known only of the gardener. Without congruence the
equality l = g is known and useless: an equivalence relation is free to
let K hold of g and fail of l.

And the cost is there for all to see: the congruence axiom has to be
written for K -- that is, you have to know in advance which predicate the
proof is going to want to move.


The four examples are the very same question:

without_congruence   -- Eq and the relation properties alone.  Does not prove.

with_congruence      -- plus a congruence axiom for K.  343 steps.

with_paramodulation  -- the sign = and an inference rule, with no axioms.  16 steps.

with_superposition   -- the same rule, restricted by a term ordering.  9 steps.
"""


# ההנחה של השאלה, בניסוח עם Eq.

WITHOUT_CONGRUENCE = [
    "exists f exists l exists g "
    "(F(f) and Eq(f,l) and Eq(f,g) "
    "and L(l) and G(g) and K(g))"
]


# הקונגרואנציה של K -- אקסיומה אחת, לפרדיקט אחד.
# לכל פרדיקט נוסף בשפה צריך עוד אחת, ולכל פונקציה גם.

CONGRUENCE_FOR_K = (
    "all u all v "
    "((Eq(u,v) and K(u)) -> K(v))"
)


WITH_CONGRUENCE = (
    WITHOUT_CONGRUENCE
    +
    [
        CONGRUENCE_FOR_K
    ]
)


# אותה הנחה עם הסימן =, ובלי שום אקסיומה של שוויון:
# את הסימטריה, הטרנזיטיביות והקונגרואנציה עושה כלל ההיסק.

WITH_EQUALITY_SIGN = [
    "exists f exists l exists g "
    "(F(f) and f = l and f = g "
    "and L(l) and G(g) and K(g))"
]
