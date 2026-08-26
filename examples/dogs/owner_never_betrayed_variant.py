"""אבל אם ננסח את ההנחות באופן שונה, זה כן ינבע

לכל כלב יש בעלים

אם y בעלים של x אז x נאמן ל y

כל יתר ההנחות כמו קודם

זהו המקרה היחיד כאן שבו ההנחות עצמן שונות
(OWNERSHIP_VARIANT ולא BASE).
"""

COMMENTARY_EN = """But if we phrase the assumptions differently, it does follow

every dog has an owner

if y is the owner of x then x is loyal to y

all the rest of the assumptions as before

The whole difference is that second assumption: it ties ownership to loyalty for
every pair, not just for a dog and the one owner it was handed. Chained with
"loyal implies does not betray", O(x,y) now reaches ¬B(x,y) directly.

This is the only case here where the assumptions themselves differ
(OWNERSHIP_VARIANT rather than BASE).
"""


from skolemization import prove

from .assumptions import OWNERSHIP_VARIANT

conclusion = (
    "all x, all y, O(x,y) -> not B(x,y)"
)


if __name__ == "__main__":

    result = prove(
        OWNERSHIP_VARIANT,
        conclusion
    )
