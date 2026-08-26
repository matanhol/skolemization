"""כיוון 1:  φ1 ⊨ φ2"""

COMMENTARY_EN = """Direction 1:  φ1 ⊨ φ2"""


from .question import question


def check():

    """Run only the first direction."""

    return question().forward()


if __name__ == "__main__":

    check()
