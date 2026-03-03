"""
Religious affinity matrix for the LAGOS-2058 election engine.

Affinity values range -1.0 to +1.0.
  +1.0 = maximum positive affinity (same sub-group identity)
   0.0 = neutral / no religious signal
  -1.0 = maximum antagonism

Categories (9):
  Muslim sub-groups:
    Tijaniyya          — dominant Sufi order, apolitical-traditionalist
    Qadiriyya          — secondary Sufi order, more quietist
    Al-Shahid          — al-Shahid movement (NIM-adjacent, activist)
    Mainstream Sunni   — non-affiliated majority Muslim

  Christian sub-groups:
    Pentecostal        — charismatic / evangelical
    Catholic           — Roman Catholic
    Mainline Protestant — Anglican, Methodist, Presbyterian, ECWA etc.

  Other:
    Traditionalist     — indigenous / syncretic religion
    Secular            — non-religious / religiously unaffiliated
"""

from __future__ import annotations

import numpy as np
from typing import Optional


RELIGIOUS_GROUPS: list[str] = [
    "Tijaniyya",
    "Qadiriyya",
    "Al-Shahid",
    "Mainstream Sunni",
    "Pentecostal",
    "Catholic",
    "Mainline Protestant",
    "Traditionalist",
    "Secular",
]

# Aliases → canonical
_ALIASES: dict[str, str] = {
    "tijaniyya": "Tijaniyya",
    "tijjaniyya": "Tijaniyya",
    "qadiriyya": "Qadiriyya",
    "qadiriya": "Qadiriyya",
    "al-shahid": "Al-Shahid",
    "al shahid": "Al-Shahid",
    "alshahid": "Al-Shahid",
    "mainstream sunni": "Mainstream Sunni",
    "sunni": "Mainstream Sunni",
    "muslim": "Mainstream Sunni",
    "pentecostal": "Pentecostal",
    "evangelical": "Pentecostal",
    "charismatic": "Pentecostal",
    "catholic": "Catholic",
    "roman catholic": "Catholic",
    "mainline protestant": "Mainline Protestant",
    "protestant": "Mainline Protestant",
    "anglican": "Mainline Protestant",
    "methodist": "Mainline Protestant",
    "ecwa": "Mainline Protestant",
    "traditionalist": "Traditionalist",
    "traditional": "Traditionalist",
    "indigenous": "Traditionalist",
    "secular": "Secular",
    "none": "Secular",
    "non-religious": "Secular",
}


def _resolve(group: str) -> str:
    """Resolve a religious group name to its canonical form."""
    canonical = _ALIASES.get(group.lower().strip())
    if canonical:
        return canonical
    if group in RELIGIOUS_GROUPS:
        return group
    return "Secular"  # default fallback


# ---------------------------------------------------------------------------
# Default affinity matrix (-1.0 to +1.0)
# ---------------------------------------------------------------------------
# Key design choices from the spec:
#   Tijaniyya ↔ Al-Shahid:          0.30 (same religion, different politics)
#   Al-Shahid ↔ Pentecostal:       -0.20 (active antagonism)
#   Al-Shahid ↔ Secular:           -0.15
#   Pentecostal ↔ Mainline Prot:    0.60 (within-Christian kinship)
#   Secular ↔ Mainline Prot:        0.20 (mild affinity)
#   Within-Muslim ordering: Tijaniyya ↔ Qadiriyya close, both distant from Al-Shahid
#   Within-Christian ordering: Pentecostal most distinct from Catholic

_DEFAULT_MATRIX: dict[str, dict[str, float]] = {
    "Tijaniyya": {
        "Tijaniyya":         1.00,
        "Qadiriyya":         0.70,
        "Al-Shahid":         0.30,
        "Mainstream Sunni":  0.65,
        "Pentecostal":      -0.05,
        "Catholic":          0.00,
        "Mainline Protestant": 0.05,
        "Traditionalist":    0.10,
        "Secular":           0.00,
    },
    "Qadiriyya": {
        "Tijaniyya":         0.70,
        "Qadiriyya":         1.00,
        "Al-Shahid":         0.25,
        "Mainstream Sunni":  0.70,
        "Pentecostal":      -0.05,
        "Catholic":          0.05,
        "Mainline Protestant": 0.05,
        "Traditionalist":    0.10,
        "Secular":           0.05,
    },
    "Al-Shahid": {
        "Tijaniyya":         0.30,
        "Qadiriyya":         0.25,
        "Al-Shahid":         1.00,
        "Mainstream Sunni":  0.40,
        "Pentecostal":      -0.20,
        "Catholic":         -0.10,
        "Mainline Protestant": -0.10,
        "Traditionalist":   -0.15,
        "Secular":          -0.15,
    },
    "Mainstream Sunni": {
        "Tijaniyya":         0.65,
        "Qadiriyya":         0.70,
        "Al-Shahid":         0.40,
        "Mainstream Sunni":  1.00,
        "Pentecostal":      -0.05,
        "Catholic":          0.00,
        "Mainline Protestant": 0.00,
        "Traditionalist":    0.05,
        "Secular":           0.00,
    },
    "Pentecostal": {
        "Tijaniyya":        -0.05,
        "Qadiriyya":        -0.05,
        "Al-Shahid":        -0.20,
        "Mainstream Sunni": -0.05,
        "Pentecostal":       1.00,
        "Catholic":          0.40,
        "Mainline Protestant": 0.60,
        "Traditionalist":   -0.10,
        "Secular":           0.05,
    },
    "Catholic": {
        "Tijaniyya":         0.00,
        "Qadiriyya":         0.05,
        "Al-Shahid":        -0.10,
        "Mainstream Sunni":  0.00,
        "Pentecostal":       0.40,
        "Catholic":          1.00,
        "Mainline Protestant": 0.65,
        "Traditionalist":    0.05,
        "Secular":           0.15,
    },
    "Mainline Protestant": {
        "Tijaniyya":         0.05,
        "Qadiriyya":         0.05,
        "Al-Shahid":        -0.10,
        "Mainstream Sunni":  0.00,
        "Pentecostal":       0.60,
        "Catholic":          0.65,
        "Mainline Protestant": 1.00,
        "Traditionalist":    0.10,
        "Secular":           0.20,
    },
    "Traditionalist": {
        "Tijaniyya":         0.10,
        "Qadiriyya":         0.10,
        "Al-Shahid":        -0.15,
        "Mainstream Sunni":  0.05,
        "Pentecostal":      -0.10,
        "Catholic":          0.05,
        "Mainline Protestant": 0.10,
        "Traditionalist":    1.00,
        "Secular":           0.25,
    },
    "Secular": {
        "Tijaniyya":         0.00,
        "Qadiriyya":         0.05,
        "Al-Shahid":        -0.15,
        "Mainstream Sunni":  0.00,
        "Pentecostal":       0.05,
        "Catholic":          0.15,
        "Mainline Protestant": 0.20,
        "Traditionalist":    0.25,
        "Secular":           1.00,
    },
}


class ReligiousAffinityMatrix:
    """
    Religious affinity matrix with lookup and sub-category splitting.

    Parameters
    ----------
    matrix : dict[str, dict[str, float]], optional
        Override the default matrix. Values should be in [-1, 1] with diagonal = 1.0.
    """

    def __init__(self, matrix: Optional[dict[str, dict[str, float]]] = None) -> None:
        self._matrix = matrix if matrix is not None else _DEFAULT_MATRIX

    def get_affinity(self, voter_group: str, leader_group: str) -> float:
        """
        Return religious affinity between voter sub-group and leader alignment.

        Returns float in [-1, 1]. Negative values indicate antagonism.
        """
        # Try raw names first (supports custom matrices)
        row = self._matrix.get(voter_group)
        if row is not None:
            val = row.get(leader_group)
            if val is not None:
                return val

        # Fall back to alias resolution
        v = _resolve(voter_group)
        l = _resolve(leader_group)
        row = self._matrix.get(v)
        if row is None:
            return 0.0
        return row.get(l, 0.0)

    def get_utility(self, voter_group: str, leader_group: str, alpha_r: float) -> float:
        """Return religious utility component: alpha_r × affinity."""
        return alpha_r * self.get_affinity(voter_group, leader_group)

    def as_numpy(self) -> tuple[np.ndarray, list[str]]:
        """Export the matrix as a 2D numpy array."""
        groups = RELIGIOUS_GROUPS
        n = len(groups)
        mat = np.zeros((n, n))
        for i, vg in enumerate(groups):
            for j, lg in enumerate(groups):
                mat[i, j] = self.get_affinity(vg, lg)
        return mat, groups


# ---------------------------------------------------------------------------
# Sub-category splitting function
# ---------------------------------------------------------------------------

def split_religious_subcategories(
    pct_muslim: float,
    pct_christian: float,
    pct_traditionalist: float,
    tijaniyya_presence: int,
    qadiriyya_presence: int,
    pentecostal_growth: int,
    al_shahid_influence: int,
    urban_pct: float,
    tertiary_pct: float,
    pada_naijin_pct: float,
) -> dict[str, float]:
    """
    Estimate population fractions for each of the 9 religious sub-categories.

    Parameters
    ----------
    pct_muslim, pct_christian, pct_traditionalist : float
        Percentage of LGA population in each broad religious category (0–100).
    tijaniyya_presence, qadiriyya_presence : int
        Ordinal indicators (0–3) of Sufi order strength.
    pentecostal_growth : int
        Ordinal indicator (0–3) of Pentecostal expansion.
    al_shahid_influence : int
        Ordinal indicator (0–5) of Al-Shahid movement strength.
    urban_pct : float
        Urban population percentage (0–100).
    tertiary_pct : float
        Tertiary-educated population percentage (0–100).
    pada_naijin_pct : float
        Combined Pada + Naijin population share (0–100).

    Returns
    -------
    dict[str, float]
        Estimated fractions for each of the 9 sub-categories. Sums to ~1.0.
    """
    f_muslim = pct_muslim / 100.0
    f_christian = pct_christian / 100.0
    f_trad = pct_traditionalist / 100.0

    # ---- Muslim sub-splits ----
    # Al-Shahid: scales with al_shahid_influence (0–5)
    al_shahid_share = min(al_shahid_influence / 5.0 * 0.35, 0.35)
    # Tijaniyya: ordinal 0–3
    tijaniyya_share = min(tijaniyya_presence / 3.0 * 0.40, 0.40)
    # Qadiriyya: ordinal 0–3, but lower weight than Tijaniyya
    qadiriyya_share = min(qadiriyya_presence / 3.0 * 0.25, 0.25)

    # Normalise within Muslim — remaining is Mainstream Sunni
    total_sufi = al_shahid_share + tijaniyya_share + qadiriyya_share
    if total_sufi > 1.0:
        scale = 1.0 / total_sufi
        al_shahid_share *= scale
        tijaniyya_share *= scale
        qadiriyya_share *= scale
    mainstream_sunni_share = max(0.0, 1.0 - total_sufi)

    f_tijaniyya       = f_muslim * tijaniyya_share
    f_qadiriyya       = f_muslim * qadiriyya_share
    f_al_shahid       = f_muslim * al_shahid_share
    f_main_sunni      = f_muslim * mainstream_sunni_share

    # ---- Christian sub-splits ----
    # Pentecostal: scales with pentecostal_growth (0–3) + urban boost
    pent_base = pentecostal_growth / 3.0 * 0.55 + (urban_pct / 100.0) * 0.10
    pent_share = min(pent_base, 0.65)

    # Catholic vs Mainline: roughly even split of remainder, with mild urban tilt
    remaining_christian = max(0.0, 1.0 - pent_share)
    # Urban areas skew slightly Pentecostal / Catholic; rural skews Mainline
    catholic_share = remaining_christian * (0.40 + urban_pct / 500.0)
    mainline_share = max(0.0, remaining_christian - catholic_share)

    f_pentecostal = f_christian * pent_share
    f_catholic = f_christian * catholic_share
    f_mainline = f_christian * mainline_share

    # ---- Traditionalist sub-split ----
    f_traditionalist = f_trad

    # ---- Secular ----
    # Secular is estimated from urbanization, education, and Pada/Naijin presence
    secular_est = (
        (urban_pct / 100.0) * 0.04
        + (tertiary_pct / 100.0) * 0.10
        + (pada_naijin_pct / 100.0) * 0.15
    )
    # Secular comes out of all groups proportionally; cap at 15% of total
    secular_est = min(secular_est, 0.15)

    # Redistribute: subtract secular from all religious categories proportionally
    total_religious = f_tijaniyya + f_qadiriyya + f_al_shahid + f_main_sunni \
                    + f_pentecostal + f_catholic + f_mainline + f_traditionalist
    if total_religious > 0:
        factor = max(0.0, 1.0 - secular_est) / total_religious
        f_tijaniyya  *= factor
        f_qadiriyya  *= factor
        f_al_shahid  *= factor
        f_main_sunni *= factor
        f_pentecostal *= factor
        f_catholic   *= factor
        f_mainline   *= factor
        f_traditionalist *= factor

    fracs = {
        "Tijaniyya":          f_tijaniyya,
        "Qadiriyya":          f_qadiriyya,
        "Al-Shahid":          f_al_shahid,
        "Mainstream Sunni":   f_main_sunni,
        "Pentecostal":        f_pentecostal,
        "Catholic":           f_catholic,
        "Mainline Protestant": f_mainline,
        "Traditionalist":     f_traditionalist,
        "Secular":            secular_est,
    }

    # Final normalisation to ensure sum ≈ 1.0
    total = sum(fracs.values())
    if total > 0:
        fracs = {k: v / total for k, v in fracs.items()}

    return fracs


def batch_split_religious_subcategories(
    pct_muslim: np.ndarray,
    pct_christian: np.ndarray,
    pct_traditionalist: np.ndarray,
    tijaniyya_presence: np.ndarray,
    qadiriyya_presence: np.ndarray,
    pentecostal_growth: np.ndarray,
    al_shahid_influence: np.ndarray,
    urban_pct: np.ndarray,
    tertiary_pct: np.ndarray,
    pada_naijin_pct: np.ndarray,
) -> np.ndarray:
    """
    Vectorised religious subcategory split for all LGAs at once.

    All inputs are (N,) arrays.  Returns (N, 9) array of fractions in
    RELIGIOUS_GROUPS order.
    """
    N = len(pct_muslim)
    f_muslim = pct_muslim / 100.0
    f_christian = pct_christian / 100.0
    f_trad = pct_traditionalist / 100.0

    # Muslim sub-splits
    al_shahid_share = np.minimum(al_shahid_influence / 5.0 * 0.35, 0.35)
    tijaniyya_share = np.minimum(tijaniyya_presence / 3.0 * 0.40, 0.40)
    qadiriyya_share = np.minimum(qadiriyya_presence / 3.0 * 0.25, 0.25)

    total_sufi = al_shahid_share + tijaniyya_share + qadiriyya_share
    needs_scale = total_sufi > 1.0
    scale = np.where(needs_scale, 1.0 / np.maximum(total_sufi, 1e-30), 1.0)
    al_shahid_share = np.where(needs_scale, al_shahid_share * scale, al_shahid_share)
    tijaniyya_share = np.where(needs_scale, tijaniyya_share * scale, tijaniyya_share)
    qadiriyya_share = np.where(needs_scale, qadiriyya_share * scale, qadiriyya_share)
    mainstream_sunni_share = np.maximum(0.0, 1.0 - al_shahid_share - tijaniyya_share - qadiriyya_share)

    f_tijaniyya = f_muslim * tijaniyya_share
    f_qadiriyya = f_muslim * qadiriyya_share
    f_al_shahid = f_muslim * al_shahid_share
    f_main_sunni = f_muslim * mainstream_sunni_share

    # Christian sub-splits
    pent_base = pentecostal_growth / 3.0 * 0.55 + (urban_pct / 100.0) * 0.10
    pent_share = np.minimum(pent_base, 0.65)
    remaining_christian = np.maximum(0.0, 1.0 - pent_share)
    catholic_share = remaining_christian * (0.40 + urban_pct / 500.0)
    mainline_share = np.maximum(0.0, remaining_christian - catholic_share)

    f_pentecostal = f_christian * pent_share
    f_catholic = f_christian * catholic_share
    f_mainline = f_christian * mainline_share

    # Secular
    secular_est = (
        (urban_pct / 100.0) * 0.04
        + (tertiary_pct / 100.0) * 0.10
        + (pada_naijin_pct / 100.0) * 0.15
    )
    secular_est = np.minimum(secular_est, 0.15)

    # Redistribute
    total_religious = (f_tijaniyya + f_qadiriyya + f_al_shahid + f_main_sunni
                       + f_pentecostal + f_catholic + f_mainline + f_trad)
    factor = np.where(
        total_religious > 0,
        np.maximum(0.0, 1.0 - secular_est) / np.maximum(total_religious, 1e-30),
        1.0,
    )
    f_tijaniyya *= factor
    f_qadiriyya *= factor
    f_al_shahid *= factor
    f_main_sunni *= factor
    f_pentecostal *= factor
    f_catholic *= factor
    f_mainline *= factor
    f_trad *= factor

    # Stack and normalise: (N, 9)
    result = np.column_stack([
        f_tijaniyya, f_qadiriyya, f_al_shahid, f_main_sunni,
        f_pentecostal, f_catholic, f_mainline, f_trad, secular_est,
    ])
    row_sums = result.sum(axis=1, keepdims=True)
    row_sums = np.maximum(row_sums, 1e-30)
    result /= row_sums

    return result


# Module-level default instance
DEFAULT_RELIGIOUS_MATRIX = ReligiousAffinityMatrix()
