"""Build ``skolemization.ipynb`` -- the package as one Colab notebook.

The notebook is the shape the original had: **one cell holding the whole
model**, then a cell per example with its Hebrew commentary in a markdown cell
above it.  Nothing here is written by hand, which is the point -- the frozen
``skolemization_example.py`` drifted from the package the moment the package
changed, and a generated notebook cannot::

    python3 build_notebook.py        # from the repo root, after any change

The model cell is the package concatenated in dependency order, with the
relative imports dropped and each module's docstring turned into a banner
comment.  Not one line of logic is rewritten: the module qualifiers the code
uses stay, ``config.py`` becoming ``class config:`` and ``narration``,
``rewrite`` and ``aliases`` each getting a namespace class after their section.
So ``config.MAX_RESOLUTION_STEPS = 400`` still means what the docs say, and the
narration comes out byte-for-byte identical to the package's -- which is the
test that the flattening changed nothing.

The example cells read their assumptions, conclusions and Hebrew straight out
of ``examples/``, so the notebook cannot disagree with the scripts.
"""

import ast
import importlib
import json
import pathlib
import textwrap

import skolemization
from skolemization import config


REPO_ROOT = pathlib.Path(__file__).resolve().parent

PACKAGE = "skolemization"

def notebook_path():

    """Where this build goes -- one notebook per language.

    Hebrew keeps the plain name, since it is the default and what every link
    points at; another language gets a suffix rather than overwriting it.
    """

    if config.LANGUAGE == "he":
        return REPO_ROOT / "skolemization.ipynb"

    return REPO_ROOT / f"skolemization.{config.LANGUAGE}.ipynb"

BANNER_RULE = "# " + "=" * 64


# ================================================================
# READING ORDER
# ================================================================
#
# Dependency order alone would sort the modules alphabetically, which reads
# like nothing.  This is the order a person would read them in -- settings,
# the data model, parsing, the seven steps, then the search -- and the
# topological sort still has the last word, so a module whose dependencies are
# not ready yet simply waits.

READING_ORDER = [
    "config",
    "rewrite",
    "inference",
    "formulas",
    "output",
    "display",
    "signature",
    "substitution",
    "unification",
    "clauses",
    "parsing.aliases",
    "parsing.tokenizer",
    "parsing.parser",
    "steps.implications",
    "steps.nnf",
    "steps.skolemize",
    "steps.forall",
    "steps.cnf",
    "steps.clausify",
    "resolution",
    "factoring",
    "ordering",
    "paramodulation",
    "subsumption",
    "saturation",
    "narration",
    "focus",
    "axioms",
    "search",
    "preprocessing",
    "prover",
    "equivalence",
]


# ================================================================
# WHICH EXAMPLES BECOME CELLS, AND IN WHAT ORDER
# ================================================================
#
# Only the order and the kind of cell live here.  Every value and every word
# of Hebrew is read from the modules themselves.

EXAMPLE_GROUPS = [

    {
        "intro": "examples.dogs.assumptions",
        "examples": [
            ("examples.dogs.betrayer_not_dog", "prove"),
            ("examples.dogs.betrayer_not_dog_per_formula", "prove"),
            ("examples.dogs.betrayer_is_dog", "prove"),
            ("examples.dogs.some_dog_exists", "prove"),
            ("examples.dogs.someone_is_loyal", "prove"),
            ("examples.dogs.owner_never_betrayed", "prove"),
            ("examples.dogs.owner_never_betrayed_variant", "prove"),
        ],
    },

    {
        "intro": "examples.uniqueness.assumptions",
        "examples": [
            ("examples.uniqueness.with_eq_axioms", "prove"),
            ("examples.uniqueness.without_eq_axioms", "prove"),
            ("examples.uniqueness.matching_argument_order", "prove"),
            ("examples.uniqueness.with_paramodulation", "prove"),
            ("examples.uniqueness.with_superposition", "prove"),
        ],
    },

    {
        "intro": "examples.equality.assumptions",
        "examples": [
            ("examples.equality.without_congruence", "prove"),
            ("examples.equality.with_congruence", "prove"),
            ("examples.equality.with_paramodulation", "prove"),
            ("examples.equality.with_superposition", "prove"),
        ],
    },

    {
        "intro": "examples.recursion.assumptions",
        "examples": [
            ("examples.recursion.runaway", "prove"),
            ("examples.recursion.shallowest_first", "prove"),
        ],
    },

    {
        "intro": "examples.equivalence.formulas",
        "examples": [
            ("examples.equivalence.equivalence", "check"),
            ("examples.equivalence.phi1_implies_phi2", "forward"),
            ("examples.equivalence.phi2_implies_phi1", "backward"),
        ],
    },

    {
        "intro": "examples.question8.assumptions",
        "examples": [
            ("examples.question8.pr_and_not_l", "prove"),
        ],
    },

    {
        "intro": "examples.teacher.assumptions",
        "examples": [
            ("examples.teacher.linked_to_every_s", "prove"),
        ],
    },

    {
        "intro": "examples.ceo.assumptions",
        "examples": [
            ("examples.ceo.some_t_is_not_s", "prove"),
        ],
    },
]


# An example whose cell deserves a warning the docstring does not carry -- in
# each language the notebook can be built in, since this note is written here
# rather than read out of the example.

EXTRA_NOTES = {

    "examples.equality.with_congruence": {
        "he": "⚠️ התא הזה רץ 343 צעדים ולוקח כמה דקות.",
        "en": "⚠️ This cell runs for 343 steps and takes a few minutes.",
    },
}


# ================================================================
# READING THE PACKAGE
# ================================================================

def module_files():

    """Every module of the package, keyed by its dotted name.

    ``__init__.py`` files are not modules for our purposes -- they only
    re-export -- but their docstrings are kept separately, as banners.
    """

    modules = {}

    for path in sorted(
        (REPO_ROOT / PACKAGE).rglob("*.py")
    ):

        if path.name == "__init__.py":
            continue

        modules[
            dotted_name(path)
        ] = path

    return modules


def dotted_name(path):

    """``skolemization/steps/nnf.py`` -> ``skolemization.steps.nnf``."""

    relative = path.relative_to(REPO_ROOT)

    return ".".join(
        relative.with_suffix("").parts
    )


def package_of(name):

    """The package a dotted module name lives in."""

    return name.rsplit(".", 1)[0]


def resolve_relative(name, node):

    """What ``from .x import y`` inside ``name`` actually refers to.

    Returns a list of candidate dotted names; a plain ``from . import narration``
    contributes one per imported name, since those names are modules.
    """

    parts = package_of(name).split(".")

    base = parts[: len(parts) - (node.level - 1)] if node.level > 1 else parts

    if node.module is None:

        return [
            ".".join(base + [alias.name])
            for alias in node.names
        ]

    return [
        ".".join(base + node.module.split("."))
    ]


def dependencies(name, tree, modules):

    """The package modules this module needs defined before it.

    A target that is a package rather than a module (``from .parsing import
    Parser``) stands for every module inside it.
    """

    needed = set()

    for node in ast.walk(tree):

        if not isinstance(node, ast.ImportFrom):
            continue

        if not node.level:
            continue

        for target in resolve_relative(
            name,
            node
        ):

            if target in modules:

                needed.add(target)

                continue

            # A subpackage: depend on everything in it.
            inside = {
                other
                for other in modules
                if other.startswith(target + ".")
            }

            if not inside:

                raise ValueError(
                    f"{name}: cannot resolve import of {target}"
                )

            needed |= inside

    needed.discard(name)

    return needed


def reading_rank(name):

    """Where a module belongs in ``READING_ORDER``, unlisted ones last."""

    short = name[len(PACKAGE) + 1:]

    if short in READING_ORDER:

        return (
            READING_ORDER.index(short),
            short
        )

    return (
        len(READING_ORDER),
        short
    )


def ordered_modules():

    """The package sorted so that every module follows what it depends on.

    ``READING_ORDER`` decides between modules that are equally ready, and
    anything it does not name falls to the end alphabetically -- so the
    notebook is byte-identical from one run to the next, and a module added to
    the package still lands in it without being listed anywhere.
    """

    modules = module_files()

    graph = {}

    for name, path in modules.items():

        graph[name] = dependencies(
            name,
            ast.parse(
                path.read_text(
                    encoding="utf-8"
                )
            ),
            modules
        )

    ordered = []

    placed = set()

    while len(ordered) < len(graph):

        ready = sorted(
            (
                name
                for name, needs in graph.items()
                if name not in placed
                and needs <= placed
            ),
            key=reading_rank
        )

        if not ready:

            raise ValueError(
                "import cycle among: "
                + ", ".join(
                    sorted(
                        set(graph) - placed
                    )
                )
            )

        # One at a time, so a module that becomes ready now can still take
        # its place in the reading order ahead of one that was ready already.

        name = ready[0]

        ordered.append(
            (
                name,
                modules[name]
            )
        )

        placed.add(name)

    return ordered


# ================================================================
# TURNING A MODULE INTO A SECTION OF THE CELL
# ================================================================

def commentary_of(tree):

    """An example's commentary, in the language the notebook is being built in.

    Every example carries its teaching text twice: the Hebrew as the module
    docstring, the English as a ``COMMENTARY_EN`` constant beside it.  Under
    ``config.LANGUAGE = "en"`` the constant is used and the docstring ignored;
    a module that has not been given one falls back to the docstring rather
    than losing its commentary, so a half-translated package still builds.
    """

    if config.LANGUAGE == "he":

        return docstring_of(
            tree
        )

    for node in tree.body:

        if not isinstance(
            node,
            ast.Assign
        ):

            continue

        for target in node.targets:

            if (
                isinstance(target, ast.Name)
                and
                target.id == "COMMENTARY_EN"
                and
                isinstance(node.value, ast.Constant)
            ):

                return textwrap.dedent(
                    node.value.value
                ).strip()

    return docstring_of(
        tree
    )


def docstring_of(tree):

    """The module docstring, dedented, or None."""

    if not tree.body:
        return None

    first = tree.body[0]

    if (
        isinstance(first, ast.Expr)
        and
        isinstance(first.value, ast.Constant)
        and
        isinstance(first.value.value, str)
    ):

        return textwrap.dedent(
            first.value.value
        ).strip()

    return None


def banner(title, text=None):

    """A ``# ====`` heading, optionally with commentary under it."""

    lines = [
        BANNER_RULE,
        f"# {title}",
        BANNER_RULE,
    ]

    if text:

        lines.append("#")

        for line in text.splitlines():

            lines.append(
                ("# " + line).rstrip()
            )

    return "\n".join(lines)


def module_style_imports(tree):

    """The names a module imports as modules -- ``from . import narration``.

    ``config`` is left out: it survives the flattening as a class, precisely so
    that ``config.STRATEGY`` keeps working the way the documentation says.
    """

    names = []

    for node in tree.body:

        if (
            isinstance(node, ast.ImportFrom)
            and
            node.level
            and
            node.module is None
        ):

            names += [
                alias.name
                for alias in node.names
                if alias.name != "config"
            ]

    return names


def qualified_uses(modules):

    """Which attributes the package reaches for through a module qualifier.

    ``{"narration": {"step_header", ...}, ...}`` -- the public surface each of
    those modules is actually used through, and so exactly what has to survive
    the flattening.
    """

    used = {
        name: set()
        for name in modules
    }

    for path in module_files().values():

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        for node in ast.walk(tree):

            if (
                isinstance(node, ast.Attribute)
                and
                isinstance(node.value, ast.Name)
                and
                node.value.id in used
            ):

                used[node.value.id].add(node.attr)

    return used


def namespace_class(name, attributes):

    """Put a module qualifier back, once its module has been flattened away.

    ``preprocessing.py`` calls ``narration.rewrites(...)`` while holding a
    local list called ``rewrites``; dropping the qualifier would quietly hand
    the call the list.  So the qualifier stays, as a class whose attributes are
    the flattened functions themselves -- the same trick ``config`` gets, for
    the same reason.
    """

    lines = [
        f"class {name}:",
        "",
        f'    """The flattened {name}.py, still reachable as {name}.x."""',
        "",
    ]

    lines += [
        f"    {attribute} = {attribute}"
        for attribute in sorted(attributes)
    ]

    return "\n".join(lines)


def strip_imports(source, tree):

    """Drop the docstring and every import, keeping everything else verbatim.

    Line spans are removed rather than the tree being unparsed, because the
    comments and the vertical layout are the teaching material.
    """

    lines = source.splitlines()

    dropped = set()

    def drop(node):

        for number in range(
            node.lineno,
            node.end_lineno + 1
        ):

            dropped.add(number)

    first = tree.body[0] if tree.body else None

    if docstring_of(tree) is not None:

        drop(first)

    for node in tree.body:

        if isinstance(
            node,
            (ast.Import, ast.ImportFrom)
        ):

            drop(node)

    kept = [
        line
        for number, line in enumerate(lines, 1)
        if number not in dropped
    ]

    while kept and not kept[0].strip():
        kept.pop(0)

    while kept and not kept[-1].strip():
        kept.pop()

    return "\n".join(kept)


def refuse_aliased_imports(name, tree):

    """An ``import x as y`` inside the package cannot survive flattening.

    Dropping the import leaves the body calling ``y`` while the flat file only
    defines ``x`` -- a NameError in the notebook and nowhere else.  Refuse to
    build rather than ship that.
    """

    for node in tree.body:

        if not isinstance(node, ast.ImportFrom):
            continue

        if not node.level:
            continue

        for alias in node.names:

            if alias.asname:

                raise ValueError(
                    f"{name}: '{alias.name} as {alias.asname}' cannot be "
                    "flattened -- rename the definition instead of aliasing "
                    "the import"
                )


def stdlib_imports(tree):

    """The non-relative imports of a module, as source lines."""

    found = []

    for node in tree.body:

        if isinstance(node, ast.Import):

            for alias in node.names:

                found.append(
                    f"import {alias.name}"
                )

        elif (
            isinstance(node, ast.ImportFrom)
            and
            not node.level
        ):

            names = ", ".join(
                alias.name
                for alias in node.names
            )

            found.append(
                f"from {node.module} import {names}"
            )

    return found


def as_config_class(body, doc):

    """``config.py`` as ``class config:``, so ``config.X`` keeps working.

    With one value overridden: LANGUAGE is set to the language the notebook is
    being built in.  Otherwise an English notebook would carry English
    commentary around a prover still narrating in Hebrew, because config.py is
    copied in verbatim and its default is "he".
    """

    body = body.replace(
        'LANGUAGE = "he"',
        f'LANGUAGE = "{config.LANGUAGE}"'
    )

    quoted = '"""' + doc + '\n"""'

    return "\n".join(
        [
            "class config:",
            "",
            textwrap.indent(
                quoted,
                "    "
            ),
            "",
            textwrap.indent(
                body,
                "    "
            ).replace(
                "\n    \n",
                "\n\n"
            ),
        ]
    )


def subpackage_banner(name, seen):

    """The banner for a subpackage's ``__init__``, the first time it is due."""

    package = package_of(name)

    if (
        package == PACKAGE
        or
        package in seen
    ):

        return None

    seen.add(package)

    init = REPO_ROOT / pathlib.Path(
        *package.split(".")
    ) / "__init__.py"

    doc = docstring_of(
        ast.parse(
            init.read_text(
                encoding="utf-8"
            )
        )
    )

    return banner(
        package.replace(".", "/") + "/",
        doc
    )


def model_cell():

    """The whole package, as the source of a single notebook cell."""

    sections = [
        banner(
            "Educational First-Order Logic Resolution Solver",
            "Generated from skolemization/ by build_notebook.py.\n"
            "Edit the package and regenerate -- not this cell."
        )
    ]

    imports = []

    bodies = []

    seen_packages = set()

    modules = ordered_modules()

    namespaces = qualified_uses(
        sorted(
            {
                short
                for name, path in modules
                for short in module_style_imports(
                    ast.parse(
                        path.read_text(
                            encoding="utf-8"
                        )
                    )
                )
            }
        )
    )

    for name, path in modules:

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source)

        refuse_aliased_imports(
            name,
            tree
        )

        for line in stdlib_imports(tree):

            if line not in imports:

                imports.append(line)

        doc = docstring_of(tree)

        body = strip_imports(
            source,
            tree
        )

        if name == PACKAGE + ".config":

            body = as_config_class(
                body,
                doc
            )

            doc = None

        heading = subpackage_banner(
            name,
            seen_packages
        )

        if heading:

            bodies.append(heading)

        bodies.append(
            banner(
                name.replace(".", "/") + ".py",
                doc
            )
        )

        bodies.append(body)

        short = name.rsplit(".", 1)[-1]

        if short in namespaces:

            bodies.append(
                namespace_class(
                    short,
                    namespaces[short]
                )
            )

    sections.append(
        "\n".join(
            sorted(imports)
        )
    )

    sections.extend(bodies)

    return "\n\n\n".join(sections) + "\n"


# ================================================================
# THE EXAMPLE CELLS
# ================================================================

def example_module(name):

    """Import an example and hand back the module and its parsed source."""

    module = importlib.import_module(name)

    path = pathlib.Path(
        module.__file__
    )

    return (
        module,
        ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )
    )


def imported_constant(module, tree, source_module):

    """The value an example pulls in from its sibling assumptions module."""

    for node in tree.body:

        if (
            isinstance(node, ast.ImportFrom)
            and
            node.level
            and
            node.module == source_module
        ):

            return getattr(
                module,
                node.names[0].name
            )

    raise ValueError(
        f"{module.__name__}: no import from .{source_module}"
    )


def prove_keywords(module, tree):

    """The extra ``prove`` arguments an example passes under ``__main__``.

    An example may name a constant it imported (``EQ_SYMMETRIC``) or write the
    set out in the call (``{"Eq"}``); both have to come back as the value, so
    the cell can restate it.
    """

    extra = {}

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if getattr(node.func, "id", None) != "prove":
            continue

        for keyword in node.keywords:

            if isinstance(
                keyword.value,
                ast.Name
            ):

                extra[keyword.arg] = getattr(
                    module,
                    keyword.value.id
                )

                continue

            extra[keyword.arg] = (
                ast.literal_eval(
                    keyword.value
                )
            )

    return extra


def config_settings(tree):

    """The ``config.NAME = ...`` an example sets before it runs.

    A script can set a flag and walk away; a notebook cell cannot, because the
    namespace outlives it and every cell run afterwards would quietly inherit
    the setting.  So the cell is rendered with the flag put back, and what it
    is put back to is read from ``skolemization/config.py`` itself.
    """

    settings = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:

            if (
                isinstance(target, ast.Attribute)
                and
                isinstance(target.value, ast.Name)
                and
                target.value.id == "config"
            ):

                settings.append(
                    (
                        target.attr,
                        ast.literal_eval(
                            node.value
                        ),
                        getattr(
                            skolemization.config,
                            target.attr
                        )
                    )
                )

    return settings


def string_literal(text):

    """A double-quoted literal; the formulas never contain a quote."""

    return '"' + text + '"'


def render_list(name, values):

    """A vertical list assignment, the way the examples write one.

    An example can have no assumptions at all -- the equality rule needs none --
    and an empty list should read as one.
    """

    if not values:

        return f"{name} = []"

    inner = ",\n".join(
        "    " + string_literal(value)
        for value in values
    )

    return f"{name} = [\n{inner}\n]"


def render_prove(module, tree):

    """An example's cell: its assumptions, its conclusion, and the call."""

    assumptions = imported_constant(
        module,
        tree,
        "assumptions"
    )

    extra = prove_keywords(
        module,
        tree
    )

    call = [
        "result = prove(",
        "    assumptions,",
        "    conclusion" + ("," if extra else ""),
    ]

    for index, (keyword, value) in enumerate(
        extra.items()
    ):

        relations = ", ".join(
            string_literal(item)
            for item in sorted(value)
        )

        call.append(
            f"    {keyword}={{{relations}}}"
            + (
                ","
                if index < len(extra) - 1
                else ""
            )
        )

    call.append(")")

    settings = config_settings(tree)

    blocks = [
        f"config.{name} = {chosen!r}"
        for name, chosen, _ in settings
    ]

    blocks += [
        render_list(
            "assumptions",
            assumptions
        ),
        "conclusion = (\n    "
        + string_literal(module.conclusion)
        + "\n)",
        "\n".join(call),
    ]

    blocks += [
        f"config.{name} = {default!r}"
        for name, _, default in settings
    ]

    return "\n\n".join(blocks) + "\n"


def render_equivalence(kind):

    """A cell for one of the equivalence examples.

    Self-contained like the others: it restates both formulas rather than
    leaning on a cell above it.
    """

    formulas = importlib.import_module(
        "examples.equivalence.formulas"
    )

    calls = {
        "check": "result = question.check()",
        "forward": "result = question.forward()",
        "backward": "result = question.backward()",
    }

    return "\n\n".join(
        [
            "phi1 = (\n    "
            + string_literal(formulas.PHI1)
            + "\n)",
            "phi2 = (\n    "
            + string_literal(formulas.PHI2)
            + "\n)",
            "question = Equivalence(\n    phi1,\n    phi2\n)",
            calls[kind],
        ]
    ) + "\n"


def example_cells():

    """Every example, as markdown-then-code pairs."""

    cells = []

    for group in EXAMPLE_GROUPS:

        intro, intro_tree = example_module(
            group["intro"]
        )

        cells.append(
            markdown_cell(
                commentary_of(intro_tree)
            )
        )

        for name, kind in group["examples"]:

            module, tree = example_module(name)

            text = commentary_of(tree)

            if name in EXTRA_NOTES:

                text = (
                    text
                    + "\n\n"
                    + EXTRA_NOTES[name][
                        config.LANGUAGE
                    ]
                )

            cells.append(
                markdown_cell(text)
            )

            cells.append(
                code_cell(
                    render_prove(
                        module,
                        tree
                    )
                    if kind == "prove"
                    else render_equivalence(kind)
                )
            )

    return cells


# ================================================================
# NOTEBOOK JSON
# ================================================================

def source_lines(text):

    """Notebook cells store source as a list of newline-terminated lines."""

    lines = text.splitlines(True)

    return lines or [""]


def keep_line_breaks(text):

    """Make markdown respect the layout the docstring was written in.

    The commentary puts one thought, or one formula, on a line; markdown would
    reflow consecutive lines into a paragraph and lose that.  Two trailing
    spaces is markdown's hard line break.
    """

    lines = text.splitlines()

    kept = []

    for index, line in enumerate(lines):

        following = (
            lines[index + 1]
            if index + 1 < len(lines)
            else ""
        )

        kept.append(
            line + "  "
            if line.strip()
            and following.strip()
            else line
        )

    return "\n".join(kept)


def markdown_cell(text):

    """A markdown cell holding the Hebrew commentary."""

    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines(
            keep_line_breaks(text)
        ),
    }


def code_cell(text):

    """An unexecuted code cell."""

    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines(text),
    }


def notebook():

    """The finished notebook: the title, the model, then the examples."""

    package_doc = docstring_of(
        ast.parse(
            (
                REPO_ROOT
                / PACKAGE
                / "__init__.py"
            ).read_text(
                encoding="utf-8"
            )
        )
    )

    cells = [
        markdown_cell(
            "# Skolemization\n\n"
            + package_doc
        ),
        code_cell(
            model_cell()
        ),
    ]

    cells.extend(
        example_cells()
    )

    return {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": cells,
    }


def main():

    """Write the notebook, and say how big it came out."""

    path = notebook_path()

    path.write_text(
        json.dumps(
            notebook(),
            ensure_ascii=False,
            indent=1
        ) + "\n",
        encoding="utf-8"
    )

    print(
        f"wrote {path.relative_to(REPO_ROOT)} "
        f"({config.LANGUAGE})"
    )


if __name__ == "__main__":

    main()
