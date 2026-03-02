"""
Ethnic affinity matrix for the LAGOS-2058 election engine.

Affinity values range 0.0 to 1.0.  Diagonal = 1.0 (perfect in-group affinity).
Values represent estimated cultural-political proximity between an LGA voter's
ethnic identity and a party leader's ethnic background.

These are illustrative calibration starting values; the matrix is designed to be
overridable by passing a custom dict of dicts to the accessor functions.

Groups modelled:
  Core cluster labels (15 named + 2 catch-alls):
  - Hausa, Fulani, Hausa-Fulani Undiff   → northern Muslim cluster
  - Yoruba                               → southwestern
  - Igbo                                 → southeastern
  - Ijaw                                 → Niger Delta
  - Kanuri                               → northeast / Borno basin
  - Tiv                                  → Middle Belt
  - Nupe                                 → Niger state / Middle Belt
  - Edo                                  → south-south / Benin
  - Ibibio                               → southeast coastal
  - Niger Delta Minorities               → Rivers / Delta / Bayelsa clusters
  - Middle Belt Minorities               → Plateau / Benue / Nassarawa clusters
  - Pada                                 → speculative 2058 synthetic group
  - Naijin                               → speculative 2058 synthetic group
  - Other-North                          → catch-all northern small groups
  - Other-South                          → catch-all southern small groups
"""

from __future__ import annotations

import numpy as np
from typing import Optional

# ---------------------------------------------------------------------------
# Group definitions and aliases
# ---------------------------------------------------------------------------

# Canonical group names (order doesn't matter — matrix is keyed by name)
ETHNIC_GROUPS: list[str] = [
    "Hausa",
    "Fulani",
    "Hausa-Fulani Undiff",
    "Yoruba",
    "Igbo",
    "Ijaw",
    "Kanuri",
    "Tiv",
    "Nupe",
    "Edo",
    "Ibibio",
    "Niger Delta Minorities",
    "Middle Belt Minorities",
    "Pada",
    "Naijin",
    "Other-North",
    "Other-South",
]

# Aliases map non-canonical names → canonical
_ALIASES: dict[str, str] = {
    "hausa": "Hausa",
    "fulani": "Fulani",
    "hausa-fulani": "Hausa-Fulani Undiff",
    "hausa fulani": "Hausa-Fulani Undiff",
    "hausa_fulani_undiff": "Hausa-Fulani Undiff",
    "yoruba": "Yoruba",
    "igbo": "Igbo",
    "ibo": "Igbo",
    "ijaw": "Ijaw",
    "kanuri": "Kanuri",
    "tiv": "Tiv",
    "nupe": "Nupe",
    "edo": "Edo",
    "edo bini": "Edo",
    "ibibio": "Ibibio",
    "niger delta": "Niger Delta Minorities",
    "niger_delta_minorities": "Niger Delta Minorities",
    "middle belt": "Middle Belt Minorities",
    "middle_belt_minorities": "Middle Belt Minorities",
    "pada": "Pada",
    "naijin": "Naijin",
    "other-north": "Other-North",
    "other north": "Other-North",
    "other-south": "Other-South",
    "other south": "Other-South",
    "other": "Other-South",  # default: map generic Other to Other-South
}


def _resolve(group: str) -> str:
    """Resolve a group name to its canonical form."""
    canonical = _ALIASES.get(group.lower().strip())
    if canonical:
        return canonical
    if group in ETHNIC_GROUPS:
        return group
    # Partial-match fallback
    lower = group.lower()
    if any(k in lower for k in ["north", "hausa", "kanuri", "fulani", "nupe", "tiv"]):
        return "Other-North"
    return "Other-South"


# ---------------------------------------------------------------------------
# Default affinity matrix
# ---------------------------------------------------------------------------
# Rows = voter group, columns = leader group. Values 0.0–1.0. Diagonal = 1.0.
# Key design choices:
#   - Hausa/Fulani/HF-Undiff cluster: very high mutual affinity (0.85–1.0)
#   - Yoruba-Igbo moderate cross-affinity (0.30)
#   - Pada: moderate with Yoruba (0.40), Igbo (0.35), Naijin (0.50)
#   - Naijin: cosmopolitan moderate-affinity with everyone (0.30–0.55)
#   - Cross-regional (Hausa-Igbo, Hausa-Yoruba): low (0.05–0.15)
#   - Niger Delta minorities cluster: 0.50–0.65 mutual
#   - Middle Belt groups: moderate cross-affinity (0.35–0.55)

_DEFAULT_MATRIX: dict[str, dict[str, float]] = {
    "Hausa": {
        "Hausa": 1.00, "Fulani": 0.88, "Hausa-Fulani Undiff": 0.90,
        "Yoruba": 0.10, "Igbo": 0.05, "Ijaw": 0.05, "Kanuri": 0.45,
        "Tiv": 0.15, "Nupe": 0.40, "Edo": 0.08, "Ibibio": 0.05,
        "Niger Delta Minorities": 0.05, "Middle Belt Minorities": 0.20,
        "Pada": 0.10, "Naijin": 0.30, "Other-North": 0.55, "Other-South": 0.08,
    },
    "Fulani": {
        "Hausa": 0.88, "Fulani": 1.00, "Hausa-Fulani Undiff": 0.92,
        "Yoruba": 0.10, "Igbo": 0.05, "Ijaw": 0.05, "Kanuri": 0.40,
        "Tiv": 0.12, "Nupe": 0.38, "Edo": 0.08, "Ibibio": 0.05,
        "Niger Delta Minorities": 0.05, "Middle Belt Minorities": 0.18,
        "Pada": 0.10, "Naijin": 0.28, "Other-North": 0.52, "Other-South": 0.08,
    },
    "Hausa-Fulani Undiff": {
        "Hausa": 0.90, "Fulani": 0.92, "Hausa-Fulani Undiff": 1.00,
        "Yoruba": 0.10, "Igbo": 0.05, "Ijaw": 0.05, "Kanuri": 0.42,
        "Tiv": 0.13, "Nupe": 0.39, "Edo": 0.08, "Ibibio": 0.05,
        "Niger Delta Minorities": 0.05, "Middle Belt Minorities": 0.19,
        "Pada": 0.10, "Naijin": 0.29, "Other-North": 0.53, "Other-South": 0.08,
    },
    "Yoruba": {
        "Hausa": 0.10, "Fulani": 0.10, "Hausa-Fulani Undiff": 0.10,
        "Yoruba": 1.00, "Igbo": 0.30, "Ijaw": 0.22, "Kanuri": 0.08,
        "Tiv": 0.20, "Nupe": 0.18, "Edo": 0.35, "Ibibio": 0.25,
        "Niger Delta Minorities": 0.20, "Middle Belt Minorities": 0.22,
        "Pada": 0.40, "Naijin": 0.45, "Other-North": 0.10, "Other-South": 0.40,
    },
    "Igbo": {
        "Hausa": 0.05, "Fulani": 0.05, "Hausa-Fulani Undiff": 0.05,
        "Yoruba": 0.30, "Igbo": 1.00, "Ijaw": 0.35, "Kanuri": 0.06,
        "Tiv": 0.22, "Nupe": 0.15, "Edo": 0.40, "Ibibio": 0.45,
        "Niger Delta Minorities": 0.38, "Middle Belt Minorities": 0.25,
        "Pada": 0.35, "Naijin": 0.42, "Other-North": 0.06, "Other-South": 0.42,
    },
    "Ijaw": {
        "Hausa": 0.05, "Fulani": 0.05, "Hausa-Fulani Undiff": 0.05,
        "Yoruba": 0.22, "Igbo": 0.35, "Ijaw": 1.00, "Kanuri": 0.06,
        "Tiv": 0.18, "Nupe": 0.12, "Edo": 0.38, "Ibibio": 0.42,
        "Niger Delta Minorities": 0.65, "Middle Belt Minorities": 0.20,
        "Pada": 0.28, "Naijin": 0.38, "Other-North": 0.06, "Other-South": 0.40,
    },
    "Kanuri": {
        "Hausa": 0.45, "Fulani": 0.40, "Hausa-Fulani Undiff": 0.42,
        "Yoruba": 0.08, "Igbo": 0.06, "Ijaw": 0.06, "Kanuri": 1.00,
        "Tiv": 0.15, "Nupe": 0.35, "Edo": 0.08, "Ibibio": 0.06,
        "Niger Delta Minorities": 0.06, "Middle Belt Minorities": 0.20,
        "Pada": 0.12, "Naijin": 0.30, "Other-North": 0.60, "Other-South": 0.08,
    },
    "Tiv": {
        "Hausa": 0.15, "Fulani": 0.12, "Hausa-Fulani Undiff": 0.13,
        "Yoruba": 0.20, "Igbo": 0.22, "Ijaw": 0.18, "Kanuri": 0.15,
        "Tiv": 1.00, "Nupe": 0.42, "Edo": 0.25, "Ibibio": 0.28,
        "Niger Delta Minorities": 0.22, "Middle Belt Minorities": 0.60,
        "Pada": 0.25, "Naijin": 0.38, "Other-North": 0.30, "Other-South": 0.28,
    },
    "Nupe": {
        "Hausa": 0.40, "Fulani": 0.38, "Hausa-Fulani Undiff": 0.39,
        "Yoruba": 0.18, "Igbo": 0.15, "Ijaw": 0.12, "Kanuri": 0.35,
        "Tiv": 0.42, "Nupe": 1.00, "Edo": 0.20, "Ibibio": 0.18,
        "Niger Delta Minorities": 0.15, "Middle Belt Minorities": 0.50,
        "Pada": 0.20, "Naijin": 0.35, "Other-North": 0.50, "Other-South": 0.18,
    },
    "Edo": {
        "Hausa": 0.08, "Fulani": 0.08, "Hausa-Fulani Undiff": 0.08,
        "Yoruba": 0.35, "Igbo": 0.40, "Ijaw": 0.38, "Kanuri": 0.08,
        "Tiv": 0.25, "Nupe": 0.20, "Edo": 1.00, "Ibibio": 0.50,
        "Niger Delta Minorities": 0.55, "Middle Belt Minorities": 0.28,
        "Pada": 0.30, "Naijin": 0.40, "Other-North": 0.08, "Other-South": 0.48,
    },
    "Ibibio": {
        "Hausa": 0.05, "Fulani": 0.05, "Hausa-Fulani Undiff": 0.05,
        "Yoruba": 0.25, "Igbo": 0.45, "Ijaw": 0.42, "Kanuri": 0.06,
        "Tiv": 0.28, "Nupe": 0.18, "Edo": 0.50, "Ibibio": 1.00,
        "Niger Delta Minorities": 0.60, "Middle Belt Minorities": 0.30,
        "Pada": 0.30, "Naijin": 0.40, "Other-North": 0.06, "Other-South": 0.50,
    },
    "Niger Delta Minorities": {
        "Hausa": 0.05, "Fulani": 0.05, "Hausa-Fulani Undiff": 0.05,
        "Yoruba": 0.20, "Igbo": 0.38, "Ijaw": 0.65, "Kanuri": 0.06,
        "Tiv": 0.22, "Nupe": 0.15, "Edo": 0.55, "Ibibio": 0.60,
        "Niger Delta Minorities": 1.00, "Middle Belt Minorities": 0.25,
        "Pada": 0.28, "Naijin": 0.38, "Other-North": 0.06, "Other-South": 0.50,
    },
    "Middle Belt Minorities": {
        "Hausa": 0.20, "Fulani": 0.18, "Hausa-Fulani Undiff": 0.19,
        "Yoruba": 0.22, "Igbo": 0.25, "Ijaw": 0.20, "Kanuri": 0.20,
        "Tiv": 0.60, "Nupe": 0.50, "Edo": 0.28, "Ibibio": 0.30,
        "Niger Delta Minorities": 0.25, "Middle Belt Minorities": 1.00,
        "Pada": 0.30, "Naijin": 0.38, "Other-North": 0.40, "Other-South": 0.28,
    },
    "Pada": {
        "Hausa": 0.10, "Fulani": 0.10, "Hausa-Fulani Undiff": 0.10,
        "Yoruba": 0.40, "Igbo": 0.35, "Ijaw": 0.28, "Kanuri": 0.12,
        "Tiv": 0.25, "Nupe": 0.20, "Edo": 0.30, "Ibibio": 0.30,
        "Niger Delta Minorities": 0.28, "Middle Belt Minorities": 0.30,
        "Pada": 1.00, "Naijin": 0.50, "Other-North": 0.15, "Other-South": 0.40,
    },
    "Naijin": {
        "Hausa": 0.30, "Fulani": 0.28, "Hausa-Fulani Undiff": 0.29,
        "Yoruba": 0.45, "Igbo": 0.42, "Ijaw": 0.38, "Kanuri": 0.30,
        "Tiv": 0.38, "Nupe": 0.35, "Edo": 0.40, "Ibibio": 0.40,
        "Niger Delta Minorities": 0.38, "Middle Belt Minorities": 0.38,
        "Pada": 0.55, "Naijin": 1.00, "Other-North": 0.35, "Other-South": 0.45,
    },
    "Other-North": {
        "Hausa": 0.55, "Fulani": 0.52, "Hausa-Fulani Undiff": 0.53,
        "Yoruba": 0.10, "Igbo": 0.06, "Ijaw": 0.06, "Kanuri": 0.60,
        "Tiv": 0.30, "Nupe": 0.50, "Edo": 0.08, "Ibibio": 0.06,
        "Niger Delta Minorities": 0.06, "Middle Belt Minorities": 0.40,
        "Pada": 0.15, "Naijin": 0.35, "Other-North": 1.00, "Other-South": 0.10,
    },
    "Other-South": {
        "Hausa": 0.08, "Fulani": 0.08, "Hausa-Fulani Undiff": 0.08,
        "Yoruba": 0.40, "Igbo": 0.42, "Ijaw": 0.40, "Kanuri": 0.08,
        "Tiv": 0.28, "Nupe": 0.18, "Edo": 0.48, "Ibibio": 0.50,
        "Niger Delta Minorities": 0.50, "Middle Belt Minorities": 0.28,
        "Pada": 0.40, "Naijin": 0.45, "Other-North": 0.10, "Other-South": 1.00,
    },
}


# ---------------------------------------------------------------------------
# AffinityMatrix class
# ---------------------------------------------------------------------------

class EthnicAffinityMatrix:
    """
    Ethnic affinity matrix with lookup and utility computation.

    Parameters
    ----------
    matrix : dict[str, dict[str, float]], optional
        Override the default matrix. Keys must cover all groups in ETHNIC_GROUPS.
        Values should be in [0, 1] with diagonal = 1.0.
    """

    def __init__(self, matrix: Optional[dict[str, dict[str, float]]] = None) -> None:
        self._matrix = matrix if matrix is not None else _DEFAULT_MATRIX

    def get_affinity(self, voter_group: str, leader_group: str) -> float:
        """
        Return affinity between voter's ethnic group and party leader's group.

        Parameters
        ----------
        voter_group : str
            Voter's ethnic identity (will be resolved via aliases).
        leader_group : str
            Party leader's ethnic background (will be resolved via aliases).

        Returns
        -------
        float
            Affinity score in [0, 1]. Returns 0.15 as default for unknown pairs.
        """
        # Try raw names first (supports custom matrices with arbitrary group names)
        row = self._matrix.get(voter_group)
        if row is not None:
            val = row.get(leader_group)
            if val is not None:
                return val

        # Fall back to alias resolution for the default matrix
        v = _resolve(voter_group)
        l = _resolve(leader_group)
        row = self._matrix.get(v)
        if row is None:
            return 0.15  # unknown voter group
        return row.get(l, 0.15)  # unknown leader group

    def get_utility(self, voter_group: str, leader_group: str, alpha_e: float) -> float:
        """
        Return ethnic utility component: alpha_e × affinity.

        Parameters
        ----------
        alpha_e : float
            Ethnic sensitivity parameter.
        """
        return alpha_e * self.get_affinity(voter_group, leader_group)

    def as_numpy(self) -> tuple[np.ndarray, list[str]]:
        """
        Export the matrix as a 2D numpy array.

        Returns
        -------
        (array, groups) where array[i, j] is affinity between groups[i] and groups[j].
        """
        groups = ETHNIC_GROUPS
        n = len(groups)
        mat = np.zeros((n, n))
        for i, vg in enumerate(groups):
            for j, lg in enumerate(groups):
                mat[i, j] = self.get_affinity(vg, lg)
        return mat, groups


# Module-level default instance
DEFAULT_ETHNIC_MATRIX = EthnicAffinityMatrix()
