"""מסקנה שלא נובעת מההנחות כפי שנוסחו כאן:

אם y בעלים של x אז x לא בוגד ב y

למה לא נובעת? כי רק טענו שלכל כלב יש בעלים ושהוא נאמן לו.

למעשה אפשר היה לדלג על הבעלים, כתוב רק שהוא נאמן למישהו

השוו ל-owner_never_betrayed_variant, שבו אותה מסקנה כן נובעת.
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
