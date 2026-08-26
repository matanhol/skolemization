"""3. אותה שאלה, עם הסימן = וכלל היסק במקום אקסיומות.

ההנחה היא ההנחה של השאלה, וזהו:

אין רפלקסיביות, אין סימטריה, אין טרנזיטיביות, ואין קונגרואנציה.

Paramodulation מציב שווה בשווה בתוך האיברים עצמם, ולכן הוא עושה את
עבודתן של שלוש התכונות **וגם** של הקונגרואנציה, לכל פרדיקט ולכל
פונקציה בשפה בבת אחת -- כאן זה K, בלי שאיש כתב עליו אקסיומה.

ההוכחה עצמה קצרה: f = l מציב את f בתוך f = g ונותן l = g; אחר כך
l = g מציב בתוך K(g) ונותן K(l); ומכאן שלוש רזולוציות סוגרות.

16 צעדים, לעומת 343 בדרך של האקסיומות.

האקסיומה היחידה שמתווספת היא x = x, והסולבר מוסיף אותה לבד ומסביר למה.
"""

COMMENTARY_EN = """3. The same question, with the sign = and an inference rule instead of axioms.

The assumption is the assumption of the problem, and that is the whole of
it:

no reflexivity, no symmetry, no transitivity, and no congruence.

Paramodulation substitutes equals for equals inside the terms themselves,
and therefore does the work of all three properties **as well as** that of
congruence, for every predicate and every function in the language at once
-- here that is K, and nobody wrote an axiom about it.

The proof itself is short: f = l substitutes for f inside f = g and yields
l = g; then l = g substitutes inside K(g) and yields K(l); and from there
three resolutions close it.

16 steps, against 343 by way of the axioms.

The only axiom that gets added is x = x, and the solver adds it itself and
explains why.
"""


from skolemization import (
    config,
    prove,
)

from .assumptions import WITH_EQUALITY_SIGN

conclusion = (
    "exists x exists y "
    "(L(x) and G(y) and x = y and K(x))"
)


if __name__ == "__main__":

    config.EQUALITY_RULE = "paramodulation"
    config.SHOW_FULL_KB_EACH_STEP = True

    result = prove(
        WITH_EQUALITY_SIGN,
        conclusion
    )
