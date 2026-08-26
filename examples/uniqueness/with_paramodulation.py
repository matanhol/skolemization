"""אותה שאלה (3 סעיף א), אבל בלי אף אקסיומה של שוויון.

כאן כותבים

x = y

ולא Eq(x,y), ואת השוויון מטפל **כלל היסק** ולא אקסיומות:

Paramodulation -- הצבת שווה בשווה בתוך פסוקית.

למה זה עדיף?

שלוש האקסיומות (רפלקסיביות, סימטריה, טרנזיטיביות) הופכות את Eq
ליחס שקילות בלבד. שוויון דורש גם קונגרואנציה:

אם x = y אז לכל פרדיקט P מתקיים P(x) -> P(y),

ולכל פונקציה f מתקיים f(x) = f(y).

כלומר צריך אקסיומה לכל פרדיקט ולכל פונקציה בשפה --
כולל פונקציות ה-Skolem שנוצרות בשלב 4.

כלל ההיסק מחליף את כולן בבת אחת, כי הוא מציב בתוך האיברים עצמם.

האקסיומה היחידה שנשארת היא x = x, והסולבר מוסיף אותה לבד.

ראו גם with_superposition, שבו אותו כלל מוגבל לפי סדר איברים.
"""

COMMENTARY_EN = """The same question (3a), but with no equality axiom at all.

Here one writes

x = y

rather than Eq(x,y), and equality is handled by an **inference rule**
instead of axioms:

Paramodulation -- substituting equals for equals inside a clause.

Why is that better?

The three axioms (reflexivity, symmetry, transitivity) make Eq no more
than an equivalence relation. Equality also demands congruence:

if x = y then for every predicate P we have P(x) -> P(y),

and for every function f we have f(x) = f(y).

That means one axiom for every predicate and every function in the
language -- the Skolem functions invented in step 4 included.

The inference rule replaces the whole family in one stroke, because it
substitutes inside the terms themselves.

The only axiom left is x = x, and the solver adds that one by itself.

See also with_superposition, where the same rule is restricted by an
ordering on terms.
"""


from skolemization import (
    config,
    prove,
)

from .assumptions import WITH_EQUALITY_SIGN

conclusion = (
    "exists x "
    "(P(x) and "
    "(all y (P(y) -> y = x)))"
)


if __name__ == "__main__":

    config.EQUALITY_RULE = "paramodulation"

    result = prove(
        WITH_EQUALITY_SIGN,
        conclusion
    )
