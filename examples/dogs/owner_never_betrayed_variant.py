"""אבל אם ננסח את ההנחות באופן שונה, זה כן ינבע

לכל כלב יש בעלים

אם y בעלים של x אז x נאמן ל y

כל יתר ההנחות כמו קודם

זהו המקרה היחיד כאן שבו ההנחות עצמן שונות
(OWNERSHIP_VARIANT ולא BASE).
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
