import pytest
import cv2
from item.read_descr import read_descr
from item.data.rarity import ItemRarity


@pytest.mark.parametrize(
    "filename,rarity",
    [
        ("item_dscr_1.png", ItemRarity.Rare),
        ("item_dscr_2.png", ItemRarity.Legendary),
        ("item_dscr_3.png", ItemRarity.Rare),
        ("item_dscr_4.png", ItemRarity.Rare),
        ("issue.png", ItemRarity.Rare),
    ],
)
def test_read_descr(filename, rarity):
    img = cv2.imread(f"test/assets/ocr/{filename}")
    res = read_descr(rarity, img)
