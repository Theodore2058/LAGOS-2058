"""Load example parties from examples/run_election.py."""

import sys
import importlib
from pathlib import Path

from api.schemas.party import PartySchema

# Default colors for parties
PARTY_COLORS = [
    "#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6",
    "#ec4899", "#06b6d4", "#f97316", "#14b8a6", "#6366f1",
    "#d946ef", "#84cc16", "#0ea5e9", "#e11d48",
    "#a855f7", "#65a30d", "#0891b2", "#dc2626",
]


def load_example_parties() -> list[PartySchema]:
    """Dynamically load PARTIES from examples/run_election.py."""
    examples_dir = Path(__file__).parent.parent.parent / "examples"
    sys.path.insert(0, str(examples_dir.parent / "src"))
    sys.path.insert(0, str(examples_dir))

    spec = importlib.util.spec_from_file_location("run_election_example", examples_dir / "run_election.py")
    mod = importlib.util.module_from_spec(spec)

    # Suppress logging and the main execution
    import logging
    logging.disable(logging.CRITICAL)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    finally:
        logging.disable(logging.NOTSET)

    parties = getattr(mod, "PARTIES", [])
    result = []
    for i, p in enumerate(parties):
        positions = p.positions.tolist() if hasattr(p.positions, 'tolist') else list(p.positions)
        strongholds = None
        if p.regional_strongholds:
            strongholds = {str(k): v for k, v in p.regional_strongholds.items()}

        result.append(PartySchema(
            name=p.name,
            full_name=p.name,
            positions=positions,
            valence=p.valence,
            leader_ethnicity=p.leader_ethnicity,
            religious_alignment=p.religious_alignment,
            demographic_coefficients=p.demographic_coefficients,
            regional_strongholds=strongholds,
            economic_positioning=p.economic_positioning,
            color=PARTY_COLORS[i % len(PARTY_COLORS)],
        ))

    return result
