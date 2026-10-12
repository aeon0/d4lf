from typing import TYPE_CHECKING

import pytest

import hooks.check_lines as check_lines_module
from hooks.check_lines import MAX_LINES, count_code_lines, main

if TYPE_CHECKING:
    from pathlib import Path


def _write(tmp_path: Path, source: str, name: str = "module.py") -> Path:
    file = tmp_path / name
    file.write_text(source, encoding="utf-8")
    return file


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param("# comment\n\n# another\n", 0, id="comments_and_blank_lines"),
        pytest.param("x = 1  # trailing comment\n", 1, id="code_with_trailing_comment"),
        pytest.param('"""Docstring\n\nspanning lines\n"""\n', 0, id="standalone_multiline_string"),
        pytest.param('x = """\na\nb\n"""\n', 1, id="assigned_multiline_string"),
        pytest.param('f"{x}"\n', 1, id="fstring_expression"),
        pytest.param('f"plain text"\n', 0, id="fstring_without_expression"),
        pytest.param("a = 1; b = 2; c = a + b\n", 1, id="multiple_tokens_on_one_line"),
        pytest.param("x = (\n    1,\n    2,\n)\n", 4, id="bracket_continuation"),
    ],
)
def test_count_code_lines(tmp_path: Path, source: str, expected: int) -> None:
    assert count_code_lines(_write(tmp_path, source)) == expected


@pytest.mark.parametrize(("line_count", "expected"), [(MAX_LINES, 0), (MAX_LINES + 1, 1)])
def test_main_line_limit_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, line_count: int, expected: int
) -> None:
    _write(tmp_path, "".join(f"x{i} = {i}\n" for i in range(line_count)))
    monkeypatch.setattr(check_lines_module, "DIRS", [tmp_path])

    assert main() == expected


def test_main_ignores_non_code_lines_for_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path, "# comment\n" * (MAX_LINES + 1) + "x = 1\n")
    monkeypatch.setattr(check_lines_module, "DIRS", [tmp_path])

    assert main() == 0


def test_main_fails_on_incomplete_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path, "x = (\n    1,\n")
    monkeypatch.setattr(check_lines_module, "DIRS", [tmp_path])

    assert main() == 1


def test_main_fails_on_unreadable_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(tmp_path, "x = 1\n")
    monkeypatch.setattr(check_lines_module, "DIRS", [tmp_path])

    def raise_os_error(_file: Path) -> int:
        msg = "permission denied"
        raise OSError(msg)

    monkeypatch.setattr(check_lines_module, "count_code_lines", raise_os_error)

    assert main() == 1
