"""כיוון 2:  φ2 ⊨ φ1"""

COMMENTARY_EN = """Direction 2:  φ2 ⊨ φ1"""


from .question import question


def check():

    """Run only the second direction."""

    return question().backward()


if __name__ == "__main__":

    check()
