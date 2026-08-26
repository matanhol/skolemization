"""מסקנה שלא נובעת מההנחות כפי שנוסחו כאן:

אם y בעלים של x אז x לא בוגד ב y

למה לא נובעת? כי רק טענו שלכל כלב יש בעלים ושהוא נאמן לו.

למעשה אפשר היה לדלג על הבעלים, כתוב רק שהוא נאמן למישהו

השוו ל-owner_never_betrayed_variant, שבו אותה מסקנה כן נובעת.
"""

COMMENTARY_EN = """A conclusion that does not follow from the assumptions as they are phrased here:

if y is the owner of x then x does not betray y

Why does it not follow? Because all we claimed is that every dog has an owner
and that it is loyal to him.

In fact the owner could have been left out altogether, writing only that the dog
is loyal to someone.

Nothing here connects O to F in general: the link is made only for dogs, and only
for the one owner assumption 1 produces, whereas the conclusion quantifies over
every pair. Compare owner_never_betrayed_variant, where the same conclusion does
follow.
"""


from skolemization import prove

from .assumptions import BASE

conclusion = (
    "all x, all y, O(x,y) -> not B(x,y)"
)


if __name__ == "__main__":

    result = prove(
        BASE,
        conclusion
    )
