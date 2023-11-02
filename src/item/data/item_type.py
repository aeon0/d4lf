from enum import Enum


class ItemType(Enum):
    # Armor
    Helm = "helm"
    Armor = "chest armor"
    Legs = "pants"
    Gloves = "gloves"
    Boots = "boots"
    # Jewelry
    Ring = "ring"
    Amulet = "amulet"
    # Weapons
    Axe = "axe"
    Axe2H = "two-handed axe"
    Sword = "sword"
    Sword2H = "two-handed sword"
    Mace = "mace"
    Mace2H = "two-handed mace"
    Scythe = "scythe"
    Scythe2H = "two-handed scythe"
    Bow = "bow"
    Bracers = "bracers"
    Crossbow = "crossbow"
    Dagger = "dagger"
    Polearm = "polearm"
    Shield = "shield"
    Staff = "staff"
    Wand = "wand"
    Offhand = "offhand"
    Totem = "totem"
    Focus = "focus"
