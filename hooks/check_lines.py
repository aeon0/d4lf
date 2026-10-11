# /// script
# requires-python = ">=3.15"
# ///

"""Check that Python files stay within the maximum number of code lines."""

import tokenize
from pathlib import Path

ROOT = Path(__file__).parents[1]
DIRS = [ROOT / "src", ROOT / "tests"]
MAX_LINES = 300

NON_CODE_TOKEN_TYPES = frozenset(
    {
        tokenize.COMMENT,
        tokenize.DEDENT,
        tokenize.ENCODING,
        tokenize.ENDMARKER,
        tokenize.FSTRING_END,
        tokenize.FSTRING_MIDDLE,
        tokenize.FSTRING_START,
        tokenize.INDENT,
        tokenize.NEWLINE,
        tokenize.NL,
        tokenize.STRING,
    }
)


def count_code_lines(file: Path) -> int:
    """Count physical lines containing Python tokens outside comments and strings."""
    code_lines = 0
    last_code_line = -1

    with file.open("rb") as source:
        for token in tokenize.tokenize(source.readline):
            if token.type not in NON_CODE_TOKEN_TYPES and token.start[0] != last_code_line:
                code_lines += 1
                last_code_line = token.start[0]

    return code_lines


def main() -> int:
    violations: list[tuple[Path, int]] = []
    errors: list[tuple[Path, Exception]] = []

    for directory in DIRS:
        for file in directory.glob("**/*.py"):
            try:
                lines = count_code_lines(file)
            except (OSError, SyntaxError, tokenize.TokenError) as error:
                errors.append((file, error))
                continue

            if lines > MAX_LINES:
                violations.append((file, lines))

    for file, error in errors:
        print(f"Could not tokenize {file}: {error}")

    if violations:
        print(f"Python files must not exceed {MAX_LINES} code lines:\n")
        for file, lines in violations:
            print(f"  {file}: {lines} code lines")

    return 1 if violations or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
