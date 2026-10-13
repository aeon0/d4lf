import pytest
from pydantic import ValidationError

from src.settings.models.core import AdvancedOptionsModel, SettingsCategory


def test_settings_categories_are_stable_public_values() -> None:
    assert SettingsCategory.LOOT.value == "📦 Loot Behavior"
    assert SettingsCategory.HOTKEYS.value == "⌨️ Hotkeys"


def test_advanced_options_reject_duplicate_hotkeys() -> None:
    with pytest.raises(ValidationError, match="unique"):
        AdvancedOptionsModel(exit_key="f1", run_filter="f1")


def test_advanced_options_accept_fast_vision_coordinates() -> None:
    model = AdvancedOptionsModel(fast_vision_mode_coordinates="12,34")
    assert model.fast_vision_mode_coordinates == (12, 34)


@pytest.mark.parametrize(("configured", "expected"), [(None, 10), ("0", 0), ("2", 2), (3, 3)])
def test_advanced_options_parse_max_missing_affixes_shown(configured: str | int | None, expected: int) -> None:
    model = AdvancedOptionsModel() if configured is None else AdvancedOptionsModel(max_missing_affixes_shown=configured)
    assert model.max_missing_affixes_shown == expected


def test_advanced_options_reject_negative_max_missing_affixes_shown() -> None:
    with pytest.raises(ValidationError, match="greater than zero"):
        AdvancedOptionsModel(max_missing_affixes_shown="-1")
