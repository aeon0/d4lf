"""Leaf, thread-safe state shared by the overlay lifecycle and renderer."""

import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.overlay.widget.widget import BossTimerOverlay


@dataclass
class _CurrentOverlay:
    overlay: BossTimerOverlay | None = None


_CURRENT = _CurrentOverlay()
_OVERLAY_LOCK = threading.RLock()


def get_overlay() -> BossTimerOverlay | None:
    """Return the currently composed overlay, if one exists."""
    with _OVERLAY_LOCK:
        return _CURRENT.overlay


def set_overlay(overlay: BossTimerOverlay) -> None:
    """Publish an overlay after its UI object has been constructed."""
    with _OVERLAY_LOCK:
        _CURRENT.overlay = overlay


def clear_overlay(overlay: BossTimerOverlay | None = None) -> None:
    """Clear the current overlay, preserving a newer replacement if present."""
    with _OVERLAY_LOCK:
        if overlay is None or _CURRENT.overlay is overlay:
            _CURRENT.overlay = None


def is_open() -> bool:
    """Return whether an overlay has been composed."""
    return get_overlay() is not None
