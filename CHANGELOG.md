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
