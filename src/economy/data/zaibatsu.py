"""Zaibatsu (family corporation) definitions."""

from src.economy.core.types import ZaibatsuDef

ZAIBATSU: list[ZaibatsuDef] = [
    ZaibatsuDef(
        id=0, name="Igwe Industries",
        controlled_commodities=[26, 15, 28, 33],
        controlled_lgas=[],
        efficiency_bonus=0.25,
        ethnic_affiliation="igbo",
    ),
    ZaibatsuDef(
        id=1, name="Danjuma Group",
        controlled_commodities=[12, 21],
        controlled_lgas=[],
        efficiency_bonus=0.20,
        ethnic_affiliation="hausa_fulani",
    ),
    ZaibatsuDef(
        id=2, name="BUA Group",
        controlled_commodities=[27, 16, 23, 35],
        controlled_lgas=[],
        efficiency_bonus=0.20,
        ethnic_affiliation="mixed",
    ),
    ZaibatsuDef(
        id=3, name="IDA Corporation",
        controlled_commodities=[29, 26],
        controlled_lgas=[],
        efficiency_bonus=0.30,
        ethnic_affiliation="yoruba",
    ),
    ZaibatsuDef(
        id=4, name="Deltel",
        controlled_commodities=[31, 26],
        controlled_lgas=[],
        efficiency_bonus=0.25,
        ethnic_affiliation="naijin",
    ),
]

ZAIBATSU_BY_ID: dict[int, ZaibatsuDef] = {z.id: z for z in ZAIBATSU}
ZAIBATSU_BY_NAME: dict[str, ZaibatsuDef] = {z.name: z for z in ZAIBATSU}
