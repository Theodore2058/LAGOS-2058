# Data Directory

This directory contains input data for the LAGOS-2058 election engine.

## Required file

**`nigeria_lga_polsim_2058.xlsx`** — 774 LGA rows × 162 columns

Sheets:
- `LGA_DATA` — main data (774 rows, 162 columns)
- `METADATA` — column descriptions
- `CHANGELOG` — revision history

Column groups (see `src/election_engine/data_loader.py` for full details):
- A–D: Identification (State, LGA Name, Colonial Era Region, Terrain Type)
- E–F: Administrative Zone
- G–L: Demographics (Population, Density, Age, Fertility, Bio Enhancement)
- M–CT: Ethnolinguistic percentages (86 ethnic groups)
- CU–DD: Religious data
- DE–DF: Urbanization
- DG–EB: Economic indicators
- EC–EI: Infrastructure
- EJ–ER: Education
- ES–EZ: Political structure
- FA–FB: Connectivity
- FC–FF: Cultural indicators

This file is **not committed to git** (see `.gitignore`). Obtain it separately and place it in this directory before running the engine.
