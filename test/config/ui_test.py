import pytest
from natsort import natsorted

from config.ui import ResManager, COLORS


@pytest.mark.parametrize("res", natsorted(ResManager().transformers), ids=natsorted(ResManager().transformers.keys()))
def test_transformation(res):
    if res == "1920x1080":
        return
    pos1 = ResManager().pos
    ResManager().set_resolution(res)
    pos2 = ResManager().pos
    assert pos1 != pos2


def test_colors():
    assert COLORS is not None
