# CHANGELOG — LAGOS-2058 Election Engine Calibration

## 2026-03-02 — Cycle 0: Baseline Diagnostic

### Configuration
- 14 parties, 100 MC runs, seed=2058
- Default parameters: q=0.5, β_s=1.0, α_e=2.5, α_r=1.5, λ=1.0, τ₀=1.5, τ₁=0.3, τ₂=0.5, κ=200, σ_nat=0.10, σ_reg=0.15, σ_lga=0.20

### Baseline Results
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| National Turnout | 70.4% | 70–90% | OK (low end) |
| Top party share | NDC 18.2% | <45% | OK |
| Swing LGAs | 304/774 (39.3%) | 10–30% | TOO HIGH |
| NDC in Hausa heartlands | 55–63% | Dominant | OK |
| CND in Yoruba states | 41–46% | Dominant | OK |
| IPA in Igbo states | 25–27% | Dominant | Weak but plausible |
| UJP in Borno | 45.8% | Strong NE | OK |
| MBPP in Bayelsa | 43.3% | Should not dominate | WRONG |
| PLF in Rivers/Bayelsa | 1–10% | Should be stronger | WEAK |

### National Vote Shares (base run)
```
NDC   18.2%    NWF  8.8%    NHA  5.8%    PLF  4.8%    NSA  2.0%
CND   14.2%    ANPC 7.0%    UJP  6.7%    CDA  5.6%    NRP  2.1%
MBPP  11.9%    IPA  6.4%    SNM  6.2%                  NNV  0.2%
```

### Identified Issues (ordered by priority)
1. **Swing LGAs too high (39.3%)**: Noise parameters produce too much MC instability. κ=200 too low, σ_lga=0.20 too high.
2. **MBPP wins Bayelsa (43.3%)**: MBPP (Middle Belt) has no ethnic base in Bayelsa (Ijaw territory). Spatial utility from pro-infrastructure/healthcare positions outweighs ethnic penalty. PLF (Ijaw leader) loses its heartland due to extreme anti-local-resource-control positions (-4.5 on resource revenue).
3. **IPA relatively weak in Igbo heartlands (25–27%)**: Compared to NDC's 55–63% in Hausa heartlands. Driven by more party competition for southern voters. Somewhat realistic (Hausa-Fulani political unity > Igbo) but gap is large.

---

## 2026-03-02 — Cycle 1: Noise Reduction

### Changes
- κ: 200 → 400 (tighter Dirichlet concentration)
- σ_national: 0.10 → 0.07
- σ_regional: 0.15 → 0.10
- Removed unused sigma_lga from EngineParams call

### Results
| Metric | Before | After |
|--------|--------|-------|
| Swing LGAs | 304 (39.3%) | 213 (27.5%) ✓ |
| Base run shares | Unchanged | Unchanged |

### Rationale
Swing LGAs at 39.3% exceeded the 10–30% target. Reduced all three noise components proportionally.

---

## 2026-03-02 — Cycle 2: Identity vs Spatial Rebalancing

### Changes
- α_e: 2.5 → 3.0 (stronger ethnic voting)
- α_r: 1.5 → 2.0 (stronger religious voting)
- β_s: 1.0 → 0.7 (reduced spatial utility dominance)

### Results
| Metric | Cycle 0 | Cycle 2 | Target |
|--------|---------|---------|--------|
| National Turnout | 70.4% | 75.5% | 70–90% ✓ |
| Top party | NDC 18.2% | NDC 18.6% | <45% ✓ |
| Swing LGAs | 304 (39%) | 118 (15%) | 10–30% ✓ |
| NDC in Hausa heartlands | 55–63% | 58–64% | Dominant ✓ |
| CND in Yoruba states | 41–46% | 53–58% | Dominant ✓ |
| IPA in Igbo states | 25–27% | 34–38% | Strong ✓ |
| UJP in Borno | 45.8% | 43.0% | Strong NE ✓ |
| MBPP in Bayelsa | 43.3% | 32.5% | Improved |
| ANPC in Edo | 36.3% | 45.8% | Edo leader ✓ |

### National Vote Shares (Cycle 2 base run)
```
NDC   18.6%    SNM  7.1%    NHA  5.1%    PLF  3.2%    NRP  2.3%
CND   17.0%    NWF  6.3%    UJP  4.6%    NSA  3.2%    NNV  0.5%
MBPP  10.9%    IPA  7.8%    CDA  6.0%
```

### Rationale
With 28 salience-weighted dimensions, spatial utility at β_s=1.0 could reach ±15, overwhelming ethnic utility (max α_e×1.0 = 2.5). Reducing β_s to 0.7 and increasing identity parameters restored proper ethnic heartland dominance. The 30% increase in α_e and 33% increase in α_r bring identity voting to appropriate levels for the Nigerian context.

### Remaining Issues
- MBPP still wins Bayelsa (32.5%) — this is a party design issue (no Ijaw-aligned party with moderate positions). PLF's extreme anti-resource-local-control stance (-4.5) alienates its own ethnic base.
- NNV at 0.5% — extreme party effectively nonviable. Realistic.
