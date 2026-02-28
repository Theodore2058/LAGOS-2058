# Fix Changelog
**Source:** `nigeria_lga_polsim_formatted.xlsx` -> `nigeria_lga_polsim_formatted_fixed.xlsx`
**Date:** 2026-02-28

**Total cells modified: 1776**

| Fix | Cells Changed |
|-----|---------------|
| Categorical | 603 |
| Ethnicity | 1065 |
| Median Age | 35 |
| Religion | 73 |

## Verification

| Check | Before | After |
|-------|--------|-------|
| Ethnicity rows deviating >1.0 from 100 | 318 | 0 |
| Religion null % Muslim | 73 | 0 |
| Religion rows deviating >1.0 from 100 | 73 | 0 |
| Median Age below 15.0 | 35 | 0 |
| Capitalization variants | 13 pairs | 0 |

## Ethnicity Fixes (1065 changes)

| Row | Column | Old | New | Note |
|-----|--------|-----|-----|------|
| 20 | % Other | 7.00 | 27.00 | Added 20.00 deficit to % Other (sum was 80.00) |
| 22 | % Other | 10.00 | 12.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 24 | % Other | 5.00 | 20.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 26 | % Other | 3.00 | 9.00 | Added 6.00 deficit to % Other (sum was 94.00) |
| 28 | % Other | 5.00 | 20.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 29 | % Other | 13.00 | 38.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 31 | % Other | 11.00 | 19.00 | Added 8.00 deficit to % Other (sum was 92.00) |
| 35 | % Other | 7.00 | 12.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 36 | % Other | 8.00 | 43.00 | Added 35.00 deficit to % Other (sum was 65.00) |
| 38 | % Other | 11.00 | 16.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 42 | % Other | 3.00 | 8.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 48 | % Other | 3.00 | 85.00 | Added 82.00 deficit to % Other (sum was 18.00) |
| 51 | % Other | 1.00 | 21.50 | Added 20.50 deficit to % Other (sum was 79.50) |
| 52 | % Hausa | 0.50 | 0.49 | Scaled down by 0.9814 (sum was 101.90) |
| 52 | % Igbo | 0.50 | 0.49 | Scaled down by 0.9814 (sum was 101.90) |
| 52 | % Ibibio | 98.90 | 97.06 | Scaled down by 0.9814 (sum was 101.90) |
| 52 | % Annang | 2.00 | 1.96 | Scaled down by 0.9814 (sum was 101.90) |
| 53 | % Hausa | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Yoruba | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Igbo | 1.10 | 1.03 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Ibibio | 97.30 | 91.02 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Efik | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Annang | 2.00 | 1.87 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Obolo | 3.00 | 2.81 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Other | 2.00 | 1.87 | Scaled down by 0.9355 (sum was 106.90) |
| 53 | % Ibibio | 91.02 | 91.01 | Rounding adjustment of -0.01 |
| 55 | % Igbo | 2.20 | 2.16 | Scaled down by 0.9804 (sum was 102.00) |
| 55 | % Ibibio | 97.80 | 95.88 | Scaled down by 0.9804 (sum was 102.00) |
| 55 | % Annang | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 56 | % Other | 2.00 | 3.50 | Added 1.50 deficit to % Other (sum was 98.50) |
| 64 | % Hausa | 1.10 | 1.02 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Yoruba | 0.50 | 0.46 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Igbo | 0.50 | 0.46 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Ibibio | 97.80 | 90.64 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Annang | 1.00 | 0.93 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Obolo | 2.00 | 1.85 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Eket | 4.00 | 3.71 | Scaled down by 0.9268 (sum was 107.90) |
| 64 | % Other | 1.00 | 0.93 | Scaled down by 0.9268 (sum was 107.90) |
| 69 | % Hausa | 0.50 | 0.47 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Yoruba | 0.50 | 0.47 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Igbo | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Ibibio | 93.60 | 88.30 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Efik | 4.30 | 4.06 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Annang | 1.00 | 0.94 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Oron | 2.00 | 1.89 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Obolo | 2.00 | 1.89 | Scaled down by 0.9434 (sum was 106.00) |
| 69 | % Other | 1.00 | 0.94 | Scaled down by 0.9434 (sum was 106.00) |
| 71 | % Hausa | 3.40 | 3.05 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Yoruba | 2.20 | 1.97 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Igbo | 5.60 | 5.03 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Ibibio | 87.60 | 78.64 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Efik | 1.10 | 0.99 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Annang | 5.00 | 4.49 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Oron | 2.00 | 1.80 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Obolo | 0.50 | 0.45 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Eket | 2.00 | 1.80 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Other | 2.00 | 1.80 | Scaled down by 0.8977 (sum was 111.40) |
| 71 | % Ibibio | 78.64 | 78.62 | Rounding adjustment of -0.02 |
| 93 | % Other | 0.00 | 40.00 | Added 40.00 deficit to % Other (sum was 60.00) |
| 94 | % Other | 9.00 | 30.00 | Added 21.00 deficit to % Other (sum was 79.00) |
| 95 | % Other | 7.00 | 80.00 | Added 73.00 deficit to % Other (sum was 27.00) |
| 96 | % Other | 5.00 | 15.00 | Added 10.00 deficit to % Other (sum was 90.00) |
| 97 | % Other | 6.00 | 35.00 | Added 29.00 deficit to % Other (sum was 71.00) |
| 98 | % Other | 0.00 | 70.00 | Added 70.00 deficit to % Other (sum was 30.00) |
| 99 | % Other | 5.00 | 35.00 | Added 30.00 deficit to % Other (sum was 70.00) |
| 100 | % Other | 5.00 | 45.00 | Added 40.00 deficit to % Other (sum was 60.00) |
| 101 | % Other | 7.00 | 32.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 102 | % Hausa | 73.90 | 69.07 | Scaled down by 0.9346 (sum was 107.00) |
| 102 | % Fulani | 22.70 | 21.21 | Scaled down by 0.9346 (sum was 107.00) |
| 102 | % Kanuri | 3.40 | 3.18 | Scaled down by 0.9346 (sum was 107.00) |
| 102 | % Other | 7.00 | 6.54 | Scaled down by 0.9346 (sum was 107.00) |
| 103 | % Other | 0.00 | 20.00 | Added 20.00 deficit to % Other (sum was 80.00) |
| 104 | % Other | 1.00 | 30.00 | Added 29.00 deficit to % Other (sum was 71.00) |
| 105 | % Other | 0.00 | 40.00 | Added 40.00 deficit to % Other (sum was 60.00) |
| 106 | % Other | 7.00 | 22.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 107 | % Other | 0.00 | 50.00 | Added 50.00 deficit to % Other (sum was 50.00) |
| 108 | % Other | 7.00 | 25.00 | Added 18.00 deficit to % Other (sum was 82.00) |
| 109 | % Other | 9.00 | 65.00 | Added 56.00 deficit to % Other (sum was 44.00) |
| 110 | % Other | 5.00 | 48.00 | Added 43.00 deficit to % Other (sum was 57.00) |
| 111 | % Other | 7.00 | 75.00 | Added 68.00 deficit to % Other (sum was 32.00) |
| 112 | % Other | 7.00 | 30.00 | Added 23.00 deficit to % Other (sum was 77.00) |
| 121 | % Other | 2.00 | 17.50 | Added 15.50 deficit to % Other (sum was 84.50) |
| 122 | % Other | 2.00 | 75.00 | Added 73.00 deficit to % Other (sum was 27.00) |
| 123 | % Other | 1.00 | 3.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 124 | % Hausa | 1.70 | 1.68 | Scaled down by 0.9891 (sum was 101.10) |
| 124 | % Fulani | 2.20 | 2.18 | Scaled down by 0.9891 (sum was 101.10) |
| 124 | % Yoruba | 0.60 | 0.59 | Scaled down by 0.9891 (sum was 101.10) |
| 124 | % Tiv | 95.00 | 93.97 | Scaled down by 0.9891 (sum was 101.10) |
| 124 | % Idoma | 0.60 | 0.59 | Scaled down by 0.9891 (sum was 101.10) |
| 124 | % Other | 1.00 | 0.99 | Scaled down by 0.9891 (sum was 101.10) |
| 125 | % Other | 1.00 | 2.50 | Added 1.50 deficit to % Other (sum was 98.50) |
| 126 | % Other | 3.00 | 4.50 | Added 1.50 deficit to % Other (sum was 98.50) |
| 127 | % Hausa | 1.10 | 1.08 | Scaled down by 0.9804 (sum was 102.00) |
| 127 | % Fulani | 1.60 | 1.57 | Scaled down by 0.9804 (sum was 102.00) |
| 127 | % Igbo | 0.50 | 0.49 | Scaled down by 0.9804 (sum was 102.00) |
| 127 | % Tiv | 95.70 | 93.82 | Scaled down by 0.9804 (sum was 102.00) |
| 127 | % Idoma | 1.10 | 1.08 | Scaled down by 0.9804 (sum was 102.00) |
| 127 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 129 | % Other | 1.00 | 5.00 | Added 4.00 deficit to % Other (sum was 96.00) |
| 130 | % Hausa | 0.50 | 0.49 | Scaled down by 0.9814 (sum was 101.90) |
| 130 | % Fulani | 1.60 | 1.57 | Scaled down by 0.9814 (sum was 101.90) |
| 130 | % Igbo | 0.50 | 0.49 | Scaled down by 0.9814 (sum was 101.90) |
| 130 | % Tiv | 96.80 | 95.00 | Scaled down by 0.9814 (sum was 101.90) |
| 130 | % Idoma | 0.50 | 0.49 | Scaled down by 0.9814 (sum was 101.90) |
| 130 | % Other | 2.00 | 1.96 | Scaled down by 0.9814 (sum was 101.90) |
| 133 | % Hausa | 5.50 | 5.29 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Fulani | 1.60 | 1.54 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Yoruba | 3.30 | 3.17 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Igbo | 8.70 | 8.37 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Tiv | 60.10 | 57.79 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Nupe | 1.10 | 1.06 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Igala | 1.10 | 1.06 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Idoma | 16.40 | 15.77 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Jukun | 2.20 | 2.12 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 133 | % Tiv | 57.79 | 57.77 | Rounding adjustment of -0.02 |
| 134 | % Other | 5.00 | 84.50 | Added 79.50 deficit to % Other (sum was 20.50) |
| 137 | % Other | 6.00 | 85.50 | Added 79.50 deficit to % Other (sum was 20.50) |
| 138 | % Hausa | 1.10 | 1.05 | Scaled down by 0.9524 (sum was 105.00) |
| 138 | % Fulani | 0.60 | 0.57 | Scaled down by 0.9524 (sum was 105.00) |
| 138 | % Yoruba | 0.60 | 0.57 | Scaled down by 0.9524 (sum was 105.00) |
| 138 | % Igbo | 2.20 | 2.10 | Scaled down by 0.9524 (sum was 105.00) |
| 138 | % Tiv | 1.10 | 1.05 | Scaled down by 0.9524 (sum was 105.00) |
| 138 | % Idoma | 94.40 | 89.90 | Scaled down by 0.9524 (sum was 105.00) |
| 138 | % Other | 5.00 | 4.76 | Scaled down by 0.9524 (sum was 105.00) |
| 139 | % Hausa | 2.70 | 2.60 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Fulani | 0.50 | 0.48 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Yoruba | 1.60 | 1.54 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Igbo | 3.30 | 3.18 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Tiv | 2.20 | 2.12 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Idoma | 89.60 | 86.24 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Other | 4.00 | 3.85 | Scaled down by 0.9625 (sum was 103.90) |
| 139 | % Idoma | 86.24 | 86.23 | Rounding adjustment of -0.01 |
| 140 | % Other | 2.00 | 3.50 | Added 1.50 deficit to % Other (sum was 98.50) |
| 144 | % Other | 0.00 | 5.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 145 | % Other | 0.00 | 28.00 | Added 28.00 deficit to % Other (sum was 72.00) |
| 146 | % Hausa | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 146 | % Fulani | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 146 | % Kanuri | 79.10 | 77.55 | Scaled down by 0.9804 (sum was 102.00) |
| 146 | % Shuwa Arab | 11.00 | 10.78 | Scaled down by 0.9804 (sum was 102.00) |
| 146 | % Marghi | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 146 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 146 | % Kanuri | 77.55 | 77.54 | Rounding adjustment of -0.01 |
| 147 | % Other | 2.00 | 19.00 | Added 17.00 deficit to % Other (sum was 83.00) |
| 148 | % Other | 2.00 | 27.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 149 | % Other | 2.00 | 85.00 | Added 83.00 deficit to % Other (sum was 17.00) |
| 150 | % Other | 9.00 | 39.00 | Added 30.00 deficit to % Other (sum was 70.00) |
| 151 | % Hausa | 3.20 | 3.08 | Scaled down by 0.9615 (sum was 104.00) |
| 151 | % Fulani | 5.40 | 5.19 | Scaled down by 0.9615 (sum was 104.00) |
| 151 | % Kanuri | 53.80 | 51.73 | Scaled down by 0.9615 (sum was 104.00) |
| 151 | % Shuwa Arab | 37.60 | 36.15 | Scaled down by 0.9615 (sum was 104.00) |
| 151 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 153 | % Other | 0.00 | 5.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 154 | % Other | 7.00 | 80.00 | Added 73.00 deficit to % Other (sum was 27.00) |
| 155 | % Other | 2.00 | 14.00 | Added 12.00 deficit to % Other (sum was 88.00) |
| 156 | % Hausa | 5.40 | 5.14 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Fulani | 4.30 | 4.10 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Kanuri | 78.30 | 74.57 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Shuwa Arab | 5.40 | 5.14 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Marghi | 3.30 | 3.14 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Bura | 3.30 | 3.14 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Other | 5.00 | 4.76 | Scaled down by 0.9524 (sum was 105.00) |
| 156 | % Kanuri | 74.57 | 74.58 | Rounding adjustment of +0.01 |
| 157 | % Hausa | 3.20 | 3.11 | Scaled down by 0.9709 (sum was 103.00) |
| 157 | % Fulani | 3.20 | 3.11 | Scaled down by 0.9709 (sum was 103.00) |
| 157 | % Kanuri | 90.40 | 87.77 | Scaled down by 0.9709 (sum was 103.00) |
| 157 | % Shuwa Arab | 3.20 | 3.11 | Scaled down by 0.9709 (sum was 103.00) |
| 157 | % Other | 3.00 | 2.91 | Scaled down by 0.9709 (sum was 103.00) |
| 157 | % Kanuri | 87.77 | 87.76 | Rounding adjustment of -0.01 |
| 158 | % Other | 5.00 | 20.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 159 | % Hausa | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 159 | % Fulani | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 159 | % Kanuri | 79.10 | 77.55 | Scaled down by 0.9804 (sum was 102.00) |
| 159 | % Shuwa Arab | 8.80 | 8.63 | Scaled down by 0.9804 (sum was 102.00) |
| 159 | % Marghi | 5.50 | 5.39 | Scaled down by 0.9804 (sum was 102.00) |
| 159 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 159 | % Kanuri | 77.55 | 77.54 | Rounding adjustment of -0.01 |
| 160 | % Other | 2.00 | 15.00 | Added 13.00 deficit to % Other (sum was 87.00) |
| 161 | % Other | 2.00 | 5.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 162 | % Hausa | 3.30 | 3.17 | Scaled down by 0.9606 (sum was 104.10) |
| 162 | % Fulani | 3.30 | 3.17 | Scaled down by 0.9606 (sum was 104.10) |
| 162 | % Kanuri | 84.80 | 81.46 | Scaled down by 0.9606 (sum was 104.10) |
| 162 | % Shuwa Arab | 8.70 | 8.36 | Scaled down by 0.9606 (sum was 104.10) |
| 162 | % Other | 4.00 | 3.84 | Scaled down by 0.9606 (sum was 104.10) |
| 164 | % Hausa | 10.90 | 10.48 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Fulani | 5.40 | 5.19 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Yoruba | 2.20 | 2.12 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Igbo | 2.20 | 2.12 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Ijaw | 1.10 | 1.06 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Kanuri | 59.80 | 57.50 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Shuwa Arab | 8.70 | 8.37 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Marghi | 5.40 | 5.19 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Bura | 4.30 | 4.13 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 164 | % Kanuri | 57.50 | 57.49 | Rounding adjustment of -0.01 |
| 165 | % Hausa | 2.20 | 2.16 | Scaled down by 0.9804 (sum was 102.00) |
| 165 | % Fulani | 3.20 | 3.14 | Scaled down by 0.9804 (sum was 102.00) |
| 165 | % Kanuri | 73.10 | 71.67 | Scaled down by 0.9804 (sum was 102.00) |
| 165 | % Shuwa Arab | 21.50 | 21.08 | Scaled down by 0.9804 (sum was 102.00) |
| 165 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 165 | % Kanuri | 71.67 | 71.66 | Rounding adjustment of -0.01 |
| 166 | % Hausa | 2.20 | 2.16 | Scaled down by 0.9804 (sum was 102.00) |
| 166 | % Fulani | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 166 | % Kanuri | 85.70 | 84.02 | Scaled down by 0.9804 (sum was 102.00) |
| 166 | % Shuwa Arab | 8.80 | 8.63 | Scaled down by 0.9804 (sum was 102.00) |
| 166 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 166 | % Kanuri | 84.02 | 84.01 | Rounding adjustment of -0.01 |
| 167 | % Hausa | 2.20 | 2.16 | Scaled down by 0.9804 (sum was 102.00) |
| 167 | % Fulani | 3.20 | 3.14 | Scaled down by 0.9804 (sum was 102.00) |
| 167 | % Kanuri | 89.20 | 87.45 | Scaled down by 0.9804 (sum was 102.00) |
| 167 | % Shuwa Arab | 5.40 | 5.29 | Scaled down by 0.9804 (sum was 102.00) |
| 167 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 168 | % Hausa | 3.20 | 3.08 | Scaled down by 0.9615 (sum was 104.00) |
| 168 | % Fulani | 5.40 | 5.19 | Scaled down by 0.9615 (sum was 104.00) |
| 168 | % Kanuri | 59.10 | 56.83 | Scaled down by 0.9615 (sum was 104.00) |
| 168 | % Shuwa Arab | 32.30 | 31.06 | Scaled down by 0.9615 (sum was 104.00) |
| 168 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 168 | % Kanuri | 56.83 | 56.82 | Rounding adjustment of -0.01 |
| 170 | % Other | 3.00 | 52.00 | Added 49.00 deficit to % Other (sum was 51.00) |
| 171 | % Other | 2.00 | 88.00 | Added 86.00 deficit to % Other (sum was 14.00) |
| 172 | % Other | 6.00 | 28.00 | Added 22.00 deficit to % Other (sum was 78.00) |
| 173 | % Hausa | 0.60 | 0.57 | Scaled down by 0.9524 (sum was 105.00) |
| 173 | % Yoruba | 1.10 | 1.05 | Scaled down by 0.9524 (sum was 105.00) |
| 173 | % Igbo | 3.40 | 3.24 | Scaled down by 0.9524 (sum was 105.00) |
| 173 | % Ibibio | 4.50 | 4.29 | Scaled down by 0.9524 (sum was 105.00) |
| 173 | % Efik | 81.40 | 77.52 | Scaled down by 0.9524 (sum was 105.00) |
| 173 | % Ekoi | 9.00 | 8.57 | Scaled down by 0.9524 (sum was 105.00) |
| 173 | % Other | 5.00 | 4.76 | Scaled down by 0.9524 (sum was 105.00) |
| 174 | % Other | 6.00 | 31.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 175 | % Other | 3.00 | 93.00 | Added 90.00 deficit to % Other (sum was 10.00) |
| 176 | % Other | 9.00 | 76.00 | Added 67.00 deficit to % Other (sum was 33.00) |
| 177 | % Other | 4.00 | 92.00 | Added 88.00 deficit to % Other (sum was 12.00) |
| 178 | % Other | 17.00 | 24.50 | Added 7.50 deficit to % Other (sum was 92.50) |
| 179 | % Other | 17.00 | 41.50 | Added 24.50 deficit to % Other (sum was 75.50) |
| 180 | % Hausa | 0.60 | 0.58 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Yoruba | 0.60 | 0.58 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Igbo | 1.10 | 1.06 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Ibibio | 0.60 | 0.58 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Efik | 1.10 | 1.06 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Ekoi | 96.00 | 92.31 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 180 | % Ekoi | 92.31 | 92.29 | Rounding adjustment of -0.02 |
| 181 | % Other | 7.00 | 59.00 | Added 52.00 deficit to % Other (sum was 48.00) |
| 182 | % Other | 6.00 | 94.50 | Added 88.50 deficit to % Other (sum was 11.50) |
| 183 | % Other | 5.00 | 90.00 | Added 85.00 deficit to % Other (sum was 15.00) |
| 184 | % Other | 6.00 | 94.50 | Added 88.50 deficit to % Other (sum was 11.50) |
| 185 | % Other | 9.00 | 28.50 | Added 19.50 deficit to % Other (sum was 80.50) |
| 186 | % Other | 6.00 | 66.00 | Added 60.00 deficit to % Other (sum was 40.00) |
| 187 | % Other | 2.00 | 93.00 | Added 91.00 deficit to % Other (sum was 9.00) |
| 188 | % Other | 6.00 | 90.50 | Added 84.50 deficit to % Other (sum was 15.50) |
| 189 | % Igbo | 95.70 | 93.92 | Scaled down by 0.9814 (sum was 101.90) |
| 189 | % Edo Bini | 2.10 | 2.06 | Scaled down by 0.9814 (sum was 101.90) |
| 189 | % Igala | 2.10 | 2.06 | Scaled down by 0.9814 (sum was 101.90) |
| 189 | % Other | 2.00 | 1.96 | Scaled down by 0.9814 (sum was 101.90) |
| 192 | % Igbo | 2.10 | 1.98 | Scaled down by 0.9434 (sum was 106.00) |
| 192 | % Ijaw | 83.00 | 78.30 | Scaled down by 0.9434 (sum was 106.00) |
| 192 | % Urhobo | 4.30 | 4.06 | Scaled down by 0.9434 (sum was 106.00) |
| 192 | % Itsekiri | 8.50 | 8.02 | Scaled down by 0.9434 (sum was 106.00) |
| 192 | % Isoko | 2.10 | 1.98 | Scaled down by 0.9434 (sum was 106.00) |
| 192 | % Other | 6.00 | 5.66 | Scaled down by 0.9434 (sum was 106.00) |
| 194 | % Igbo | 4.30 | 4.06 | Scaled down by 0.9434 (sum was 106.00) |
| 194 | % Edo Bini | 5.30 | 5.00 | Scaled down by 0.9434 (sum was 106.00) |
| 194 | % Urhobo | 87.20 | 82.26 | Scaled down by 0.9434 (sum was 106.00) |
| 194 | % Itsekiri | 3.20 | 3.02 | Scaled down by 0.9434 (sum was 106.00) |
| 194 | % Other | 6.00 | 5.66 | Scaled down by 0.9434 (sum was 106.00) |
| 196 | % Igbo | 92.60 | 87.36 | Scaled down by 0.9434 (sum was 106.00) |
| 196 | % Edo Bini | 5.30 | 5.00 | Scaled down by 0.9434 (sum was 106.00) |
| 196 | % Urhobo | 2.10 | 1.98 | Scaled down by 0.9434 (sum was 106.00) |
| 196 | % Other | 6.00 | 5.66 | Scaled down by 0.9434 (sum was 106.00) |
| 199 | % Igbo | 90.30 | 84.31 | Scaled down by 0.9337 (sum was 107.10) |
| 199 | % Ijaw | 5.40 | 5.04 | Scaled down by 0.9337 (sum was 107.10) |
| 199 | % Urhobo | 2.20 | 2.05 | Scaled down by 0.9337 (sum was 107.10) |
| 199 | % Itsekiri | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 199 | % Isoko | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 199 | % Other | 7.00 | 6.54 | Scaled down by 0.9337 (sum was 107.10) |
| 203 | % Hausa | 1.10 | 0.99 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Yoruba | 2.20 | 1.99 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Igbo | 84.30 | 76.08 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Ijaw | 2.20 | 1.99 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Edo Bini | 2.20 | 1.99 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Urhobo | 5.60 | 5.05 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Itsekiri | 1.10 | 0.99 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Isoko | 1.10 | 0.99 | Scaled down by 0.9025 (sum was 110.80) |
| 203 | % Other | 11.00 | 9.93 | Scaled down by 0.9025 (sum was 110.80) |
| 205 | % Yoruba | 4.30 | 3.99 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Igbo | 13.00 | 12.05 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Ijaw | 3.30 | 3.06 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Edo Bini | 7.60 | 7.04 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Urhobo | 65.20 | 60.43 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Itsekiri | 5.40 | 5.00 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Isoko | 1.10 | 1.02 | Scaled down by 0.9268 (sum was 107.90) |
| 205 | % Other | 8.00 | 7.41 | Scaled down by 0.9268 (sum was 107.90) |
| 210 | % Yoruba | 3.20 | 2.99 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Igbo | 9.70 | 9.06 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Ijaw | 4.30 | 4.01 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Edo Bini | 2.20 | 2.05 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Urhobo | 73.10 | 68.25 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Itsekiri | 6.50 | 6.07 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Isoko | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 210 | % Other | 7.00 | 6.54 | Scaled down by 0.9337 (sum was 107.10) |
| 212 | % Yoruba | 3.40 | 3.04 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Igbo | 15.90 | 14.20 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Ijaw | 14.80 | 13.21 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Edo Bini | 2.30 | 2.05 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Urhobo | 28.40 | 25.36 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Itsekiri | 34.10 | 30.45 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Isoko | 1.10 | 0.98 | Scaled down by 0.8929 (sum was 112.00) |
| 212 | % Other | 12.00 | 10.71 | Scaled down by 0.8929 (sum was 112.00) |
| 221 | % Other | 1.00 | 4.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 225 | % Other | 1.00 | 4.50 | Added 3.50 deficit to % Other (sum was 96.50) |
| 235 | % Hausa Fulani Undiff | 6.40 | 6.03 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Yoruba | 4.30 | 4.05 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Igbo | 4.30 | 4.05 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Nupe | 1.10 | 1.04 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Edo Bini | 83.00 | 78.15 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Ebira | 1.10 | 1.04 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Other | 6.00 | 5.65 | Scaled down by 0.9416 (sum was 106.20) |
| 235 | % Edo Bini | 78.15 | 78.14 | Rounding adjustment of -0.01 |
| 238 | % Hausa Fulani Undiff | 4.20 | 3.96 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Yoruba | 6.30 | 5.94 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Igbo | 9.50 | 8.96 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Ijaw | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Edo Bini | 74.10 | 69.91 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Urhobo | 2.60 | 2.45 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Itsekiri | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Isoko | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 238 | % Other | 6.00 | 5.66 | Scaled down by 0.9434 (sum was 106.00) |
| 279 | % Other | 1.00 | 12.40 | Added 11.40 deficit to % Other (sum was 88.60) |
| 284 | % Other | 14.00 | 19.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 285 | % Other | 9.00 | 34.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 290 | % Other | 9.00 | 47.00 | Added 38.00 deficit to % Other (sum was 62.00) |
| 293 | % Other | 10.00 | 35.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 324 | % Hausa | 56.50 | 52.31 | Scaled down by 0.9259 (sum was 108.00) |
| 324 | % Fulani | 10.90 | 10.09 | Scaled down by 0.9259 (sum was 108.00) |
| 324 | % Kanuri | 32.60 | 30.19 | Scaled down by 0.9259 (sum was 108.00) |
| 324 | % Ngizim | 3.00 | 2.78 | Scaled down by 0.9259 (sum was 108.00) |
| 324 | % Other | 5.00 | 4.63 | Scaled down by 0.9259 (sum was 108.00) |
| 325 | % Hausa | 80.40 | 77.31 | Scaled down by 0.9615 (sum was 104.00) |
| 325 | % Fulani | 19.60 | 18.85 | Scaled down by 0.9615 (sum was 104.00) |
| 325 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 325 | % Hausa | 77.31 | 77.30 | Rounding adjustment of -0.01 |
| 334 | % Hausa | 67.80 | 62.26 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Fulani | 10.90 | 10.01 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Yoruba | 2.20 | 2.02 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Igbo | 1.60 | 1.47 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Kanuri | 16.40 | 15.06 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Tiv | 0.50 | 0.46 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Igala | 0.50 | 0.46 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Duwai | 3.00 | 2.75 | Scaled down by 0.9183 (sum was 108.90) |
| 334 | % Other | 6.00 | 5.51 | Scaled down by 0.9183 (sum was 108.90) |
| 339 | % Hausa | 54.30 | 50.28 | Scaled down by 0.9259 (sum was 108.00) |
| 339 | % Fulani | 10.90 | 10.09 | Scaled down by 0.9259 (sum was 108.00) |
| 339 | % Kanuri | 34.80 | 32.22 | Scaled down by 0.9259 (sum was 108.00) |
| 339 | % Ngizim | 3.00 | 2.78 | Scaled down by 0.9259 (sum was 108.00) |
| 339 | % Other | 5.00 | 4.63 | Scaled down by 0.9259 (sum was 108.00) |
| 342 | % Hausa | 62.40 | 58.26 | Scaled down by 0.9337 (sum was 107.10) |
| 342 | % Fulani | 12.90 | 12.04 | Scaled down by 0.9337 (sum was 107.10) |
| 342 | % Kanuri | 23.70 | 22.13 | Scaled down by 0.9337 (sum was 107.10) |
| 342 | % Shuwa Arab | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 342 | % Other | 7.00 | 6.54 | Scaled down by 0.9337 (sum was 107.10) |
| 349 | % Other | 1.00 | 15.00 | Added 14.00 deficit to % Other (sum was 86.00) |
| 350 | % Other | 0.00 | 22.00 | Added 22.00 deficit to % Other (sum was 78.00) |
| 352 | % Hausa | 65.20 | 60.88 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Fulani | 10.90 | 10.18 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Yoruba | 4.30 | 4.01 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Igbo | 3.30 | 3.08 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Kanuri | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Nupe | 2.20 | 2.05 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Igala | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Ebira | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Gwari Gbagyi | 5.40 | 5.04 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Kataf Atyap | 2.20 | 2.05 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Bajju | 2.20 | 2.05 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Ham Jaba | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 352 | % Other | 7.00 | 6.54 | Scaled down by 0.9337 (sum was 107.10) |
| 354 | % Hausa | 8.60 | 8.28 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Fulani | 3.20 | 3.08 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Yoruba | 1.10 | 1.06 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Igbo | 1.60 | 1.54 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Nupe | 0.50 | 0.48 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Gwari Gbagyi | 1.10 | 1.06 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Kataf Atyap | 0.50 | 0.48 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Bajju | 1.10 | 1.06 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Ham Jaba | 82.20 | 79.11 | Scaled down by 0.9625 (sum was 103.90) |
| 354 | % Other | 4.00 | 3.85 | Scaled down by 0.9625 (sum was 103.90) |
| 355 | % Other | 9.00 | 58.00 | Added 49.00 deficit to % Other (sum was 51.00) |
| 356 | % Other | 8.00 | 45.50 | Added 37.50 deficit to % Other (sum was 62.50) |
| 357 | % Hausa | 68.10 | 63.06 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Fulani | 8.80 | 8.15 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Yoruba | 5.50 | 5.09 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Igbo | 4.40 | 4.07 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Kanuri | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Nupe | 3.30 | 3.06 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Igala | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Ebira | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Gwari Gbagyi | 3.30 | 3.06 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Kataf Atyap | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Bajju | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Ham Jaba | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Other | 8.00 | 7.41 | Scaled down by 0.9259 (sum was 108.00) |
| 357 | % Hausa | 63.06 | 63.04 | Rounding adjustment of -0.02 |
| 358 | % Other | 1.00 | 18.00 | Added 17.00 deficit to % Other (sum was 83.00) |
| 359 | % Other | 7.00 | 58.00 | Added 51.00 deficit to % Other (sum was 49.00) |
| 360 | % Other | 6.00 | 64.00 | Added 58.00 deficit to % Other (sum was 42.00) |
| 361 | % Other | 1.00 | 89.00 | Added 88.00 deficit to % Other (sum was 12.00) |
| 362 | % Other | 14.00 | 60.00 | Added 46.00 deficit to % Other (sum was 54.00) |
| 363 | % Hausa | 85.40 | 80.49 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Fulani | 11.20 | 10.56 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Yoruba | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Igbo | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Kanuri | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Nupe | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Gwari Gbagyi | 1.10 | 1.04 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Other | 6.00 | 5.66 | Scaled down by 0.9425 (sum was 106.10) |
| 363 | % Hausa | 80.49 | 80.46 | Rounding adjustment of -0.03 |
| 365 | % Other | 9.00 | 18.00 | Added 9.00 deficit to % Other (sum was 91.00) |
| 368 | % Other | 6.00 | 88.00 | Added 82.00 deficit to % Other (sum was 18.00) |
| 369 | % Hausa | 84.30 | 79.53 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Fulani | 11.20 | 10.57 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Yoruba | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Igbo | 0.60 | 0.57 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Kanuri | 0.60 | 0.57 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Nupe | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Gwari Gbagyi | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Other | 6.00 | 5.66 | Scaled down by 0.9434 (sum was 106.00) |
| 369 | % Hausa | 79.53 | 79.51 | Rounding adjustment of -0.02 |
| 370 | % Other | 7.00 | 24.00 | Added 17.00 deficit to % Other (sum was 83.00) |
| 371 | % Other | 2.00 | 4.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 377 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 378 | % Hausa | 84.90 | 80.17 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Fulani | 5.30 | 5.00 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Yoruba | 3.20 | 3.02 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Igbo | 1.60 | 1.51 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Ijaw | 0.20 | 0.19 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Kanuri | 2.10 | 1.98 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Shuwa Arab | 0.50 | 0.47 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Nupe | 1.60 | 1.51 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Edo Bini | 0.30 | 0.28 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Ebira | 0.20 | 0.19 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Other | 6.00 | 5.67 | Scaled down by 0.9443 (sum was 105.90) |
| 378 | % Hausa | 80.17 | 80.18 | Rounding adjustment of +0.01 |
| 380 | % Other | 0.00 | 1.70 | Added 1.70 deficit to % Other (sum was 98.30) |
| 381 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 382 | % Hausa | 88.60 | 85.19 | Scaled down by 0.9615 (sum was 104.00) |
| 382 | % Fulani | 11.40 | 10.96 | Scaled down by 0.9615 (sum was 104.00) |
| 382 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 383 | % Hausa | 75.60 | 68.92 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Fulani | 4.40 | 4.01 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Yoruba | 7.80 | 7.11 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Igbo | 5.00 | 4.56 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Ijaw | 0.40 | 0.36 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Kanuri | 2.20 | 2.01 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Shuwa Arab | 0.30 | 0.27 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Tiv | 0.20 | 0.18 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Ibibio | 0.20 | 0.18 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Nupe | 2.20 | 2.01 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Edo Bini | 0.40 | 0.36 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Urhobo | 0.10 | 0.09 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Igala | 0.20 | 0.18 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Idoma | 0.10 | 0.09 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Ebira | 0.40 | 0.36 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Gwari Gbagyi | 0.20 | 0.18 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Other | 10.00 | 9.12 | Scaled down by 0.9116 (sum was 109.70) |
| 383 | % Hausa | 68.92 | 68.93 | Rounding adjustment of +0.01 |
| 385 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 386 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 389 | % Hausa | 83.20 | 78.64 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Fulani | 5.30 | 5.01 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Yoruba | 4.30 | 4.06 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Igbo | 2.10 | 1.98 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Ijaw | 0.20 | 0.19 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Kanuri | 2.10 | 1.98 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Shuwa Arab | 0.50 | 0.47 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Nupe | 1.60 | 1.51 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Edo Bini | 0.30 | 0.28 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Ebira | 0.20 | 0.19 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Other | 6.00 | 5.67 | Scaled down by 0.9452 (sum was 105.80) |
| 389 | % Hausa | 78.64 | 78.66 | Rounding adjustment of +0.02 |
| 392 | % Hausa | 81.30 | 76.12 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Fulani | 5.30 | 4.96 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Yoruba | 4.30 | 4.03 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Igbo | 3.20 | 3.00 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Ijaw | 0.20 | 0.19 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Kanuri | 2.10 | 1.97 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Shuwa Arab | 0.50 | 0.47 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Nupe | 2.10 | 1.97 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Edo Bini | 0.30 | 0.28 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Ebira | 0.30 | 0.28 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Gwari Gbagyi | 0.20 | 0.19 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Other | 7.00 | 6.55 | Scaled down by 0.9363 (sum was 106.80) |
| 392 | % Hausa | 76.12 | 76.11 | Rounding adjustment of -0.01 |
| 412 | % Other | 0.00 | 2.20 | Added 2.20 deficit to % Other (sum was 97.80) |
| 433 | % Other | 1.00 | 3.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 439 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 450 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 451 | % Other | 0.00 | 32.00 | Added 32.00 deficit to % Other (sum was 68.00) |
| 452 | % Hausa | 72.50 | 71.08 | Scaled down by 0.9804 (sum was 102.00) |
| 452 | % Fulani | 24.20 | 23.73 | Scaled down by 0.9804 (sum was 102.00) |
| 452 | % Yoruba | 1.10 | 1.08 | Scaled down by 0.9804 (sum was 102.00) |
| 452 | % Igbo | 1.10 | 1.08 | Scaled down by 0.9804 (sum was 102.00) |
| 452 | % Nupe | 1.10 | 1.08 | Scaled down by 0.9804 (sum was 102.00) |
| 452 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 452 | % Hausa | 71.08 | 71.07 | Rounding adjustment of -0.01 |
| 453 | % Hausa | 70.20 | 68.82 | Scaled down by 0.9804 (sum was 102.00) |
| 453 | % Fulani | 29.80 | 29.22 | Scaled down by 0.9804 (sum was 102.00) |
| 453 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 454 | % Other | 4.00 | 33.00 | Added 29.00 deficit to % Other (sum was 71.00) |
| 455 | % Other | 0.00 | 17.00 | Added 17.00 deficit to % Other (sum was 83.00) |
| 456 | % Hausa | 73.90 | 71.75 | Scaled down by 0.9709 (sum was 103.00) |
| 456 | % Fulani | 26.10 | 25.34 | Scaled down by 0.9709 (sum was 103.00) |
| 456 | % Other | 3.00 | 2.91 | Scaled down by 0.9709 (sum was 103.00) |
| 457 | % Other | 4.00 | 47.00 | Added 43.00 deficit to % Other (sum was 57.00) |
| 458 | % Other | 4.00 | 80.00 | Added 76.00 deficit to % Other (sum was 24.00) |
| 459 | % Other | 2.00 | 4.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 462 | % Other | 4.00 | 15.00 | Added 11.00 deficit to % Other (sum was 89.00) |
| 463 | % Hausa | 73.90 | 71.06 | Scaled down by 0.9615 (sum was 104.00) |
| 463 | % Fulani | 26.10 | 25.10 | Scaled down by 0.9615 (sum was 104.00) |
| 463 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 463 | % Hausa | 71.06 | 71.05 | Rounding adjustment of -0.01 |
| 464 | % Other | 3.00 | 43.00 | Added 40.00 deficit to % Other (sum was 60.00) |
| 465 | % Other | 5.00 | 75.00 | Added 70.00 deficit to % Other (sum was 30.00) |
| 466 | % Other | 3.00 | 66.00 | Added 63.00 deficit to % Other (sum was 37.00) |
| 467 | % Hausa | 65.90 | 63.37 | Scaled down by 0.9615 (sum was 104.00) |
| 467 | % Fulani | 34.10 | 32.79 | Scaled down by 0.9615 (sum was 104.00) |
| 467 | % Other | 4.00 | 3.85 | Scaled down by 0.9615 (sum was 104.00) |
| 467 | % Hausa | 63.37 | 63.36 | Rounding adjustment of -0.01 |
| 468 | % Other | 7.00 | 75.00 | Added 68.00 deficit to % Other (sum was 32.00) |
| 469 | % Other | 3.00 | 51.00 | Added 48.00 deficit to % Other (sum was 52.00) |
| 470 | % Other | 2.00 | 78.00 | Added 76.00 deficit to % Other (sum was 24.00) |
| 471 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 472 | % Other | 8.00 | 18.00 | Added 10.00 deficit to % Other (sum was 90.00) |
| 473 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 474 | % Other | 3.00 | 73.00 | Added 70.00 deficit to % Other (sum was 30.00) |
| 475 | % Other | 2.00 | 5.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 477 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 478 | % Other | 0.00 | 4.00 | Added 4.00 deficit to % Other (sum was 96.00) |
| 479 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 480 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 481 | % Other | 5.00 | 22.00 | Added 17.00 deficit to % Other (sum was 83.00) |
| 482 | % Other | 10.00 | 25.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 483 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 484 | % Other | 0.00 | 3.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 485 | % Other | 6.00 | 80.00 | Added 74.00 deficit to % Other (sum was 26.00) |
| 488 | % Other | 0.00 | 3.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 489 | % Hausa | 3.20 | 3.10 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Fulani | 2.20 | 2.13 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Igbo | 1.10 | 1.07 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Nupe | 3.20 | 3.10 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Igala | 88.20 | 85.55 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Ebira | 2.20 | 2.13 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Other | 3.00 | 2.91 | Scaled down by 0.9699 (sum was 103.10) |
| 489 | % Igala | 85.55 | 85.56 | Rounding adjustment of +0.01 |
| 490 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 491 | % Other | 0.00 | 2.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 493 | % Other | 3.00 | 78.00 | Added 75.00 deficit to % Other (sum was 25.00) |
| 494 | % Hausa | 4.30 | 4.17 | Scaled down by 0.9709 (sum was 103.00) |
| 494 | % Fulani | 3.30 | 3.20 | Scaled down by 0.9709 (sum was 103.00) |
| 494 | % Yoruba | 6.50 | 6.31 | Scaled down by 0.9709 (sum was 103.00) |
| 494 | % Igbo | 1.10 | 1.07 | Scaled down by 0.9709 (sum was 103.00) |
| 494 | % Nupe | 84.80 | 82.33 | Scaled down by 0.9709 (sum was 103.00) |
| 494 | % Other | 3.00 | 2.91 | Scaled down by 0.9709 (sum was 103.00) |
| 494 | % Nupe | 82.33 | 82.34 | Rounding adjustment of +0.01 |
| 497 | % Hausa | 6.60 | 6.23 | Scaled down by 0.9434 (sum was 106.00) |
| 497 | % Fulani | 11.00 | 10.38 | Scaled down by 0.9434 (sum was 106.00) |
| 497 | % Yoruba | 74.70 | 70.47 | Scaled down by 0.9434 (sum was 106.00) |
| 497 | % Igbo | 3.30 | 3.11 | Scaled down by 0.9434 (sum was 106.00) |
| 497 | % Nupe | 4.40 | 4.15 | Scaled down by 0.9434 (sum was 106.00) |
| 497 | % Other | 6.00 | 5.66 | Scaled down by 0.9434 (sum was 106.00) |
| 498 | % Hausa | 7.70 | 7.20 | Scaled down by 0.9346 (sum was 107.00) |
| 498 | % Fulani | 11.00 | 10.28 | Scaled down by 0.9346 (sum was 107.00) |
| 498 | % Yoruba | 73.60 | 68.79 | Scaled down by 0.9346 (sum was 107.00) |
| 498 | % Igbo | 3.30 | 3.08 | Scaled down by 0.9346 (sum was 107.00) |
| 498 | % Nupe | 4.40 | 4.11 | Scaled down by 0.9346 (sum was 107.00) |
| 498 | % Other | 7.00 | 6.54 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Hausa | 8.80 | 8.22 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Fulani | 11.00 | 10.28 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Yoruba | 71.40 | 66.73 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Igbo | 3.30 | 3.08 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Nupe | 5.50 | 5.14 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Other | 7.00 | 6.54 | Scaled down by 0.9346 (sum was 107.00) |
| 499 | % Yoruba | 66.73 | 66.74 | Rounding adjustment of +0.01 |
| 502 | % Other | 3.00 | 50.00 | Added 47.00 deficit to % Other (sum was 53.00) |
| 503 | % Other | 3.00 | 5.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 508 | % Hausa | 10.90 | 10.29 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Fulani | 1.10 | 1.04 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Hausa Fulani Undiff | 2.20 | 2.08 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Yoruba | 60.10 | 56.75 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Igbo | 15.30 | 14.45 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Ijaw | 0.50 | 0.47 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Ibibio | 0.50 | 0.47 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Nupe | 3.30 | 3.12 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Edo Bini | 2.20 | 2.08 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Urhobo | 0.50 | 0.47 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Igala | 1.10 | 1.04 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Ebira | 2.20 | 2.08 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Other | 6.00 | 5.67 | Scaled down by 0.9443 (sum was 105.90) |
| 508 | % Yoruba | 56.75 | 56.74 | Rounding adjustment of -0.01 |
| 509 | % Hausa | 3.30 | 3.11 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Fulani | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Hausa Fulani Undiff | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Yoruba | 33.30 | 31.39 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Igbo | 33.30 | 31.39 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Ijaw | 11.10 | 10.46 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Ibibio | 1.70 | 1.60 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Efik | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Nupe | 1.10 | 1.04 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Edo Bini | 6.70 | 6.31 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Urhobo | 3.30 | 3.11 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Itsekiri | 1.10 | 1.04 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Isoko | 1.10 | 1.04 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Igala | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Idoma | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Ebira | 1.10 | 1.04 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Other | 6.00 | 5.66 | Scaled down by 0.9425 (sum was 106.10) |
| 509 | % Yoruba | 31.39 | 31.35 | Rounding adjustment of -0.04 |
| 510 | % Hausa | 3.30 | 3.15 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Fulani | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Hausa Fulani Undiff | 1.60 | 1.53 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Yoruba | 74.30 | 70.90 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Igbo | 10.90 | 10.40 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Ijaw | 1.10 | 1.05 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Ibibio | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Nupe | 1.60 | 1.53 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Edo Bini | 2.20 | 2.10 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Urhobo | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Igala | 1.10 | 1.05 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Ebira | 2.20 | 2.10 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Other | 5.00 | 4.77 | Scaled down by 0.9542 (sum was 104.80) |
| 510 | % Yoruba | 70.90 | 70.88 | Rounding adjustment of -0.02 |
| 511 | % Hausa | 2.30 | 2.11 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Fulani | 0.60 | 0.55 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Hausa Fulani Undiff | 0.60 | 0.55 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Yoruba | 45.50 | 41.70 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Igbo | 28.40 | 26.03 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Ijaw | 6.80 | 6.23 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Ibibio | 1.70 | 1.56 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Efik | 0.60 | 0.55 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Nupe | 1.10 | 1.01 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Edo Bini | 4.50 | 4.12 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Urhobo | 4.00 | 3.67 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Itsekiri | 1.10 | 1.01 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Isoko | 0.60 | 0.55 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Igala | 0.60 | 0.55 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Idoma | 0.60 | 0.55 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Ebira | 1.10 | 1.01 | Scaled down by 0.9166 (sum was 109.10) |
| 511 | % Other | 9.00 | 8.25 | Scaled down by 0.9166 (sum was 109.10) |
| 512 | % Hausa | 4.50 | 4.13 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Fulani | 0.60 | 0.55 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Hausa Fulani Undiff | 1.10 | 1.01 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Yoruba | 43.20 | 39.63 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Igbo | 25.00 | 22.94 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Ijaw | 4.50 | 4.13 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Ibibio | 2.30 | 2.11 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Efik | 0.60 | 0.55 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Nupe | 2.30 | 2.11 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Edo Bini | 6.80 | 6.24 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Urhobo | 3.40 | 3.12 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Itsekiri | 1.70 | 1.56 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Isoko | 0.60 | 0.55 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Igala | 1.10 | 1.01 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Idoma | 0.60 | 0.55 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Ebira | 1.70 | 1.56 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Other | 9.00 | 8.26 | Scaled down by 0.9174 (sum was 109.00) |
| 512 | % Yoruba | 39.63 | 39.62 | Rounding adjustment of -0.01 |
| 513 | % Other | 4.00 | 56.00 | Added 52.00 deficit to % Other (sum was 48.00) |
| 514 | % Hausa | 0.50 | 0.49 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Yoruba | 95.20 | 92.52 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Igbo | 2.10 | 2.04 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Ijaw | 1.10 | 1.07 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Nupe | 0.50 | 0.49 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Edo Bini | 0.50 | 0.49 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Other | 3.00 | 2.92 | Scaled down by 0.9718 (sum was 102.90) |
| 514 | % Yoruba | 92.52 | 92.50 | Rounding adjustment of -0.02 |
| 515 | % Other | 0.00 | 15.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 516 | % Hausa | 0.50 | 0.48 | Scaled down by 0.9625 (sum was 103.90) |
| 516 | % Yoruba | 94.10 | 90.57 | Scaled down by 0.9625 (sum was 103.90) |
| 516 | % Igbo | 3.20 | 3.08 | Scaled down by 0.9625 (sum was 103.90) |
| 516 | % Ijaw | 1.10 | 1.06 | Scaled down by 0.9625 (sum was 103.90) |
| 516 | % Nupe | 0.50 | 0.48 | Scaled down by 0.9625 (sum was 103.90) |
| 516 | % Edo Bini | 0.50 | 0.48 | Scaled down by 0.9625 (sum was 103.90) |
| 516 | % Other | 4.00 | 3.85 | Scaled down by 0.9625 (sum was 103.90) |
| 517 | % Hausa | 3.30 | 3.15 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Fulani | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Hausa Fulani Undiff | 1.60 | 1.53 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Yoruba | 76.10 | 72.61 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Igbo | 10.90 | 10.40 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Ijaw | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Ibibio | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Nupe | 1.60 | 1.53 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Edo Bini | 1.60 | 1.53 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Urhobo | 0.50 | 0.48 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Igala | 1.10 | 1.05 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Ebira | 1.60 | 1.53 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Other | 5.00 | 4.77 | Scaled down by 0.9542 (sum was 104.80) |
| 517 | % Yoruba | 72.61 | 72.59 | Rounding adjustment of -0.02 |
| 519 | % Hausa | 1.10 | 1.07 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Fulani | 0.50 | 0.49 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Hausa Fulani Undiff | 0.50 | 0.49 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Yoruba | 86.80 | 84.27 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Igbo | 5.30 | 5.15 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Ijaw | 1.60 | 1.55 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Ibibio | 0.50 | 0.49 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Nupe | 1.10 | 1.07 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Edo Bini | 1.10 | 1.07 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Urhobo | 0.50 | 0.49 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Igala | 0.50 | 0.49 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Ebira | 0.50 | 0.49 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Other | 3.00 | 2.91 | Scaled down by 0.9709 (sum was 103.00) |
| 519 | % Yoruba | 84.27 | 84.24 | Rounding adjustment of -0.03 |
| 520 | % Hausa | 3.40 | 3.17 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Fulani | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Hausa Fulani Undiff | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Yoruba | 67.00 | 62.56 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Igbo | 15.60 | 14.57 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Ijaw | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Ibibio | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Efik | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Nupe | 1.70 | 1.59 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Edo Bini | 2.80 | 2.61 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Urhobo | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Itsekiri | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Igala | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Idoma | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Ebira | 1.70 | 1.59 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Other | 7.00 | 6.54 | Scaled down by 0.9337 (sum was 107.10) |
| 520 | % Yoruba | 62.56 | 62.54 | Rounding adjustment of -0.02 |
| 521 | % Hausa | 5.70 | 5.17 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Fulani | 0.60 | 0.54 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Hausa Fulani Undiff | 1.70 | 1.54 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Yoruba | 39.80 | 36.12 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Igbo | 31.80 | 28.86 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Ijaw | 2.30 | 2.09 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Ibibio | 2.30 | 2.09 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Efik | 0.60 | 0.54 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Nupe | 2.30 | 2.09 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Edo Bini | 5.70 | 5.17 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Urhobo | 2.30 | 2.09 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Itsekiri | 1.10 | 1.00 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Isoko | 0.60 | 0.54 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Igala | 1.10 | 1.00 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Idoma | 0.60 | 0.54 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Ebira | 1.70 | 1.54 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Other | 10.00 | 9.07 | Scaled down by 0.9074 (sum was 110.20) |
| 521 | % Yoruba | 36.12 | 36.13 | Rounding adjustment of +0.01 |
| 522 | % Other | 1.00 | 13.00 | Added 12.00 deficit to % Other (sum was 88.00) |
| 523 | % Hausa | 5.50 | 5.03 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Fulani | 0.60 | 0.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Hausa Fulani Undiff | 1.70 | 1.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Yoruba | 57.50 | 52.56 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Igbo | 19.90 | 18.19 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Ijaw | 1.10 | 1.01 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Ibibio | 1.70 | 1.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Efik | 0.60 | 0.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Nupe | 2.20 | 2.01 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Edo Bini | 3.30 | 3.02 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Urhobo | 1.70 | 1.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Itsekiri | 0.60 | 0.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Isoko | 0.60 | 0.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Igala | 1.10 | 1.01 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Idoma | 0.60 | 0.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Ebira | 1.70 | 1.55 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Other | 9.00 | 8.23 | Scaled down by 0.9141 (sum was 109.40) |
| 523 | % Yoruba | 52.56 | 52.55 | Rounding adjustment of -0.01 |
| 524 | % Hausa | 2.80 | 2.61 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Fulani | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Hausa Fulani Undiff | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Yoruba | 62.50 | 58.36 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Igbo | 20.50 | 19.14 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Ijaw | 2.30 | 2.15 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Ibibio | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Efik | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Nupe | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Edo Bini | 2.30 | 2.15 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Urhobo | 1.70 | 1.59 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Itsekiri | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Isoko | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Igala | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Idoma | 0.60 | 0.56 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Ebira | 1.10 | 1.03 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Other | 7.00 | 6.54 | Scaled down by 0.9337 (sum was 107.10) |
| 524 | % Yoruba | 58.36 | 58.34 | Rounding adjustment of -0.02 |
| 525 | % Hausa | 3.90 | 3.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Fulani | 0.60 | 0.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Hausa Fulani Undiff | 1.10 | 1.00 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Yoruba | 55.60 | 50.41 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Igbo | 22.20 | 20.13 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Ijaw | 1.70 | 1.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Ibibio | 1.70 | 1.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Efik | 0.60 | 0.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Nupe | 2.20 | 1.99 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Edo Bini | 3.90 | 3.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Urhobo | 2.20 | 1.99 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Itsekiri | 0.60 | 0.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Isoko | 0.60 | 0.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Igala | 1.10 | 1.00 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Idoma | 0.60 | 0.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Ebira | 1.70 | 1.54 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Other | 10.00 | 9.07 | Scaled down by 0.9066 (sum was 110.30) |
| 525 | % Yoruba | 50.41 | 50.42 | Rounding adjustment of +0.01 |
| 526 | % Hausa | 3.40 | 3.14 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Fulani | 0.60 | 0.55 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Hausa Fulani Undiff | 1.10 | 1.01 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Yoruba | 61.50 | 56.73 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Igbo | 20.10 | 18.54 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Ijaw | 1.10 | 1.01 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Ibibio | 1.70 | 1.57 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Efik | 0.60 | 0.55 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Nupe | 1.70 | 1.57 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Edo Bini | 3.40 | 3.14 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Urhobo | 1.70 | 1.57 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Itsekiri | 0.60 | 0.55 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Isoko | 0.60 | 0.55 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Igala | 0.60 | 0.55 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Idoma | 0.60 | 0.55 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Ebira | 1.10 | 1.01 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Other | 8.00 | 7.38 | Scaled down by 0.9225 (sum was 108.40) |
| 526 | % Yoruba | 56.73 | 56.76 | Rounding adjustment of +0.03 |
| 528 | % Other | 6.00 | 85.00 | Added 79.00 deficit to % Other (sum was 21.00) |
| 529 | % Other | 7.00 | 27.00 | Added 20.00 deficit to % Other (sum was 80.00) |
| 530 | % Other | 8.00 | 53.00 | Added 45.00 deficit to % Other (sum was 55.00) |
| 531 | % Other | 14.00 | 42.00 | Added 28.00 deficit to % Other (sum was 72.00) |
| 532 | % Other | 7.00 | 57.00 | Added 50.00 deficit to % Other (sum was 50.00) |
| 533 | % Other | 15.00 | 61.00 | Added 46.00 deficit to % Other (sum was 54.00) |
| 534 | % Other | 15.00 | 83.00 | Added 68.00 deficit to % Other (sum was 32.00) |
| 535 | % Other | 16.00 | 57.00 | Added 41.00 deficit to % Other (sum was 59.00) |
| 536 | % Other | 8.00 | 54.00 | Added 46.00 deficit to % Other (sum was 54.00) |
| 537 | % Other | 9.00 | 87.00 | Added 78.00 deficit to % Other (sum was 22.00) |
| 538 | % Other | 11.00 | 54.00 | Added 43.00 deficit to % Other (sum was 57.00) |
| 539 | % Other | 5.00 | 27.00 | Added 22.00 deficit to % Other (sum was 78.00) |
| 540 | % Other | 10.00 | 82.00 | Added 72.00 deficit to % Other (sum was 28.00) |
| 541 | % Hausa | 3.30 | 3.27 | Scaled down by 0.9901 (sum was 101.00) |
| 541 | % Fulani | 5.50 | 5.45 | Scaled down by 0.9901 (sum was 101.00) |
| 541 | % Yoruba | 1.10 | 1.09 | Scaled down by 0.9901 (sum was 101.00) |
| 541 | % Nupe | 87.90 | 87.03 | Scaled down by 0.9901 (sum was 101.00) |
| 541 | % Gwari Gbagyi | 2.20 | 2.18 | Scaled down by 0.9901 (sum was 101.00) |
| 541 | % Other | 1.00 | 0.99 | Scaled down by 0.9901 (sum was 101.00) |
| 541 | % Nupe | 87.03 | 87.02 | Rounding adjustment of -0.01 |
| 542 | % Other | 9.00 | 82.00 | Added 73.00 deficit to % Other (sum was 27.00) |
| 543 | % Other | 2.00 | 4.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 544 | % Other | 1.00 | 55.00 | Added 54.00 deficit to % Other (sum was 46.00) |
| 545 | % Other | 7.00 | 15.00 | Added 8.00 deficit to % Other (sum was 92.00) |
| 546 | % Other | 8.00 | 15.00 | Added 7.00 deficit to % Other (sum was 93.00) |
| 547 | % Hausa | 3.20 | 3.14 | Scaled down by 0.9804 (sum was 102.00) |
| 547 | % Fulani | 5.40 | 5.29 | Scaled down by 0.9804 (sum was 102.00) |
| 547 | % Nupe | 91.40 | 89.61 | Scaled down by 0.9804 (sum was 102.00) |
| 547 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 549 | % Other | 4.00 | 17.00 | Added 13.00 deficit to % Other (sum was 87.00) |
| 550 | % Hausa | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 550 | % Fulani | 5.50 | 5.39 | Scaled down by 0.9804 (sum was 102.00) |
| 550 | % Nupe | 87.90 | 86.18 | Scaled down by 0.9804 (sum was 102.00) |
| 550 | % Gwari Gbagyi | 3.30 | 3.24 | Scaled down by 0.9804 (sum was 102.00) |
| 550 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 550 | % Nupe | 86.18 | 86.17 | Rounding adjustment of -0.01 |
| 551 | % Other | 8.00 | 44.00 | Added 36.00 deficit to % Other (sum was 64.00) |
| 552 | % Hausa | 5.60 | 5.38 | Scaled down by 0.9606 (sum was 104.10) |
| 552 | % Fulani | 5.60 | 5.38 | Scaled down by 0.9606 (sum was 104.10) |
| 552 | % Nupe | 50.00 | 48.03 | Scaled down by 0.9606 (sum was 104.10) |
| 552 | % Gwari Gbagyi | 38.90 | 37.37 | Scaled down by 0.9606 (sum was 104.10) |
| 552 | % Other | 4.00 | 3.84 | Scaled down by 0.9606 (sum was 104.10) |
| 553 | % Hausa | 3.20 | 3.11 | Scaled down by 0.9709 (sum was 103.00) |
| 553 | % Fulani | 5.30 | 5.15 | Scaled down by 0.9709 (sum was 103.00) |
| 553 | % Yoruba | 1.10 | 1.07 | Scaled down by 0.9709 (sum was 103.00) |
| 553 | % Nupe | 90.40 | 87.77 | Scaled down by 0.9709 (sum was 103.00) |
| 553 | % Other | 3.00 | 2.91 | Scaled down by 0.9709 (sum was 103.00) |
| 553 | % Nupe | 87.77 | 87.76 | Rounding adjustment of -0.01 |
| 554 | % Other | 14.00 | 72.00 | Added 58.00 deficit to % Other (sum was 42.00) |
| 555 | % Other | 10.00 | 65.00 | Added 55.00 deficit to % Other (sum was 45.00) |
| 556 | % Other | 12.00 | 50.00 | Added 38.00 deficit to % Other (sum was 62.00) |
| 557 | % Hausa | 5.60 | 5.44 | Scaled down by 0.9709 (sum was 103.00) |
| 557 | % Fulani | 5.60 | 5.44 | Scaled down by 0.9709 (sum was 103.00) |
| 557 | % Yoruba | 3.40 | 3.30 | Scaled down by 0.9709 (sum was 103.00) |
| 557 | % Igbo | 1.10 | 1.07 | Scaled down by 0.9709 (sum was 103.00) |
| 557 | % Nupe | 84.30 | 81.84 | Scaled down by 0.9709 (sum was 103.00) |
| 557 | % Other | 3.00 | 2.91 | Scaled down by 0.9709 (sum was 103.00) |
| 558 | % Other | 5.00 | 20.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 559 | % Other | 4.00 | 8.00 | Added 4.00 deficit to % Other (sum was 96.00) |
| 560 | % Other | 9.00 | 14.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 561 | % Other | 14.00 | 74.00 | Added 60.00 deficit to % Other (sum was 40.00) |
| 562 | % Other | 4.00 | 16.00 | Added 12.00 deficit to % Other (sum was 88.00) |
| 563 | % Other | 10.00 | 27.00 | Added 17.00 deficit to % Other (sum was 83.00) |
| 564 | % Other | 14.00 | 54.00 | Added 40.00 deficit to % Other (sum was 60.00) |
| 565 | % Other | 4.00 | 18.00 | Added 14.00 deficit to % Other (sum was 86.00) |
| 570 | % Hausa | 2.20 | 2.04 | Scaled down by 0.9259 (sum was 108.00) |
| 570 | % Fulani | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 570 | % Yoruba | 90.20 | 83.52 | Scaled down by 0.9259 (sum was 108.00) |
| 570 | % Igbo | 5.40 | 5.00 | Scaled down by 0.9259 (sum was 108.00) |
| 570 | % Nupe | 1.10 | 1.02 | Scaled down by 0.9259 (sum was 108.00) |
| 570 | % Other | 8.00 | 7.41 | Scaled down by 0.9259 (sum was 108.00) |
| 570 | % Yoruba | 83.52 | 83.51 | Rounding adjustment of -0.01 |
| 576 | % Other | 2.00 | 6.00 | Added 4.00 deficit to % Other (sum was 96.00) |
| 577 | % Other | 2.00 | 7.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 584 | % Other | 2.00 | 4.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 585 | % Hausa | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 585 | % Fulani | 2.10 | 1.98 | Scaled down by 0.9434 (sum was 106.00) |
| 585 | % Yoruba | 95.70 | 90.28 | Scaled down by 0.9434 (sum was 106.00) |
| 585 | % Igbo | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 585 | % Egun/Ogu | 4.00 | 3.77 | Scaled down by 0.9434 (sum was 106.00) |
| 585 | % Other | 2.00 | 1.89 | Scaled down by 0.9434 (sum was 106.00) |
| 667 | % Other | 0.00 | 25.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 668 | % Other | 3.00 | 93.00 | Added 90.00 deficit to % Other (sum was 10.00) |
| 669 | % Other | 8.00 | 88.00 | Added 80.00 deficit to % Other (sum was 20.00) |
| 670 | % Other | 0.00 | 75.00 | Added 75.00 deficit to % Other (sum was 25.00) |
| 671 | % Other | 8.00 | 28.00 | Added 20.00 deficit to % Other (sum was 80.00) |
| 672 | % Other | 5.00 | 20.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 673 | % Other | 0.00 | 72.00 | Added 72.00 deficit to % Other (sum was 28.00) |
| 674 | % Other | 3.00 | 18.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 675 | % Other | 2.00 | 15.00 | Added 13.00 deficit to % Other (sum was 87.00) |
| 676 | % Other | 2.00 | 37.00 | Added 35.00 deficit to % Other (sum was 65.00) |
| 677 | % Other | 5.00 | 85.00 | Added 80.00 deficit to % Other (sum was 20.00) |
| 678 | % Other | 2.00 | 87.00 | Added 85.00 deficit to % Other (sum was 15.00) |
| 679 | % Other | 6.00 | 57.00 | Added 51.00 deficit to % Other (sum was 49.00) |
| 680 | % Other | 5.00 | 90.00 | Added 85.00 deficit to % Other (sum was 15.00) |
| 681 | % Other | 2.00 | 37.00 | Added 35.00 deficit to % Other (sum was 65.00) |
| 682 | % Other | 1.00 | 79.00 | Added 78.00 deficit to % Other (sum was 22.00) |
| 683 | % Other | 6.00 | 41.00 | Added 35.00 deficit to % Other (sum was 65.00) |
| 684 | % Other | 5.00 | 90.00 | Added 85.00 deficit to % Other (sum was 15.00) |
| 685 | % Other | 7.00 | 82.00 | Added 75.00 deficit to % Other (sum was 25.00) |
| 686 | % Other | 9.00 | 58.50 | Added 49.50 deficit to % Other (sum was 50.50) |
| 687 | % Hausa | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Fulani | 0.20 | 0.19 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Yoruba | 0.60 | 0.57 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Igbo | 3.40 | 3.20 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Ijaw | 95.00 | 89.54 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Ibibio | 0.30 | 0.28 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Other | 6.00 | 5.66 | Scaled down by 0.9425 (sum was 106.10) |
| 687 | % Ijaw | 89.54 | 89.53 | Rounding adjustment of -0.01 |
| 688 | % Other | 3.00 | 91.30 | Added 88.30 deficit to % Other (sum was 11.70) |
| 689 | % Hausa | 0.60 | 0.56 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Fulani | 0.20 | 0.19 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Yoruba | 0.60 | 0.56 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Igbo | 3.40 | 3.15 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Ijaw | 95.00 | 87.88 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Ibibio | 0.30 | 0.28 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Other | 8.00 | 7.40 | Scaled down by 0.9251 (sum was 108.10) |
| 689 | % Ijaw | 87.88 | 87.86 | Rounding adjustment of -0.02 |
| 691 | % Other | 7.00 | 32.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 692 | % Other | 4.00 | 82.20 | Added 78.20 deficit to % Other (sum was 21.80) |
| 695 | % Hausa | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Fulani | 0.20 | 0.19 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Yoruba | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Igbo | 3.20 | 2.99 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Ijaw | 1.10 | 1.03 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Ibibio | 0.30 | 0.28 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Ogoni | 94.10 | 88.03 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Other | 7.00 | 6.55 | Scaled down by 0.9355 (sum was 106.90) |
| 695 | % Ogoni | 88.03 | 88.02 | Rounding adjustment of -0.01 |
| 697 | % Hausa | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Fulani | 0.20 | 0.19 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Yoruba | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Igbo | 3.20 | 2.99 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Ijaw | 1.10 | 1.03 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Ibibio | 0.30 | 0.28 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Ogoni | 94.10 | 88.03 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Other | 7.00 | 6.55 | Scaled down by 0.9355 (sum was 106.90) |
| 697 | % Ogoni | 88.03 | 88.02 | Rounding adjustment of -0.01 |
| 698 | % Other | 5.00 | 16.00 | Added 11.00 deficit to % Other (sum was 89.00) |
| 699 | % Other | 6.00 | 75.50 | Added 69.50 deficit to % Other (sum was 30.50) |
| 700 | % Hausa | 0.50 | 0.46 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Fulani | 0.20 | 0.18 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Yoruba | 0.50 | 0.46 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Igbo | 4.40 | 4.04 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Ijaw | 92.90 | 85.31 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Ibibio | 0.30 | 0.28 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Ogoni | 1.10 | 1.01 | Scaled down by 0.9183 (sum was 108.90) |
| 700 | % Other | 9.00 | 8.26 | Scaled down by 0.9183 (sum was 108.90) |
| 701 | % Hausa | 1.10 | 1.00 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Fulani | 0.30 | 0.27 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Yoruba | 1.10 | 1.00 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Igbo | 5.50 | 5.00 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Ijaw | 90.80 | 82.55 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Ibibio | 0.60 | 0.55 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Ogoni | 0.60 | 0.55 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Other | 10.00 | 9.09 | Scaled down by 0.9091 (sum was 110.00) |
| 701 | % Ijaw | 82.55 | 82.54 | Rounding adjustment of -0.01 |
| 703 | % Hausa | 0.30 | 0.29 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Yoruba | 0.30 | 0.29 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Igbo | 3.30 | 3.14 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Ijaw | 92.70 | 88.29 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Ibibio | 2.20 | 2.10 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Ogoni | 1.10 | 1.05 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Other | 5.00 | 4.76 | Scaled down by 0.9524 (sum was 105.00) |
| 703 | % Ijaw | 88.29 | 88.27 | Rounding adjustment of -0.02 |
| 704 | % Other | 4.00 | 13.70 | Added 9.70 deficit to % Other (sum was 90.30) |
| 705 | % Other | 8.00 | 19.00 | Added 11.00 deficit to % Other (sum was 89.00) |
| 706 | % Hausa | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Fulani | 0.20 | 0.19 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Yoruba | 0.50 | 0.47 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Igbo | 3.20 | 2.99 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Ijaw | 1.10 | 1.03 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Ibibio | 0.30 | 0.28 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Ogoni | 94.10 | 88.03 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Other | 7.00 | 6.55 | Scaled down by 0.9355 (sum was 106.90) |
| 706 | % Ogoni | 88.03 | 88.02 | Rounding adjustment of -0.01 |
| 707 | % Other | 1.00 | 3.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 710 | % Hausa | 73.90 | 68.43 | Scaled down by 0.9259 (sum was 108.00) |
| 710 | % Fulani | 26.10 | 24.17 | Scaled down by 0.9259 (sum was 108.00) |
| 710 | % Zabarmawa | 5.00 | 4.63 | Scaled down by 0.9259 (sum was 108.00) |
| 710 | % Tuareg | 1.00 | 0.93 | Scaled down by 0.9259 (sum was 108.00) |
| 710 | % Other | 2.00 | 1.85 | Scaled down by 0.9259 (sum was 108.00) |
| 710 | % Hausa | 68.43 | 68.42 | Rounding adjustment of -0.01 |
| 713 | % Other | 1.00 | 3.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 714 | % Hausa | 73.30 | 66.64 | Scaled down by 0.9091 (sum was 110.00) |
| 714 | % Fulani | 26.70 | 24.27 | Scaled down by 0.9091 (sum was 110.00) |
| 714 | % Zabarmawa | 6.00 | 5.45 | Scaled down by 0.9091 (sum was 110.00) |
| 714 | % Tuareg | 2.00 | 1.82 | Scaled down by 0.9091 (sum was 110.00) |
| 714 | % Other | 2.00 | 1.82 | Scaled down by 0.9091 (sum was 110.00) |
| 716 | % Hausa | 72.30 | 70.88 | Scaled down by 0.9804 (sum was 102.00) |
| 716 | % Fulani | 27.70 | 27.16 | Scaled down by 0.9804 (sum was 102.00) |
| 716 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 719 | % Hausa | 76.10 | 70.46 | Scaled down by 0.9259 (sum was 108.00) |
| 719 | % Fulani | 23.90 | 22.13 | Scaled down by 0.9259 (sum was 108.00) |
| 719 | % Zabarmawa | 4.00 | 3.70 | Scaled down by 0.9259 (sum was 108.00) |
| 719 | % Tuareg | 2.00 | 1.85 | Scaled down by 0.9259 (sum was 108.00) |
| 719 | % Other | 2.00 | 1.85 | Scaled down by 0.9259 (sum was 108.00) |
| 719 | % Hausa | 70.46 | 70.47 | Rounding adjustment of +0.01 |
| 720 | % Other | 2.00 | 4.00 | Added 2.00 deficit to % Other (sum was 98.00) |
| 722 | % Hausa | 68.10 | 64.25 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Fulani | 23.40 | 22.08 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Yoruba | 3.70 | 3.49 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Igbo | 2.70 | 2.55 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Kanuri | 0.50 | 0.47 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Nupe | 1.10 | 1.04 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Edo Bini | 0.50 | 0.47 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Zabarmawa | 1.00 | 0.94 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Kamuku | 1.00 | 0.94 | Scaled down by 0.9434 (sum was 106.00) |
| 722 | % Other | 4.00 | 3.77 | Scaled down by 0.9434 (sum was 106.00) |
| 723 | % Hausa | 69.90 | 69.14 | Scaled down by 0.9891 (sum was 101.10) |
| 723 | % Fulani | 22.60 | 22.35 | Scaled down by 0.9891 (sum was 101.10) |
| 723 | % Yoruba | 3.80 | 3.76 | Scaled down by 0.9891 (sum was 101.10) |
| 723 | % Igbo | 2.20 | 2.18 | Scaled down by 0.9891 (sum was 101.10) |
| 723 | % Kanuri | 0.50 | 0.49 | Scaled down by 0.9891 (sum was 101.10) |
| 723 | % Nupe | 1.10 | 1.09 | Scaled down by 0.9891 (sum was 101.10) |
| 723 | % Zabarmawa | 1.00 | 0.99 | Scaled down by 0.9891 (sum was 101.10) |
| 731 | % Other | 12.00 | 27.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 732 | % Other | 12.00 | 17.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 733 | % Other | 16.00 | 24.00 | Added 8.00 deficit to % Other (sum was 92.00) |
| 735 | % Other | 14.00 | 29.00 | Added 15.00 deficit to % Other (sum was 85.00) |
| 736 | % Other | 18.00 | 21.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 737 | % Other | 25.00 | 65.00 | Added 40.00 deficit to % Other (sum was 60.00) |
| 738 | % Other | 12.00 | 37.00 | Added 25.00 deficit to % Other (sum was 75.00) |
| 739 | % Other | 17.00 | 22.00 | Added 5.00 deficit to % Other (sum was 95.00) |
| 740 | % Other | 12.00 | 75.00 | Added 63.00 deficit to % Other (sum was 37.00) |
| 741 | % Other | 7.00 | 15.00 | Added 8.00 deficit to % Other (sum was 92.00) |
| 742 | % Other | 9.00 | 17.00 | Added 8.00 deficit to % Other (sum was 92.00) |
| 743 | % Other | 7.00 | 17.00 | Added 10.00 deficit to % Other (sum was 90.00) |
| 744 | % Other | 15.00 | 18.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 745 | % Other | 12.00 | 18.00 | Added 6.00 deficit to % Other (sum was 94.00) |
| 761 | % Hausa | 5.60 | 5.09 | Scaled down by 0.9083 (sum was 110.10) |
| 761 | % Fulani | 5.60 | 5.09 | Scaled down by 0.9083 (sum was 110.10) |
| 761 | % Kanuri | 77.80 | 70.66 | Scaled down by 0.9083 (sum was 110.10) |
| 761 | % Shuwa Arab | 11.10 | 10.08 | Scaled down by 0.9083 (sum was 110.10) |
| 761 | % Other | 10.00 | 9.08 | Scaled down by 0.9083 (sum was 110.10) |
| 762 | % Hausa | 8.90 | 8.09 | Scaled down by 0.9091 (sum was 110.00) |
| 762 | % Fulani | 5.60 | 5.09 | Scaled down by 0.9091 (sum was 110.00) |
| 762 | % Kanuri | 83.30 | 75.73 | Scaled down by 0.9091 (sum was 110.00) |
| 762 | % Shuwa Arab | 2.20 | 2.00 | Scaled down by 0.9091 (sum was 110.00) |
| 762 | % Other | 10.00 | 9.09 | Scaled down by 0.9091 (sum was 110.00) |
| 763 | % Other | 2.00 | 5.00 | Added 3.00 deficit to % Other (sum was 97.00) |
| 772 | % Hausa | 72.30 | 70.88 | Scaled down by 0.9804 (sum was 102.00) |
| 772 | % Fulani | 27.70 | 27.16 | Scaled down by 0.9804 (sum was 102.00) |
| 772 | % Other | 2.00 | 1.96 | Scaled down by 0.9804 (sum was 102.00) |
| 776 | % Hausa | 78.70 | 74.25 | Scaled down by 0.9434 (sum was 106.00) |
| 776 | % Fulani | 21.30 | 20.09 | Scaled down by 0.9434 (sum was 106.00) |
| 776 | % Zabarmawa | 4.00 | 3.77 | Scaled down by 0.9434 (sum was 106.00) |
| 776 | % Other | 2.00 | 1.89 | Scaled down by 0.9434 (sum was 106.00) |

## Religion Fixes (73 changes)

| Row | Column | Old | New | Note |
|-----|--------|-----|-----|------|
| 634 | % Muslim | NULL | 7.00 | Computed: 100 - 53.0 - 40.0 = 7.0 |
| 635 | % Muslim | NULL | 5.00 | Computed: 100 - 52.0 - 43.0 = 5.0 |
| 636 | % Muslim | NULL | 5.00 | Computed: 100 - 57.0 - 38.0 = 5.0 |
| 637 | % Muslim | NULL | 9.00 | Computed: 100 - 63.0 - 28.0 = 9.0 |
| 638 | % Muslim | NULL | 6.00 | Computed: 100 - 52.0 - 42.0 = 6.0 |
| 639 | % Muslim | NULL | 4.00 | Computed: 100 - 44.0 - 52.0 = 4.0 |
| 640 | % Muslim | NULL | 5.00 | Computed: 100 - 50.0 - 45.0 = 5.0 |
| 641 | % Muslim | NULL | 4.00 | Computed: 100 - 52.0 - 44.0 = 4.0 |
| 642 | % Muslim | NULL | 5.00 | Computed: 100 - 48.0 - 47.0 = 5.0 |
| 643 | % Muslim | NULL | 5.00 | Computed: 100 - 46.0 - 49.0 = 5.0 |
| 644 | % Muslim | NULL | 10.00 | Computed: 100 - 42.0 - 48.0 = 10.0 |
| 645 | % Muslim | NULL | 10.00 | Computed: 100 - 40.0 - 50.0 = 10.0 |
| 646 | % Muslim | NULL | 10.00 | Computed: 100 - 42.0 - 48.0 = 10.0 |
| 647 | % Muslim | NULL | 8.00 | Computed: 100 - 48.0 - 44.0 = 8.0 |
| 648 | % Muslim | NULL | 8.00 | Computed: 100 - 68.0 - 24.0 = 8.0 |
| 649 | % Muslim | NULL | 6.00 | Computed: 100 - 62.0 - 32.0 = 6.0 |
| 650 | % Muslim | NULL | 8.00 | Computed: 100 - 64.0 - 28.0 = 8.0 |
| 651 | % Muslim | NULL | 9.00 | Computed: 100 - 63.0 - 28.0 = 9.0 |
| 652 | % Muslim | NULL | 8.00 | Computed: 100 - 64.0 - 28.0 = 8.0 |
| 653 | % Muslim | NULL | 6.00 | Computed: 100 - 50.0 - 44.0 = 6.0 |
| 654 | % Muslim | NULL | 5.00 | Computed: 100 - 37.0 - 58.0 = 5.0 |
| 655 | % Muslim | NULL | 5.00 | Computed: 100 - 38.0 - 57.0 = 5.0 |
| 656 | % Muslim | NULL | 8.00 | Computed: 100 - 43.0 - 49.0 = 8.0 |
| 657 | % Muslim | NULL | 8.00 | Computed: 100 - 65.0 - 27.0 = 8.0 |
| 658 | % Muslim | NULL | 5.00 | Computed: 100 - 47.0 - 48.0 = 5.0 |
| 659 | % Muslim | NULL | 6.00 | Computed: 100 - 50.0 - 44.0 = 6.0 |
| 660 | % Muslim | NULL | 8.00 | Computed: 100 - 66.0 - 26.0 = 8.0 |
| 661 | % Muslim | NULL | 8.00 | Computed: 100 - 45.0 - 47.0 = 8.0 |
| 662 | % Muslim | NULL | 5.00 | Computed: 100 - 56.0 - 39.0 = 5.0 |
| 663 | % Muslim | NULL | 5.00 | Computed: 100 - 55.0 - 40.0 = 5.0 |
| 664 | % Muslim | NULL | 9.00 | Computed: 100 - 65.0 - 26.0 = 9.0 |
| 665 | % Muslim | NULL | 7.00 | Computed: 100 - 65.0 - 28.0 = 7.0 |
| 666 | % Muslim | NULL | 8.00 | Computed: 100 - 45.0 - 47.0 = 8.0 |
| 667 | % Muslim | NULL | 5.00 | Computed: 100 - 8.0 - 87.0 = 5.0 |
| 668 | % Muslim | NULL | 7.00 | Computed: 100 - 20.0 - 73.0 = 7.0 |
| 669 | % Muslim | NULL | 7.00 | Computed: 100 - 8.0 - 85.0 = 7.0 |
| 670 | % Muslim | NULL | 7.00 | Computed: 100 - 25.0 - 68.0 = 7.0 |
| 671 | % Muslim | NULL | 5.00 | Computed: 100 - 45.0 - 50.0 = 5.0 |
| 672 | % Muslim | NULL | 5.00 | Computed: 100 - 18.0 - 77.0 = 5.0 |
| 673 | % Muslim | NULL | 7.00 | Computed: 100 - 55.0 - 38.0 = 7.0 |
| 674 | % Muslim | NULL | 8.00 | Computed: 100 - 10.0 - 82.0 = 8.0 |
| 675 | % Muslim | NULL | 7.00 | Computed: 100 - 5.0 - 88.0 = 7.0 |
| 676 | % Muslim | NULL | 7.00 | Computed: 100 - 5.0 - 88.0 = 7.0 |
| 677 | % Muslim | NULL | 7.00 | Computed: 100 - 15.0 - 78.0 = 7.0 |
| 678 | % Muslim | NULL | 8.00 | Computed: 100 - 4.0 - 88.0 = 8.0 |
| 679 | % Muslim | NULL | 8.00 | Computed: 100 - 10.0 - 82.0 = 8.0 |
| 680 | % Muslim | NULL | 8.00 | Computed: 100 - 5.0 - 87.0 = 8.0 |
| 681 | % Muslim | NULL | 7.00 | Computed: 100 - 6.0 - 87.0 = 7.0 |
| 682 | % Muslim | NULL | 7.00 | Computed: 100 - 18.0 - 75.0 = 7.0 |
| 683 | % Muslim | NULL | 7.00 | Computed: 100 - 58.0 - 35.0 = 7.0 |
| 684 | % Muslim | NULL | 8.00 | Computed: 100 - 2.0 - 90.0 = 8.0 |
| 685 | % Muslim | NULL | 4.00 | Computed: 100 - 2.0 - 94.0 = 4.0 |
| 686 | % Muslim | NULL | 5.00 | Computed: 100 - 2.0 - 93.0 = 5.0 |
| 687 | % Muslim | NULL | 10.00 | Computed: 100 - 2.0 - 88.0 = 10.0 |
| 688 | % Muslim | NULL | 10.00 | Computed: 100 - 2.0 - 88.0 = 10.0 |
| 689 | % Muslim | NULL | 9.00 | Computed: 100 - 2.0 - 89.0 = 9.0 |
| 690 | % Muslim | NULL | 7.00 | Computed: 100 - 2.0 - 91.0 = 7.0 |
| 691 | % Muslim | NULL | 9.00 | Computed: 100 - 2.0 - 89.0 = 9.0 |
| 692 | % Muslim | NULL | 5.00 | Computed: 100 - 2.0 - 93.0 = 5.0 |
| 693 | % Muslim | NULL | 6.00 | Computed: 100 - 2.0 - 92.0 = 6.0 |
| 694 | % Muslim | NULL | 4.00 | Computed: 100 - 2.0 - 94.0 = 4.0 |
| 695 | % Muslim | NULL | 6.00 | Computed: 100 - 2.0 - 92.0 = 6.0 |
| 696 | % Muslim | NULL | 5.00 | Computed: 100 - 3.0 - 92.0 = 5.0 |
| 697 | % Muslim | NULL | 6.00 | Computed: 100 - 2.0 - 92.0 = 6.0 |
| 698 | % Muslim | NULL | 5.00 | Computed: 100 - 8.0 - 87.0 = 5.0 |
| 699 | % Muslim | NULL | 5.00 | Computed: 100 - 3.0 - 92.0 = 5.0 |
| 700 | % Muslim | NULL | 8.00 | Computed: 100 - 2.0 - 90.0 = 8.0 |
| 701 | % Muslim | NULL | 9.00 | Computed: 100 - 2.0 - 89.0 = 9.0 |
| 702 | % Muslim | NULL | 4.00 | Computed: 100 - 2.0 - 94.0 = 4.0 |
| 703 | % Muslim | NULL | 9.00 | Computed: 100 - 2.0 - 89.0 = 9.0 |
| 704 | % Muslim | NULL | 4.00 | Computed: 100 - 4.0 - 92.0 = 4.0 |
| 705 | % Muslim | NULL | 5.00 | Computed: 100 - 10.0 - 85.0 = 5.0 |
| 706 | % Muslim | NULL | 5.00 | Computed: 100 - 2.0 - 93.0 = 5.0 |

## Median Age Fixes (35 changes)

| Row | Column | Old | New | Note |
|-----|--------|-----|-----|------|
| 100 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 102 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 105 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 112 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 154 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 156 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 158 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 165 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 168 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 169 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 322 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 323 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 328 | Median Age Estimate | 14.50 | 15.00 | Clamped from 14.5 to 15.0 |
| 331 | Median Age Estimate | 14.40 | 15.00 | Clamped from 14.4 to 15.0 |
| 333 | Median Age Estimate | 14.40 | 15.00 | Clamped from 14.4 to 15.0 |
| 335 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 336 | Median Age Estimate | 14.30 | 15.00 | Clamped from 14.3 to 15.0 |
| 337 | Median Age Estimate | 14.40 | 15.00 | Clamped from 14.4 to 15.0 |
| 338 | Median Age Estimate | 14.50 | 15.00 | Clamped from 14.5 to 15.0 |
| 343 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 345 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 347 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 348 | Median Age Estimate | 14.40 | 15.00 | Clamped from 14.4 to 15.0 |
| 461 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 465 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 468 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 747 | Median Age Estimate | 14.50 | 15.00 | Clamped from 14.5 to 15.0 |
| 753 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 757 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 758 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 759 | Median Age Estimate | 14.70 | 15.00 | Clamped from 14.7 to 15.0 |
| 760 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |
| 762 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 765 | Median Age Estimate | 14.80 | 15.00 | Clamped from 14.8 to 15.0 |
| 770 | Median Age Estimate | 14.90 | 15.00 | Clamped from 14.9 to 15.0 |

## Categorical Fixes (603 changes)

| Row | Column | Old | New | Note |
|-----|--------|-----|-----|------|
| 72 | Dominant Livelihood | subsistence farming, petty trade, transit commerce | Subsistence farming, petty trade, transit commerce | Capitalized first letter |
| 73 | Dominant Livelihood | farming, fishing, oil community work | Farming, fishing, oil community work | Capitalized first letter |
| 74 | Dominant Livelihood | subsistence farming, fishing | Subsistence farming, fishing | Capitalized first letter |
| 75 | Dominant Livelihood | farming, wood processing, trade | Farming, wood processing, trade | Capitalized first letter |
| 76 | Dominant Livelihood | farming, fishing, trading | Farming, fishing, trading | Capitalized first letter |
| 77 | Dominant Livelihood | government services, commerce, education | Government services, commerce, education | Capitalized first letter |
| 78 | Dominant Livelihood | subsistence farming, rice production, fishing | Subsistence farming, rice production, fishing | Capitalized first letter |
| 79 | Dominant Livelihood | farming, expressway commerce, petty trade | Farming, expressway commerce, petty trade | Capitalized first letter |
| 80 | Dominant Livelihood | fishing, trading, light manufacturing | Fishing, trading, light manufacturing | Capitalized first letter |
| 81 | Dominant Livelihood | commerce, trade, manufacturing, crafts | Commerce, trade, manufacturing, crafts | Capitalized first letter |
| 82 | Dominant Livelihood | trading, farming, commerce | Trading, farming, commerce | Capitalized first letter |
| 83 | Dominant Livelihood | agriculture, trade, small enterprise | Agriculture, trade, small enterprise | Capitalized first letter |
| 84 | Dominant Livelihood | trade, farming, timber processing | Trade, farming, timber processing | Capitalized first letter |
| 85 | Dominant Livelihood | manufacturing, auto parts, vehicle assembly | Manufacturing, auto parts, vehicle assembly | Capitalized first letter |
| 86 | Dominant Livelihood | farming, small-scale trade | Farming, small-scale trade | Capitalized first letter |
| 87 | Dominant Livelihood | farming, fishing, oil community work | Farming, fishing, oil community work | Capitalized first letter |
| 88 | Dominant Livelihood | wholesale trade, commerce, import distribution | Wholesale trade, commerce, import distribution | Capitalized first letter |
| 89 | Dominant Livelihood | commerce, manufacturing, hospitality | Commerce, manufacturing, hospitality | Capitalized first letter |
| 90 | Dominant Livelihood | farming, palm oil production, animal rearing | Farming, palm oil production, animal rearing | Capitalized first letter |
| 91 | Dominant Livelihood | farming, palm produce, petty trading | Farming, palm produce, petty trading | Capitalized first letter |
| 92 | Dominant Livelihood | farming, fishing, tourism, petty trade | Farming, fishing, tourism, petty trade | Capitalized first letter |
| 93 | Dominant Livelihood | farming, livestock, mining, pastoralism | Farming, livestock, mining, pastoralism | Capitalized first letter |
| 94 | Dominant Livelihood | civil service, commerce, agriculture, crafts | Civil service, commerce, agriculture, crafts | Capitalized first letter |
| 95 | Dominant Livelihood | livestock rearing, crop farming | Livestock rearing, crop farming | Capitalized first letter |
| 96 | Dominant Livelihood | subsistence farming, livestock herding | Subsistence farming, livestock herding | Capitalized first letter |
| 97 | Dominant Livelihood | farming, fishing, petty trade | Farming, fishing, petty trade | Capitalized first letter |
| 98 | Dominant Livelihood | rice and maize farming, mining, livestock | Rice and maize farming, mining, livestock | Capitalized first letter |
| 99 | Dominant Livelihood | subsistence farming, pastoralism | Subsistence farming, pastoralism | Capitalized first letter |
| 100 | Dominant Livelihood | farming, livestock, petty trade | Farming, livestock, petty trade | Capitalized first letter |
| 101 | Dominant Livelihood | subsistence farming, cash crops | Subsistence farming, cash crops | Capitalized first letter |
| 102 | Dominant Livelihood | subsistence farming, petty trade | Subsistence farming, petty trade | Capitalized first letter |
| 103 | Dominant Livelihood | farming, trade, fishing | Farming, trade, fishing | Capitalized first letter |
| 104 | Dominant Livelihood | commerce, agriculture, agro-processing, education | Commerce, agriculture, agro-processing, education | Capitalized first letter |
| 105 | Dominant Livelihood | farming, fishing along Gongola River | Farming, fishing along Gongola River | Capitalized first letter |
| 106 | Dominant Livelihood | farming, fishing, small-scale mining, trade | Farming, fishing, small-scale mining, trade | Capitalized first letter |
| 107 | Dominant Livelihood | farming, livestock, trade, mining | Farming, livestock, trade, mining | Capitalized first letter |
| 108 | Dominant Livelihood | subsistence farming, cash crops | Subsistence farming, cash crops | Capitalized first letter |
| 109 | Dominant Livelihood | farming, cotton, ginger, mining | Farming, cotton, ginger, mining | Capitalized first letter |
| 110 | Dominant Livelihood | farming, mining, livestock rearing | Farming, mining, livestock rearing | Capitalized first letter |
| 111 | Dominant Livelihood | farming, cassava, maize cultivation | Farming, cassava, maize cultivation | Capitalized first letter |
| 112 | Dominant Livelihood | subsistence farming, livestock herding | Subsistence farming, livestock herding | Capitalized first letter |
| 113 | Dominant Livelihood | fishing, farming, oil community work | Fishing, farming, oil community work | Capitalized first letter |
| 114 | Dominant Livelihood | fishing, farming, oil community work | Fishing, farming, oil community work | Capitalized first letter |
| 115 | Dominant Livelihood | farming, fishing, small-scale trade | Farming, fishing, small-scale trade | Capitalized first letter |
| 116 | Dominant Livelihood | fishing, farming, oil community work, trade | Fishing, farming, oil community work, trade | Capitalized first letter |
| 117 | Dominant Livelihood | fishing, farming, palm oil production | Fishing, farming, palm oil production | Capitalized first letter |
| 118 | Dominant Livelihood | farming, fishing, education sector | Farming, fishing, education sector | Capitalized first letter |
| 119 | Dominant Livelihood | fishing, farming, oil community work | Fishing, farming, oil community work | Capitalized first letter |
| 120 | Dominant Livelihood | government services, commerce, trade | Government services, commerce, trade | Capitalized first letter |
| 121 | Dominant Livelihood | subsistence farming, yams, cassava, rice | Subsistence farming, yams, cassava, rice | Capitalized first letter |
| 122 | Dominant Livelihood | farming, fishing; conflict-displaced livelihoods | Farming, fishing; conflict-displaced livelihoods | Capitalized first letter |
| 123 | Dominant Livelihood | subsistence farming, yams, cassava, fishing | Subsistence farming, yams, cassava, fishing | Capitalized first letter |
| 124 | Dominant Livelihood | subsistence farming, cassava, yams, fishing | Subsistence farming, cassava, yams, fishing | Capitalized first letter |
| 125 | Dominant Livelihood | commerce, cement industry, civil service, farming | Commerce, cement industry, civil service, farming | Capitalized first letter |
| 126 | Dominant Livelihood | farming, fishing; severely conflict-disrupted | Farming, fishing; severely conflict-disrupted | Capitalized first letter |
| 127 | Dominant Livelihood | farming, petty trade, cassava processing | Farming, petty trade, cassava processing | Capitalized first letter |
| 128 | Dominant Livelihood | farming, yams, cassava; conflict-disrupted | Farming, yams, cassava; conflict-disrupted | Capitalized first letter |
| 129 | Dominant Livelihood | farming, trade, fishing, small-scale commerce | Farming, trade, fishing, small-scale commerce | Capitalized first letter |
| 130 | Dominant Livelihood | subsistence farming, yams, cassava, soybeans | Subsistence farming, yams, cassava, soybeans | Capitalized first letter |
| 131 | Dominant Livelihood | farming, trade, yams, citrus, cassava | Farming, trade, yams, citrus, cassava | Capitalized first letter |
| 132 | Dominant Livelihood | farming, yams, cassava; conflict-disrupted | Farming, yams, cassava; conflict-disrupted | Capitalized first letter |
| 133 | Dominant Livelihood | civil service, commerce, petty trade, farming | Civil service, commerce, petty trade, farming | Capitalized first letter |
| 134 | Dominant Livelihood | subsistence farming, yams, rice, cassava | Subsistence farming, yams, rice, cassava | Capitalized first letter |
| 135 | Dominant Livelihood | farming, yams, cassava, palm oil production | Farming, yams, cassava, palm oil production | Capitalized first letter |
| 136 | Dominant Livelihood | subsistence farming, fishing, cassava, yams | Subsistence farming, fishing, cassava, yams | Capitalized first letter |
| 137 | Dominant Livelihood | subsistence farming, yams, cassava, palm produce | Subsistence farming, yams, cassava, palm produce | Capitalized first letter |
| 138 | Dominant Livelihood | farming, yams, cassava, rice, palm oil | Farming, yams, cassava, rice, palm oil | Capitalized first letter |
| 139 | Dominant Livelihood | commerce, civil service, farming, yam trade | Commerce, civil service, farming, yam trade | Capitalized first letter |
| 140 | Dominant Livelihood | farming, cassava, yams, soybeans, sesame | Farming, cassava, yams, soybeans, sesame | Capitalized first letter |
| 141 | Dominant Livelihood | farming, yam trade, soybeans, small commerce | Farming, yam trade, soybeans, small commerce | Capitalized first letter |
| 142 | Dominant Livelihood | farming, citrus, rice, cassava, grains | Farming, citrus, rice, cassava, grains | Capitalized first letter |
| 143 | Dominant Livelihood | farming, trade, citrus, palm oil, cassava | Farming, trade, citrus, palm oil, cassava | Capitalized first letter |
| 189 | Dominant Livelihood | subsistence farming, petty trade | Subsistence farming, petty trade | Capitalized first letter |
| 190 | Dominant Livelihood | farming, education, civil service | Farming, education, civil service | Capitalized first letter |
| 191 | Dominant Livelihood | fishing, oil-related work, farming | Fishing, oil-related work, farming | Capitalized first letter |
| 192 | Dominant Livelihood | fishing, oil work, subsistence farming | Fishing, oil work, subsistence farming | Capitalized first letter |
| 193 | Dominant Livelihood | mixed farming, oil-related services | Mixed farming, oil-related services | Capitalized first letter |
| 194 | Dominant Livelihood | farming, trade, rubber processing | Farming, trade, rubber processing | Capitalized first letter |
| 195 | Dominant Livelihood | farming, trade, commerce | Farming, trade, commerce | Capitalized first letter |
| 196 | Dominant Livelihood | subsistence farming, cassava processing | Subsistence farming, cassava processing | Capitalized first letter |
| 197 | Dominant Livelihood | farming, oil-related work, education | Farming, oil-related work, education | Capitalized first letter |
| 198 | Dominant Livelihood | farming, fishing, oil-related services | Farming, fishing, oil-related services | Capitalized first letter |
| 199 | Dominant Livelihood | farming, fishing, oil-related work | Farming, fishing, oil-related work | Capitalized first letter |
| 200 | Dominant Livelihood | farming, oil services, trading | Farming, oil services, trading | Capitalized first letter |
| 201 | Dominant Livelihood | oil services, farming, trading | Oil services, farming, trading | Capitalized first letter |
| 202 | Dominant Livelihood | farming, trade, civil service | Farming, trade, civil service | Capitalized first letter |
| 203 | Dominant Livelihood | government, commerce, services | Government, commerce, services | Capitalized first letter |
| 204 | Dominant Livelihood | fishing, farming, oil-related work | Fishing, farming, oil-related work | Capitalized first letter |
| 205 | Dominant Livelihood | timber, rubber, oil services, trade | Timber, rubber, oil services, trade | Capitalized first letter |
| 206 | Dominant Livelihood | commerce, oil services, manufacturing | Commerce, oil services, manufacturing | Capitalized first letter |
| 207 | Dominant Livelihood | oil production, farming, commerce | Oil production, farming, commerce | Capitalized first letter |
| 208 | Dominant Livelihood | oil production, farming, fishing | Oil production, farming, fishing | Capitalized first letter |
| 209 | Dominant Livelihood | farming, cassava processing, trading | Farming, cassava processing, trading | Capitalized first letter |
| 210 | Dominant Livelihood | commerce, oil services, manufacturing | Commerce, oil services, manufacturing | Capitalized first letter |
| 211 | Dominant Livelihood | fishing, oil production, water transport | Fishing, oil production, water transport | Capitalized first letter |
| 212 | Dominant Livelihood | oil industry hub, commerce, manufacturing | Oil industry hub, commerce, manufacturing | Capitalized first letter |
| 213 | Dominant Livelihood | fishing, oil production, water transport | Fishing, oil production, water transport | Capitalized first letter |
| 214 | Dominant Livelihood | government, commerce, rice farming, mining | Government, commerce, rice farming, mining | Capitalized first letter |
| 215 | Dominant Livelihood | farming, trade, fishing, palm produce | Farming, trade, fishing, palm produce | Capitalized first letter |
| 216 | Dominant Livelihood | farming, fishing along Cross River | Farming, fishing along Cross River | Capitalized first letter |
| 217 | Dominant Livelihood | farming, cassava, yam cultivation | Farming, cassava, yam cultivation | Capitalized first letter |
| 218 | Dominant Livelihood | farming, yam, cassava production | Farming, yam, cassava production | Capitalized first letter |
| 219 | Dominant Livelihood | farming, trade, civil service | Farming, trade, civil service | Capitalized first letter |
| 220 | Dominant Livelihood | rice farming, palm wine, fishing | Rice farming, palm wine, fishing | Capitalized first letter |
| 221 | Dominant Livelihood | farming, stone quarrying, limestone mining | Farming, stone quarrying, limestone mining | Capitalized first letter |
| 222 | Dominant Livelihood | mining, quarrying, farming | Mining, quarrying, farming | Capitalized first letter |
| 223 | Dominant Livelihood | farming, yam, cassava, rice production | Farming, yam, cassava, rice production | Capitalized first letter |
| 224 | Dominant Livelihood | salt mining, farming, trade | Salt mining, farming, trade | Capitalized first letter |
| 225 | Dominant Livelihood | farming, cross-border trade | Farming, cross-border trade | Capitalized first letter |
| 226 | Dominant Livelihood | farming, trade, fishing | Farming, trade, fishing | Capitalized first letter |
| 227 | Dominant Livelihood | farming, quarrying, trading, hunting | Farming, quarrying, trading, hunting | Capitalized first letter |
| 228 | Dominant Livelihood | residential, commerce, education, services | Residential, commerce, education, services | Capitalized first letter |
| 229 | Dominant Livelihood | farming, trade, healthcare services | Farming, trade, healthcare services | Capitalized first letter |
| 230 | Dominant Livelihood | trade, farming, artisanship, services | Trade, farming, artisanship, services | Capitalized first letter |
| 231 | Dominant Livelihood | farming, petty trading, civil service | Farming, petty trading, civil service | Capitalized first letter |
| 232 | Dominant Livelihood | education, farming, trade, services | Education, farming, trade, services | Capitalized first letter |
| 233 | Dominant Livelihood | farming, petty trading | Farming, petty trading | Capitalized first letter |
| 234 | Dominant Livelihood | farming, fishing, petty trading | Farming, fishing, petty trading | Capitalized first letter |
| 235 | Dominant Livelihood | education, trade, commerce, farming | Education, trade, commerce, farming | Capitalized first letter |
| 236 | Dominant Livelihood | farming, petty trading | Farming, petty trading | Capitalized first letter |
| 237 | Dominant Livelihood | commerce, industry, services, farming | Commerce, industry, services, farming | Capitalized first letter |
| 238 | Dominant Livelihood | government, commerce, trade, services | Government, commerce, trade, services | Capitalized first letter |
| 239 | Dominant Livelihood | farming, oil and gas, rubber, trading | Farming, oil and gas, rubber, trading | Capitalized first letter |
| 240 | Dominant Livelihood | farming, rubber, oil exploration, trade | Farming, rubber, oil exploration, trade | Capitalized first letter |
| 241 | Dominant Livelihood | rubber, farming, timber, palm oil | Rubber, farming, timber, palm oil | Capitalized first letter |
| 242 | Dominant Livelihood | farming, hunting, timber processing | Farming, hunting, timber processing | Capitalized first letter |
| 243 | Dominant Livelihood | farming, rubber, petty trading | Farming, rubber, petty trading | Capitalized first letter |
| 244 | Dominant Livelihood | rubber, farming, palm oil production | Rubber, farming, palm oil production | Capitalized first letter |
| 349 | Dominant Livelihood | subsistence farming, artisanal gold mining | Subsistence farming, artisanal gold mining | Capitalized first letter |
| 350 | Dominant Livelihood | peri-urban commerce, farming, livestock | Peri-urban commerce, farming, livestock | Capitalized first letter |
| 351 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 352 | Dominant Livelihood | commerce, transport, farming, military sector | Commerce, transport, farming, military sector | Capitalized first letter |
| 353 | Dominant Livelihood | subsistence farming, groundnuts, livestock | Subsistence farming, groundnuts, livestock | Capitalized first letter |
| 354 | Dominant Livelihood | subsistence farming, petty trade | Subsistence farming, petty trade | Capitalized first letter |
| 355 | Dominant Livelihood | farming, trade, tin mining | Farming, trade, tin mining | Capitalized first letter |
| 356 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 357 | Dominant Livelihood | government, commerce, manufacturing, services | Government, commerce, manufacturing, services | Capitalized first letter |
| 358 | Dominant Livelihood | commerce, manufacturing, refinery, services | Commerce, manufacturing, refinery, services | Capitalized first letter |
| 359 | Dominant Livelihood | farming, iron ore mining | Farming, iron ore mining | Capitalized first letter |
| 360 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 361 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 362 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 363 | Dominant Livelihood | subsistence farming, groundnuts, cereals | Subsistence farming, groundnuts, cereals | Capitalized first letter |
| 364 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 365 | Dominant Livelihood | subsistence farming, trade | Subsistence farming, trade | Capitalized first letter |
| 366 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 367 | Dominant Livelihood | education, commerce, services | Education, commerce, services | Capitalized first letter |
| 368 | Dominant Livelihood | subsistence farming, artisanal mining | Subsistence farming, artisanal mining | Capitalized first letter |
| 369 | Dominant Livelihood | subsistence farming, cereals, livestock | Subsistence farming, cereals, livestock | Capitalized first letter |
| 370 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 371 | Dominant Livelihood | education, commerce, government, crafts | Education, commerce, government, crafts | Capitalized first letter |
| 372 | Dominant Livelihood | subsistence farming, millet, cowpeas | Subsistence farming, millet, cowpeas | Capitalized first letter |
| 373 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 374 | Dominant Livelihood | farming, millet, rice, fishing | Farming, millet, rice, fishing | Capitalized first letter |
| 375 | Dominant Livelihood | subsistence farming, millet, livestock | Subsistence farming, millet, livestock | Capitalized first letter |
| 376 | Dominant Livelihood | farming, groundnuts, commerce | Farming, groundnuts, commerce | Capitalized first letter |
| 377 | Dominant Livelihood | irrigated farming, rice, groundnuts | Irrigated farming, rice, groundnuts | Capitalized first letter |
| 378 | Dominant Livelihood | commerce, traditional crafts, dyeing | Commerce, traditional crafts, dyeing | Capitalized first letter |
| 379 | Dominant Livelihood | farming, millet, sorghum, commerce | Farming, millet, sorghum, commerce | Capitalized first letter |
| 380 | Dominant Livelihood | farming, vegetables, peri-urban trade | Farming, vegetables, peri-urban trade | Capitalized first letter |
| 381 | Dominant Livelihood | grain trade, farming, international commerce | Grain trade, farming, international commerce | Capitalized first letter |
| 382 | Dominant Livelihood | farming, cattle rearing, artisanal mining | Farming, cattle rearing, artisanal mining | Capitalized first letter |
| 383 | Dominant Livelihood | commerce, wholesale, retail, transport | Commerce, wholesale, retail, transport | Capitalized first letter |
| 384 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 385 | Dominant Livelihood | subsistence farming, millet, cowpeas | Subsistence farming, millet, cowpeas | Capitalized first letter |
| 386 | Dominant Livelihood | irrigated farming, rice, vegetables | Irrigated farming, rice, vegetables | Capitalized first letter |
| 387 | Dominant Livelihood | farming, millet, sorghum, commerce | Farming, millet, sorghum, commerce | Capitalized first letter |
| 388 | Dominant Livelihood | farming, commodity trade, commerce | Farming, commodity trade, commerce | Capitalized first letter |
| 389 | Dominant Livelihood | commerce, education, services | Commerce, education, services | Capitalized first letter |
| 390 | Dominant Livelihood | farming, millet, sorghum, trade | Farming, millet, sorghum, trade | Capitalized first letter |
| 391 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 392 | Dominant Livelihood | commerce, government, tourism, crafts | Commerce, government, tourism, crafts | Capitalized first letter |
| 393 | Dominant Livelihood | farming, groundnuts, livestock, trade | Farming, groundnuts, livestock, trade | Capitalized first letter |
| 394 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 395 | Dominant Livelihood | farming, millet, sorghum, cotton | Farming, millet, sorghum, cotton | Capitalized first letter |
| 396 | Dominant Livelihood | manufacturing, commerce, farming | Manufacturing, commerce, farming | Capitalized first letter |
| 397 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 398 | Dominant Livelihood | irrigated rice and vegetable farming | Irrigated rice and vegetable farming | Capitalized first letter |
| 399 | Dominant Livelihood | farming, groundnuts, petty commerce | Farming, groundnuts, petty commerce | Capitalized first letter |
| 400 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 401 | Dominant Livelihood | farming, millet, cowpeas, commerce | Farming, millet, cowpeas, commerce | Capitalized first letter |
| 402 | Dominant Livelihood | commerce, manufacturing, government, banking | Commerce, manufacturing, government, banking | Capitalized first letter |
| 403 | Dominant Livelihood | farming, groundnuts, rice, commerce | Farming, groundnuts, rice, commerce | Capitalized first letter |
| 404 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 405 | Dominant Livelihood | farming, millet, cotton, artisanal mining | Farming, millet, cotton, artisanal mining | Capitalized first letter |
| 406 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 407 | Dominant Livelihood | subsistence farming, millet, cowpeas | Subsistence farming, millet, cowpeas | Capitalized first letter |
| 408 | Dominant Livelihood | farming, millet, sorghum, cotton | Farming, millet, sorghum, cotton | Capitalized first letter |
| 409 | Dominant Livelihood | commerce, services, residential | Commerce, services, residential | Capitalized first letter |
| 410 | Dominant Livelihood | farming, millet, groundnuts, commerce | Farming, millet, groundnuts, commerce | Capitalized first letter |
| 411 | Dominant Livelihood | subsistence farming, millet, groundnuts | Subsistence farming, millet, groundnuts | Capitalized first letter |
| 412 | Dominant Livelihood | subsistence farming, millet, cowpeas | Subsistence farming, millet, cowpeas | Capitalized first letter |
| 413 | Dominant Livelihood | urban commerce, peri-urban farming | Urban commerce, peri-urban farming | Capitalized first letter |
| 414 | Dominant Livelihood | farming, millet, groundnuts, commerce | Farming, millet, groundnuts, commerce | Capitalized first letter |
| 415 | Dominant Livelihood | livestock trading, farming, education | Livestock trading, farming, education | Capitalized first letter |
| 416 | Dominant Livelihood | farming, cotton, grain trade, fishing | Farming, cotton, grain trade, fishing | Capitalized first letter |
| 417 | Dominant Livelihood | farming, cattle rearing, suburban trade | Farming, cattle rearing, suburban trade | Capitalized first letter |
| 418 | Dominant Livelihood | subsistence farming, livestock, displaced | Subsistence farming, livestock, displaced | Capitalized first letter |
| 419 | Dominant Livelihood | subsistence farming, cross-border trade | Subsistence farming, cross-border trade | Capitalized first letter |
| 420 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 421 | Dominant Livelihood | farming, livestock trade, secondhand trade | Farming, livestock trade, secondhand trade | Capitalized first letter |
| 422 | Dominant Livelihood | subsistence farming, livestock, displaced | Subsistence farming, livestock, displaced | Capitalized first letter |
| 423 | Dominant Livelihood | farming, cotton, livestock, displaced | Farming, cotton, livestock, displaced | Capitalized first letter |
| 424 | Dominant Livelihood | farming, cotton, livestock | Farming, cotton, livestock | Capitalized first letter |
| 425 | Dominant Livelihood | commerce, farming, education, government | Commerce, farming, education, government | Capitalized first letter |
| 426 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 427 | Dominant Livelihood | farming, cotton, education, commerce | Farming, cotton, education, commerce | Capitalized first letter |
| 428 | Dominant Livelihood | farming, cotton, livestock, displaced | Farming, cotton, livestock, displaced | Capitalized first letter |
| 429 | Dominant Livelihood | commerce, cotton trade, manufacturing | Commerce, cotton trade, manufacturing | Capitalized first letter |
| 430 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 431 | Dominant Livelihood | cross-border trade, farming, livestock | Cross-border trade, farming, livestock | Capitalized first letter |
| 432 | Dominant Livelihood | farming, cotton, livestock | Farming, cotton, livestock | Capitalized first letter |
| 433 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 434 | Dominant Livelihood | farming, kaolin processing, livestock | Farming, kaolin processing, livestock | Capitalized first letter |
| 435 | Dominant Livelihood | farming, groundnut oil processing | Farming, groundnut oil processing | Capitalized first letter |
| 436 | Dominant Livelihood | commerce, government, education, agriculture | Commerce, government, education, agriculture | Capitalized first letter |
| 437 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 438 | Dominant Livelihood | subsistence farming, cattle rearing | Subsistence farming, cattle rearing | Capitalized first letter |
| 439 | Dominant Livelihood | cross-border trade, farming, livestock | Cross-border trade, farming, livestock | Capitalized first letter |
| 440 | Dominant Livelihood | farming, cotton ginning, grain processing | Farming, cotton ginning, grain processing | Capitalized first letter |
| 441 | Dominant Livelihood | farming, livestock, trade | Farming, livestock, trade | Capitalized first letter |
| 442 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 443 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 444 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 445 | Dominant Livelihood | subsistence farming | Subsistence farming | Capitalized first letter |
| 446 | Dominant Livelihood | subsistence farming, livestock, displaced | Subsistence farming, livestock, displaced | Capitalized first letter |
| 447 | Dominant Livelihood | subsistence farming, livestock, displaced | Subsistence farming, livestock, displaced | Capitalized first letter |
| 448 | Dominant Livelihood | subsistence farming, livestock | Subsistence farming, livestock | Capitalized first letter |
| 449 | Dominant Livelihood | subsistence farming, cross-border activity | Subsistence farming, cross-border activity | Capitalized first letter |
| 450 | Dominant Livelihood | subsistence farming millet, sorghum, groundnuts | Subsistence farming millet, sorghum, groundnuts | Capitalized first letter |
| 451 | Dominant Livelihood | subsistence farming grains, onions, pastoralism | Subsistence farming grains, onions, pastoralism | Capitalized first letter |
| 452 | Dominant Livelihood | fishing, rice farming, tourism, petty trade | Fishing, rice farming, tourism, petty trade | Capitalized first letter |
| 453 | Dominant Livelihood | subsistence farming millet, sorghum, pastoralism | Subsistence farming millet, sorghum, pastoralism | Capitalized first letter |
| 454 | Dominant Livelihood | rice farming, fishing, livestock rearing | Rice farming, fishing, livestock rearing | Capitalized first letter |
| 455 | Dominant Livelihood | government services, commerce, rice trade | Government services, commerce, rice trade | Capitalized first letter |
| 456 | Dominant Livelihood | subsistence farming sorghum, millet, livestock | Subsistence farming sorghum, millet, livestock | Capitalized first letter |
| 457 | Dominant Livelihood | subsistence farming millet, sorghum, pastoralism | Subsistence farming millet, sorghum, pastoralism | Capitalized first letter |
| 458 | Dominant Livelihood | subsistence farming, hunting, artisanal mining | Subsistence farming, hunting, artisanal mining | Capitalized first letter |
| 459 | Dominant Livelihood | subsistence farming, livestock, petty trade | Subsistence farming, livestock, petty trade | Capitalized first letter |
| 460 | Dominant Livelihood | farming millet, rice, sorghum, commerce | Farming millet, rice, sorghum, commerce | Capitalized first letter |
| 461 | Dominant Livelihood | subsistence farming millet, sorghum, groundnuts | Subsistence farming millet, sorghum, groundnuts | Capitalized first letter |
| 462 | Dominant Livelihood | farming millet, sorghum, rice, commerce | Farming millet, sorghum, rice, commerce | Capitalized first letter |
| 463 | Dominant Livelihood | subsistence farming millet, sorghum, pastoralism | Subsistence farming millet, sorghum, pastoralism | Capitalized first letter |
| 464 | Dominant Livelihood | fishing, rice farming, alluvial gold panning | Fishing, rice farming, alluvial gold panning | Capitalized first letter |
| 465 | Dominant Livelihood | subsistence farming, hunting, artisanal mining | Subsistence farming, hunting, artisanal mining | Capitalized first letter |
| 466 | Dominant Livelihood | farming sorghum, millet, fishing, gold panning | Farming sorghum, millet, fishing, gold panning | Capitalized first letter |
| 467 | Dominant Livelihood | subsistence farming millet, sorghum, rice, livestock | Subsistence farming millet, sorghum, rice, livestock | Capitalized first letter |
| 468 | Dominant Livelihood | subsistence farming, fishing, artisanal mining | Subsistence farming, fishing, artisanal mining | Capitalized first letter |
| 469 | Dominant Livelihood | farming, fishing, artisanal gold mining | Farming, fishing, artisanal gold mining | Capitalized first letter |
| 470 | Dominant Livelihood | farming, artisanal gold mining, commerce | Farming, artisanal gold mining, commerce | Capitalized first letter |
| 471 | Dominant Livelihood | subsistence farming yam, cassava, maize | Subsistence farming yam, cassava, maize | Capitalized first letter |
| 472 | Dominant Livelihood | farming, steel company employment, mining | Farming, steel company employment, mining | Capitalized first letter |
| 473 | Dominant Livelihood | farming yam, cassava; coal mining Okaba | Farming yam, cassava; coal mining Okaba | Capitalized first letter |
| 474 | Dominant Livelihood | subsistence farming, fishing along rivers | Subsistence farming, fishing along rivers | Capitalized first letter |
| 475 | Dominant Livelihood | subsistence farming yam, cassava, rice | Subsistence farming yam, cassava, rice | Capitalized first letter |
| 476 | Dominant Livelihood | rice farming, fishing, subsistence farming | Rice farming, fishing, subsistence farming | Capitalized first letter |
| 477 | Dominant Livelihood | trade, fishing on Niger River, farming | Trade, fishing on Niger River, farming | Capitalized first letter |
| 478 | Dominant Livelihood | subsistence farming cassava, yam, rice | Subsistence farming cassava, yam, rice | Capitalized first letter |
| 479 | Dominant Livelihood | farming yam, cassava, cocoa, cashew | Farming yam, cassava, cocoa, cashew | Capitalized first letter |
| 480 | Dominant Livelihood | farming yam, cassava, cocoa, cashew, rice | Farming yam, cassava, cocoa, cashew, rice | Capitalized first letter |
| 481 | Dominant Livelihood | farming, fishing, some mining activity | Farming, fishing, some mining activity | Capitalized first letter |
| 482 | Dominant Livelihood | civil service, trade, transportation hub | Civil service, trade, transportation hub | Capitalized first letter |
| 483 | Dominant Livelihood | farming cashew, gold mining, processing | Farming cashew, gold mining, processing | Capitalized first letter |
| 484 | Dominant Livelihood | farming yam, cassava, some mining | Farming yam, cassava, some mining | Capitalized first letter |
| 485 | Dominant Livelihood | subsistence farming, petty trade | Subsistence farming, petty trade | Capitalized first letter |
| 486 | Dominant Livelihood | farming, iron ore mining employment | Farming, iron ore mining employment | Capitalized first letter |
| 487 | Dominant Livelihood | trade, farming, artisanal mining, commerce | Trade, farming, artisanal mining, commerce | Capitalized first letter |
| 488 | Dominant Livelihood | subsistence farming yam, cassava, maize | Subsistence farming yam, cassava, maize | Capitalized first letter |
| 489 | Dominant Livelihood | farming, fishing along Benue, coal mining | Farming, fishing along Benue, coal mining | Capitalized first letter |
| 490 | Dominant Livelihood | farming cashew, cocoa, artisanal gold mining | Farming cashew, cocoa, artisanal gold mining | Capitalized first letter |
| 491 | Dominant Livelihood | farming cashew, artisanal gold mining | Farming cashew, artisanal gold mining | Capitalized first letter |
| 492 | Dominant Livelihood | farming yam, cassava, maize, petty trade | Farming yam, cassava, maize, petty trade | Capitalized first letter |
| 493 | Dominant Livelihood | farming yam, maize, cattle rearing, border trade | Farming yam, maize, cattle rearing, border trade | Capitalized first letter |
| 494 | Dominant Livelihood | farming rice, cassava, fishing on Niger River | Farming rice, cassava, fishing on Niger River | Capitalized first letter |
| 495 | Dominant Livelihood | farming cocoa, kola nut, cassava, yam | Farming cocoa, kola nut, cassava, yam | Capitalized first letter |
| 496 | Dominant Livelihood | farming yam, cassava, shea butter processing | Farming yam, cassava, shea butter processing | Capitalized first letter |
| 497 | Dominant Livelihood | civil service, trade, education, urban farming | Civil service, trade, education, urban farming | Capitalized first letter |
| 498 | Dominant Livelihood | civil service, education, trade, services | Civil service, education, trade, services | Capitalized first letter |
| 499 | Dominant Livelihood | civil service, commerce, artisan crafts, services | Civil service, commerce, artisan crafts, services | Capitalized first letter |
| 500 | Dominant Livelihood | farming yam, cassava, trade, shea butter | Farming yam, cassava, trade, shea butter | Capitalized first letter |
| 501 | Dominant Livelihood | farming yam, cassava, cocoa, kola nut | Farming yam, cassava, cocoa, kola nut | Capitalized first letter |
| 502 | Dominant Livelihood | farming yam, soya beans, guinea corn, cassava | Farming yam, soya beans, guinea corn, cassava | Capitalized first letter |
| 503 | Dominant Livelihood | farming yam, maize, rice, dam employment | Farming yam, maize, rice, dam employment | Capitalized first letter |
| 504 | Dominant Livelihood | trade, weaving, dyeing, farming, education | Trade, weaving, dyeing, farming, education | Capitalized first letter |
| 505 | Dominant Livelihood | farming cocoa, kola nut, yam, cassava | Farming cocoa, kola nut, yam, cassava | Capitalized first letter |
| 506 | Dominant Livelihood | farming yam, cassava, maize, petty trade | Farming yam, cassava, maize, petty trade | Capitalized first letter |
| 507 | Dominant Livelihood | farming cassava, rice, fishing, artisanal mining | Farming cassava, rice, fishing, artisanal mining | Capitalized first letter |
| 566 | Dominant Livelihood | civil service, trade, government, education | Civil service, trade, government, education | Capitalized first letter |
| 567 | Dominant Livelihood | civil service, commerce, banking, education | Civil service, commerce, banking, education | Capitalized first letter |
| 568 | Dominant Livelihood | manufacturing, industry, trade, services | Manufacturing, industry, trade, services | Capitalized first letter |
| 569 | Dominant Livelihood | cement production, quarrying, farming | Cement production, quarrying, farming | Capitalized first letter |
| 570 | Dominant Livelihood | trade, small manufacturing, services, farming | Trade, small manufacturing, services, farming | Capitalized first letter |
| 571 | Dominant Livelihood | farming, timber, cocoa, oil palm | Farming, timber, cocoa, oil palm | Capitalized first letter |
| 572 | Dominant Livelihood | trade, farming, cocoa, kolanut, education | Trade, farming, cocoa, kolanut, education | Capitalized first letter |
| 573 | Dominant Livelihood | subsistence farming, petty trade | Subsistence farming, petty trade | Capitalized first letter |
| 574 | Dominant Livelihood | commerce, trade, education, transport services | Commerce, trade, education, transport services | Capitalized first letter |
| 575 | Dominant Livelihood | education, farming, trade, cocoa | Education, farming, trade, cocoa | Capitalized first letter |
| 576 | Dominant Livelihood | subsistence farming, cattle rearing, cross-border trade | Subsistence farming, cattle rearing, cross-border trade | Capitalized first letter |
| 577 | Dominant Livelihood | farming, cross-border trade, fishing | Farming, cross-border trade, fishing | Capitalized first letter |
| 578 | Dominant Livelihood | agriculture, commuter services, Ofada rice, trade | Agriculture, commuter services, Ofada rice, trade | Capitalized first letter |
| 579 | Dominant Livelihood | farming, education, granite quarrying | Farming, education, granite quarrying | Capitalized first letter |
| 580 | Dominant Livelihood | farming, cassava, cocoa, petty trade | Farming, cassava, cocoa, petty trade | Capitalized first letter |
| 581 | Dominant Livelihood | fishing, subsistence farming, waterway trade | Fishing, subsistence farming, waterway trade | Capitalized first letter |
| 582 | Dominant Livelihood | farming, trade, artisanry | Farming, trade, artisanry | Capitalized first letter |
| 583 | Dominant Livelihood | commerce, industry, cement, kolanut trade | Commerce, industry, cement, kolanut trade | Capitalized first letter |
| 584 | Dominant Livelihood | farming, cross-border trade, cement industry | Farming, cross-border trade, cement industry | Capitalized first letter |
| 585 | Dominant Livelihood | farming, education, trade, livestock rearing | Farming, education, trade, livestock rearing | Capitalized first letter |
| 586 | Dominant Livelihood | trading, cocoa farming, kolanut, commerce | Trading, cocoa farming, kolanut, commerce | Capitalized first letter |
| 587 | Dominant Livelihood | farming, cocoa, teaching, food crops | Farming, cocoa, teaching, food crops | Capitalized first letter |
| 588 | Dominant Livelihood | farming, cocoa, education, petty trade | Farming, cocoa, education, petty trade | Capitalized first letter |
| 589 | Dominant Livelihood | agriculture, trading, cocoa, food crops | Agriculture, trading, cocoa, food crops | Capitalized first letter |
| 590 | Dominant Livelihood | farming, trade, suburban commuter services | Farming, trade, suburban commuter services | Capitalized first letter |
| 591 | Dominant Livelihood | civil service, trade, education, commerce | Civil service, trade, education, commerce | Capitalized first letter |
| 592 | Dominant Livelihood | fishing, subsistence farming, petty trading | Fishing, subsistence farming, petty trading | Capitalized first letter |
| 593 | Dominant Livelihood | cocoa farming, palm produce, food crops | Cocoa farming, palm produce, food crops | Capitalized first letter |
| 594 | Dominant Livelihood | cocoa farming, food crops, education | Cocoa farming, food crops, education | Capitalized first letter |
| 595 | Dominant Livelihood | fishing, oil production, palm oil, trading | Fishing, oil production, palm oil, trading | Capitalized first letter |
| 596 | Dominant Livelihood | cocoa farming, food crops, education | Cocoa farming, food crops, education | Capitalized first letter |
| 597 | Dominant Livelihood | farming, palm oil processing, cocoa, rubber | Farming, palm oil processing, cocoa, rubber | Capitalized first letter |
| 598 | Dominant Livelihood | commerce, transit services, farming, cocoa | Commerce, transit services, farming, cocoa | Capitalized first letter |
| 599 | Dominant Livelihood | farming, cassava, cocoa, education | Farming, cassava, cocoa, education | Capitalized first letter |
| 600 | Dominant Livelihood | farming, palm oil, timber, local crafts | Farming, palm oil, timber, local crafts | Capitalized first letter |
| 601 | Dominant Livelihood | trade, artisanship, cocoa, education | Trade, artisanship, cocoa, education | Capitalized first letter |
| 602 | Dominant Livelihood | cocoa farming, plantation farming, timber | Cocoa farming, plantation farming, timber | Capitalized first letter |
| 603 | Dominant Livelihood | trade, cocoa farming, education, civil service | Trade, cocoa farming, education, civil service | Capitalized first letter |
| 604 | Dominant Livelihood | cocoa farming, oil palm, trade | Cocoa farming, oil palm, trade | Capitalized first letter |
| 605 | Dominant Livelihood | farming, livestock rearing, local trade | Farming, livestock rearing, local trade | Capitalized first letter |
| 606 | Dominant Livelihood | gold mining, cocoa farming, agriculture | Gold mining, cocoa farming, agriculture | Capitalized first letter |
| 607 | Dominant Livelihood | cocoa farming, artisanal gold mining, oil palm | Cocoa farming, artisanal gold mining, oil palm | Capitalized first letter |
| 608 | Dominant Livelihood | subsistence farming, food crops, local trade | Subsistence farming, food crops, local trade | Capitalized first letter |
| 609 | Dominant Livelihood | agriculture, education, trade, cultural festivals | Agriculture, education, trade, cultural festivals | Capitalized first letter |
| 610 | Dominant Livelihood | trade, agriculture, cocoa processing, education | Trade, agriculture, cocoa processing, education | Capitalized first letter |
| 611 | Dominant Livelihood | farming, trade, services | Farming, trade, services | Capitalized first letter |
| 612 | Dominant Livelihood | agriculture, trade, civil service commuting | Agriculture, trade, civil service commuting | Capitalized first letter |
| 613 | Dominant Livelihood | farming, food crops, trade, education | Farming, food crops, trade, education | Capitalized first letter |
| 614 | Dominant Livelihood | education, civil service, trade, cultural tourism | Education, civil service, trade, cultural tourism | Capitalized first letter |
| 615 | Dominant Livelihood | education, agriculture, trade, cassava farming | Education, agriculture, trade, cassava farming | Capitalized first letter |
| 616 | Dominant Livelihood | farming, cassava production, local trade | Farming, cassava production, local trade | Capitalized first letter |
| 617 | Dominant Livelihood | cocoa farming, oil palm, food crops | Cocoa farming, oil palm, food crops | Capitalized first letter |
| 618 | Dominant Livelihood | subsistence farming, textile dyeing, hunting | Subsistence farming, textile dyeing, hunting | Capitalized first letter |
| 619 | Dominant Livelihood | agriculture, trade, local commerce | Agriculture, trade, local commerce | Capitalized first letter |
| 620 | Dominant Livelihood | farming, trade, local commerce | Farming, trade, local commerce | Capitalized first letter |
| 621 | Dominant Livelihood | trade, cocoa marketing, gold mining, education | Trade, cocoa marketing, gold mining, education | Capitalized first letter |
| 622 | Dominant Livelihood | trade, commerce, gold mining, agriculture | Trade, commerce, gold mining, agriculture | Capitalized first letter |
| 623 | Dominant Livelihood | agriculture, trade, commuter services | Agriculture, trade, commuter services | Capitalized first letter |
| 624 | Dominant Livelihood | agriculture, trade, food processing, palm oil | Agriculture, trade, food processing, palm oil | Capitalized first letter |
| 625 | Dominant Livelihood | farming, trade, food crops | Farming, trade, food crops | Capitalized first letter |
| 626 | Dominant Livelihood | education, agriculture, trade, commerce | Education, agriculture, trade, commerce | Capitalized first letter |
| 627 | Dominant Livelihood | agriculture, trade, cultural heritage | Agriculture, trade, cultural heritage | Capitalized first letter |
| 628 | Dominant Livelihood | agriculture, education, trade | Agriculture, education, trade | Capitalized first letter |
| 629 | Dominant Livelihood | farming, timber production, local trade | Farming, timber production, local trade | Capitalized first letter |
| 630 | Dominant Livelihood | civil service, trade, agriculture, services | Civil service, trade, agriculture, services | Capitalized first letter |
| 631 | Dominant Livelihood | agriculture, tourism, cocoa farming | Agriculture, tourism, cocoa farming | Capitalized first letter |
| 632 | Dominant Livelihood | farming, cassava production, trade | Farming, cassava production, trade | Capitalized first letter |
| 633 | Dominant Livelihood | civil service, commerce, industry, tourism | Civil service, commerce, industry, tourism | Capitalized first letter |
| 634 | Dominant Livelihood | yam and cassava farming, petty trade | Yam and cassava farming, petty trade | Capitalized first letter |
| 635 | Dominant Livelihood | maize and cassava farming, petty trade | Maize and cassava farming, petty trade | Capitalized first letter |
| 636 | Dominant Livelihood | civil service, trade, farming, tourism | Civil service, trade, farming, tourism | Capitalized first letter |
| 637 | Dominant Livelihood | cassava and yam farming, livestock | Cassava and yam farming, livestock | Capitalized first letter |
| 638 | Dominant Livelihood | farming, petty trade, suburban development | Farming, petty trade, suburban development | Capitalized first letter |
| 639 | Dominant Livelihood | education, civil service, commerce, healthcare | Education, civil service, commerce, healthcare | Capitalized first letter |
| 640 | Dominant Livelihood | commerce, transport, artisanal trades | Commerce, transport, artisanal trades | Capitalized first letter |
| 641 | Dominant Livelihood | government, banking, commerce, hospitality | Government, banking, commerce, hospitality | Capitalized first letter |
| 642 | Dominant Livelihood | petty trade, artisanal crafts, commerce | Petty trade, artisanal crafts, commerce | Capitalized first letter |
| 643 | Dominant Livelihood | commerce, banking, industry, transport | Commerce, banking, industry, transport | Capitalized first letter |
| 644 | Dominant Livelihood | yam, cassava, cocoa farming, trade | Yam, cassava, cocoa farming, trade | Capitalized first letter |
| 645 | Dominant Livelihood | farming, agro-processing, education | Farming, agro-processing, education | Capitalized first letter |
| 646 | Dominant Livelihood | cassava, yam farming, livestock rearing | Cassava, yam farming, livestock rearing | Capitalized first letter |
| 647 | Dominant Livelihood | farming, logging, charcoal production | Farming, logging, charcoal production | Capitalized first letter |
| 648 | Dominant Livelihood | farming, cattle rearing, border trade | Farming, cattle rearing, border trade | Capitalized first letter |
| 649 | Dominant Livelihood | aso-oke weaving, farming, tobacco, trade | Aso-oke weaving, farming, tobacco, trade | Capitalized first letter |
| 650 | Dominant Livelihood | subsistence farming, hunting, livestock | Subsistence farming, hunting, livestock | Capitalized first letter |
| 651 | Dominant Livelihood | cocoa, yam farming, cloth weaving | Cocoa, yam farming, cloth weaving | Capitalized first letter |
| 652 | Dominant Livelihood | cotton, tobacco farming, weaving, trade | Cotton, tobacco farming, weaving, trade | Capitalized first letter |
| 653 | Dominant Livelihood | farming, petty trade, suburban housing | Farming, petty trade, suburban housing | Capitalized first letter |
| 654 | Dominant Livelihood | commerce, education, civil service, trade | Commerce, education, civil service, trade | Capitalized first letter |
| 655 | Dominant Livelihood | farming, petty trade, artisanal crafts | Farming, petty trade, artisanal crafts | Capitalized first letter |
| 656 | Dominant Livelihood | yam, cassava farming, livestock rearing | Yam, cassava farming, livestock rearing | Capitalized first letter |
| 657 | Dominant Livelihood | farming, quarrying, petty trade | Farming, quarrying, petty trade | Capitalized first letter |
| 658 | Dominant Livelihood | farming, commerce, light manufacturing | Farming, commerce, light manufacturing | Capitalized first letter |
| 659 | Dominant Livelihood | cassava, vegetable farming, petty trade | Cassava, vegetable farming, petty trade | Capitalized first letter |
| 660 | Dominant Livelihood | yam, cassava farming, livestock, trade | Yam, cassava farming, livestock, trade | Capitalized first letter |
| 661 | Dominant Livelihood | yam, cassava farming, cattle rearing | Yam, cassava farming, cattle rearing | Capitalized first letter |
| 662 | Dominant Livelihood | farming, fishing, petty trade | Farming, fishing, petty trade | Capitalized first letter |
| 663 | Dominant Livelihood | commerce, civil service, farming, education | Commerce, civil service, farming, education | Capitalized first letter |
| 664 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 665 | Dominant Livelihood | commerce, farming, cattle, border trade | Commerce, farming, cattle, border trade | Capitalized first letter |
| 666 | Dominant Livelihood | yam, cassava farming, livestock rearing | Yam, cassava farming, livestock rearing | Capitalized first letter |
| 667 | Dominant Livelihood | agriculture and artisanal tin mining | Agriculture and artisanal tin mining | Capitalized first letter |
| 668 | Dominant Livelihood | agriculture, artisanal mining, livestock | Agriculture, artisanal mining, livestock | Capitalized first letter |
| 670 | Dominant Livelihood | agriculture, livestock rearing, trading | Agriculture, livestock rearing, trading | Capitalized first letter |
| 671 | Dominant Livelihood | commerce, civil service, education, trade | Commerce, civil service, education, trade | Capitalized first letter |
| 672 | Dominant Livelihood | industry, tin mining, agriculture | Industry, tin mining, agriculture | Capitalized first letter |
| 673 | Dominant Livelihood | farming, pastoralism, river fishing | Farming, pastoralism, river fishing | Capitalized first letter |
| 674 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 675 | Dominant Livelihood | agriculture, civil service, small trading | Agriculture, civil service, small trading | Capitalized first letter |
| 676 | Dominant Livelihood | subsistence farming, small livestock | Subsistence farming, small livestock | Capitalized first letter |
| 677 | Dominant Livelihood | agriculture, artisanal tin mining, trade | Agriculture, artisanal tin mining, trade | Capitalized first letter |
| 678 | Dominant Livelihood | subsistence farming, small-scale fishing | Subsistence farming, small-scale fishing | Capitalized first letter |
| 679 | Dominant Livelihood | agriculture, livestock rearing, trade | Agriculture, livestock rearing, trade | Capitalized first letter |
| 680 | Dominant Livelihood | rice farming, subsistence agriculture | Rice farming, subsistence agriculture | Capitalized first letter |
| 681 | Dominant Livelihood | agriculture, artisanal mining, livestock | Agriculture, artisanal mining, livestock | Capitalized first letter |
| 682 | Dominant Livelihood | agriculture, trading, fishing | Agriculture, trading, fishing | Capitalized first letter |
| 683 | Dominant Livelihood | farming, pastoralism, fishing, trade | Farming, pastoralism, fishing, trade | Capitalized first letter |
| 684 | Dominant Livelihood | farming, fishing, forest product trade | Farming, fishing, forest product trade | Capitalized first letter |
| 685 | Dominant Livelihood | farming, fishing, timber, petty trade | Farming, fishing, timber, petty trade | Capitalized first letter |
| 686 | Dominant Livelihood | rural farming, canoe building, trade | Rural farming, canoe building, trade | Capitalized first letter |
| 687 | Dominant Livelihood | fishing, oil servicing, boat building | Fishing, oil servicing, boat building | Capitalized first letter |
| 688 | Dominant Livelihood | deep-sea fishing, marine produce | Deep-sea fishing, marine produce | Capitalized first letter |
| 689 | Dominant Livelihood | fishing, palm oil trade, commerce | Fishing, palm oil trade, commerce | Capitalized first letter |
| 690 | Dominant Livelihood | oil-gas employment, fishing, maritime | Oil-gas employment, fishing, maritime | Capitalized first letter |
| 691 | Dominant Livelihood | fishing, river farming, local trade | Fishing, river farming, local trade | Capitalized first letter |
| 692 | Dominant Livelihood | petrochemicals, refining, port logistics | Petrochemicals, refining, port logistics | Capitalized first letter |
| 693 | Dominant Livelihood | palm oil production, farming, trade | Palm oil production, farming, trade | Capitalized first letter |
| 694 | Dominant Livelihood | cassava and palm oil farming, trade | Cassava and palm oil farming, trade | Capitalized first letter |
| 695 | Dominant Livelihood | farming, fishing, environmental activism | Farming, fishing, environmental activism | Capitalized first letter |
| 696 | Dominant Livelihood | farming, aviation services, petty trade | Farming, aviation services, petty trade | Capitalized first letter |
| 697 | Dominant Livelihood | agriculture, education, small trade | Agriculture, education, small trade | Capitalized first letter |
| 698 | Dominant Livelihood | commerce, real estate, private services | Commerce, real estate, private services | Capitalized first letter |
| 699 | Dominant Livelihood | oil-related activity, farming, fishing | Oil-related activity, farming, fishing | Capitalized first letter |
| 700 | Dominant Livelihood | fishing, petty trading, small farming | Fishing, petty trading, small farming | Capitalized first letter |
| 701 | Dominant Livelihood | fishing, petroleum product trade | Fishing, petroleum product trade | Capitalized first letter |
| 702 | Dominant Livelihood | cassava and vegetable farming, trade | Cassava and vegetable farming, trade | Capitalized first letter |
| 703 | Dominant Livelihood | fishing, cultural tourism, riverine trade | Fishing, cultural tourism, riverine trade | Capitalized first letter |
| 704 | Dominant Livelihood | power generation, warehousing, industry | Power generation, warehousing, industry | Capitalized first letter |
| 705 | Dominant Livelihood | oil services, shipping, banking, government | Oil services, shipping, banking, government | Capitalized first letter |
| 706 | Dominant Livelihood | farming, youth programs, activism | Farming, youth programs, activism | Capitalized first letter |
| 707 | Dominant Livelihood | subsistence farming, millet, sorghum, livestock | Subsistence farming, millet, sorghum, livestock | Capitalized first letter |
| 708 | Dominant Livelihood | farming, livestock, trade, kaolin mining | Farming, livestock, trade, kaolin mining | Capitalized first letter |
| 709 | Dominant Livelihood | farming, cement production, mining, trade | Farming, cement production, mining, trade | Capitalized first letter |
| 710 | Dominant Livelihood | subsistence farming, livestock, coal mining | Subsistence farming, livestock, coal mining | Capitalized first letter |
| 711 | Dominant Livelihood | irrigated farming, fishing, livestock rearing | Irrigated farming, fishing, livestock rearing | Capitalized first letter |
| 712 | Dominant Livelihood | subsistence farming, nomadic pastoralism | Subsistence farming, nomadic pastoralism | Capitalized first letter |
| 713 | Dominant Livelihood | farming, onion production, livestock, trade | Farming, onion production, livestock, trade | Capitalized first letter |
| 714 | Dominant Livelihood | cross-border trade, farming, livestock | Cross-border trade, farming, livestock | Capitalized first letter |
| 715 | Dominant Livelihood | subsistence farming, livestock, pastoralism | Subsistence farming, livestock, pastoralism | Capitalized first letter |
| 716 | Dominant Livelihood | farming, fishing, artisanal gold mining | Farming, fishing, artisanal gold mining | Capitalized first letter |
| 717 | Dominant Livelihood | farming, limestone mining, peri-urban trade | Farming, limestone mining, peri-urban trade | Capitalized first letter |
| 718 | Dominant Livelihood | subsistence farming, nomadic pastoralism | Subsistence farming, nomadic pastoralism | Capitalized first letter |
| 719 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 720 | Dominant Livelihood | subsistence farming, livestock, petty trade | Subsistence farming, livestock, petty trade | Capitalized first letter |
| 721 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 722 | Dominant Livelihood | government, commerce, services, trade | Government, commerce, services, trade | Capitalized first letter |
| 723 | Dominant Livelihood | commerce, education, crafts, services | Commerce, education, crafts, services | Capitalized first letter |
| 724 | Dominant Livelihood | farming, fishing, livestock, river trade | Farming, fishing, livestock, river trade | Capitalized first letter |
| 725 | Dominant Livelihood | subsistence farming, pastoralism, livestock | Subsistence farming, pastoralism, livestock | Capitalized first letter |
| 726 | Dominant Livelihood | subsistence farming, livestock, gold panning | Subsistence farming, livestock, gold panning | Capitalized first letter |
| 727 | Dominant Livelihood | education, commerce, farming, cement industry | Education, commerce, farming, cement industry | Capitalized first letter |
| 728 | Dominant Livelihood | farming, gypsum mining, livestock rearing | Farming, gypsum mining, livestock rearing | Capitalized first letter |
| 729 | Dominant Livelihood | farming, gold panning, livestock, trade | Farming, gold panning, livestock, trade | Capitalized first letter |
| 730 | Dominant Livelihood | subsistence farming, yam, maize, cassava | Subsistence farming, yam, maize, cassava | Capitalized first letter |
| 731 | Dominant Livelihood | farming, trade, cattle rearing | Farming, trade, cattle rearing | Capitalized first letter |
| 732 | Dominant Livelihood | farming, fishing, small-scale trade | Farming, fishing, small-scale trade | Capitalized first letter |
| 733 | Dominant Livelihood | subsistence farming, pastoralism, forestry | Subsistence farming, pastoralism, forestry | Capitalized first letter |
| 734 | Dominant Livelihood | farming, yam, cattle rearing, fishing | Farming, yam, cattle rearing, fishing | Capitalized first letter |
| 735 | Dominant Livelihood | fishing, farming, small-scale trade | Fishing, farming, small-scale trade | Capitalized first letter |
| 736 | Dominant Livelihood | government, commerce, services, farming | Government, commerce, services, farming | Capitalized first letter |
| 737 | Dominant Livelihood | farming, fishing, pastoralism | Farming, fishing, pastoralism | Capitalized first letter |
| 738 | Dominant Livelihood | farming, forestry, timber extraction | Farming, forestry, timber extraction | Capitalized first letter |
| 739 | Dominant Livelihood | farming, fishing, pastoralism | Farming, fishing, pastoralism | Capitalized first letter |
| 740 | Dominant Livelihood | tea farming, pastoralism, subsistence crops | Tea farming, pastoralism, subsistence crops | Capitalized first letter |
| 741 | Dominant Livelihood | farming, trade, timber, small commerce | Farming, trade, timber, small commerce | Capitalized first letter |
| 742 | Dominant Livelihood | subsistence farming, forestry, hunting | Subsistence farming, forestry, hunting | Capitalized first letter |
| 743 | Dominant Livelihood | farming, trade, fishing, education services | Farming, trade, fishing, education services | Capitalized first letter |
| 744 | Dominant Livelihood | subsistence farming, maize, sorghum, millet | Subsistence farming, maize, sorghum, millet | Capitalized first letter |
| 745 | Dominant Livelihood | farming, cattle rearing, small-scale trade | Farming, cattle rearing, small-scale trade | Capitalized first letter |
| 746 | Dominant Livelihood | farming, fishing, livestock, petty trade | Farming, fishing, livestock, petty trade | Capitalized first letter |
| 747 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 748 | Dominant Livelihood | government, commerce, services, trade | Government, commerce, services, trade | Capitalized first letter |
| 749 | Dominant Livelihood | subsistence farming, groundnuts, livestock | Subsistence farming, groundnuts, livestock | Capitalized first letter |
| 750 | Dominant Livelihood | farming, millet, sorghum, groundnuts | Farming, millet, sorghum, groundnuts | Capitalized first letter |
| 751 | Dominant Livelihood | farming, livestock, cross-border trade | Farming, livestock, cross-border trade | Capitalized first letter |
| 752 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 753 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 754 | Dominant Livelihood | farming, millet, sorghum, livestock trade | Farming, millet, sorghum, livestock trade | Capitalized first letter |
| 755 | Dominant Livelihood | farming, fishing, livestock rearing | Farming, fishing, livestock rearing | Capitalized first letter |
| 756 | Dominant Livelihood | farming, livestock, cross-border trade | Farming, livestock, cross-border trade | Capitalized first letter |
| 757 | Dominant Livelihood | farming, groundnuts, millet, livestock | Farming, groundnuts, millet, livestock | Capitalized first letter |
| 758 | Dominant Livelihood | commerce, trade, gum arabic, farming | Commerce, trade, gum arabic, farming | Capitalized first letter |
| 759 | Dominant Livelihood | livestock trade, commerce, farming | Livestock trade, commerce, farming | Capitalized first letter |
| 760 | Dominant Livelihood | subsistence farming, millet, sorghum | Subsistence farming, millet, sorghum | Capitalized first letter |
| 761 | Dominant Livelihood | farming, livestock, fishing, Lake Chad basin | Farming, livestock, fishing, Lake Chad basin | Capitalized first letter |
| 762 | Dominant Livelihood | farming, fishing, livestock rearing | Farming, fishing, livestock rearing | Capitalized first letter |
| 763 | Dominant Livelihood | artisanal gold mining, subsistence farming | Artisanal gold mining, subsistence farming | Capitalized first letter |
| 764 | Dominant Livelihood | subsistence farming, livestock, petty trade | Subsistence farming, livestock, petty trade | Capitalized first letter |
| 765 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 766 | Dominant Livelihood | artisanal gold mining, subsistence farming | Artisanal gold mining, subsistence farming | Capitalized first letter |
| 767 | Dominant Livelihood | subsistence farming, livestock rearing | Subsistence farming, livestock rearing | Capitalized first letter |
| 768 | Dominant Livelihood | subsistence farming, livestock, petty trade | Subsistence farming, livestock, petty trade | Capitalized first letter |
| 769 | Dominant Livelihood | government, commerce, farming, trade | Government, commerce, farming, trade | Capitalized first letter |
| 770 | Dominant Livelihood | commerce, farming, cotton, groundnuts trade | Commerce, farming, cotton, groundnuts trade | Capitalized first letter |
| 771 | Dominant Livelihood | subsistence farming, livestock, herding | Subsistence farming, livestock, herding | Capitalized first letter |
| 772 | Dominant Livelihood | farming, livestock, artisanal gold mining | Farming, livestock, artisanal gold mining | Capitalized first letter |
| 773 | Dominant Livelihood | farming, livestock, cross-border trade | Farming, livestock, cross-border trade | Capitalized first letter |
| 774 | Dominant Livelihood | farming, commerce, tobacco, groundnuts | Farming, commerce, tobacco, groundnuts | Capitalized first letter |
| 775 | Dominant Livelihood | subsistence farming, millet, sorghum, trade | Subsistence farming, millet, sorghum, trade | Capitalized first letter |
| 776 | Dominant Livelihood | farming, livestock, cross-border trade | Farming, livestock, cross-border trade | Capitalized first letter |
| 245 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 246 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 247 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 248 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 249 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 250 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 251 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 252 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 253 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 254 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 255 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 256 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 257 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 258 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 259 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 260 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 261 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 262 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 263 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 264 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 265 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 266 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 267 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 268 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 269 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 270 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 271 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 272 | Predominant Land Tenure | mixed: customary / some state leasehold | Mixed: customary / some state leasehold | Capitalized first letter |
| 273 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 274 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 275 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 276 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 277 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 634 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 635 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 636 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 637 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 638 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 639 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 640 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 641 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 642 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 643 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 644 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 645 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 646 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 647 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 648 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 649 | Predominant Land Tenure | mixed: customary rural / state leasehold semi-urban | Mixed: customary rural / state leasehold semi-urban | Capitalized first letter |
| 650 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 651 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 652 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 653 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 654 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 655 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 656 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 657 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 658 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 659 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 660 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 661 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 662 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 663 | Predominant Land Tenure | mixed: customary rural / state leasehold urban | Mixed: customary rural / state leasehold urban | Capitalized first letter |
| 664 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 665 | Predominant Land Tenure | mixed: customary rural / state leasehold semi-urban | Mixed: customary rural / state leasehold semi-urban | Capitalized first letter |
| 666 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 667 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 668 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 669 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 670 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 671 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 672 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 673 | Predominant Land Tenure | customary tenure with emirate/caliphate elements | Customary tenure with emirate/caliphate elements | Capitalized first letter |
| 674 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 675 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 676 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 677 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 678 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 679 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 680 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 681 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 682 | Predominant Land Tenure | community/customary tenure under Land Use Act | Community/customary tenure under Land Use Act | Capitalized first letter |
| 683 | Predominant Land Tenure | customary tenure with emirate/caliphate elements | Customary tenure with emirate/caliphate elements | Capitalized first letter |
| 684 | Predominant Land Tenure | community/customary tenure; oil-producing area | Community/customary tenure; oil-producing area | Capitalized first letter |
| 685 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 686 | Predominant Land Tenure | community/customary tenure; oil-producing area | Community/customary tenure; oil-producing area | Capitalized first letter |
| 687 | Predominant Land Tenure | community/customary riverine tenure | Community/customary riverine tenure | Capitalized first letter |
| 688 | Predominant Land Tenure | community/customary tenure; fishing-based | Community/customary tenure; fishing-based | Capitalized first letter |
| 689 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 690 | Predominant Land Tenure | customary/community; NLNG industrial leasehold | Customary/community; NLNG industrial leasehold | Capitalized first letter |
| 691 | Predominant Land Tenure | community/customary riverine tenure | Community/customary riverine tenure | Capitalized first letter |
| 692 | Predominant Land Tenure | customary tenure; oil-refinery impact zone | Customary tenure; oil-refinery impact zone | Capitalized first letter |
| 693 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 694 | Predominant Land Tenure | community/customary tenure; oil-producing area | Community/customary tenure; oil-producing area | Capitalized first letter |
| 695 | Predominant Land Tenure | community/customary tenure; oil-affected area | Community/customary tenure; oil-affected area | Capitalized first letter |
| 696 | Predominant Land Tenure | customary tenure; airport impact zone | Customary tenure; airport impact zone | Capitalized first letter |
| 697 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 698 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 699 | Predominant Land Tenure | customary tenure; major oil-producing area | Customary tenure; major oil-producing area | Capitalized first letter |
| 700 | Predominant Land Tenure | community/customary fishing-based tenure | Community/customary fishing-based tenure | Capitalized first letter |
| 701 | Predominant Land Tenure | community/customary; oil-affected riverine | Community/customary; oil-affected riverine | Capitalized first letter |
| 702 | Predominant Land Tenure | community/customary tenure | Community/customary tenure | Capitalized first letter |
| 703 | Predominant Land Tenure | community/customary riverine tenure | Community/customary riverine tenure | Capitalized first letter |
| 704 | Predominant Land Tenure | mixed: customary / state industrial leasehold | Mixed: customary / state industrial leasehold | Capitalized first letter |
| 705 | Predominant Land Tenure | mixed: customary / state leasehold urban | Mixed: customary / state leasehold urban | Capitalized first letter |
| 706 | Predominant Land Tenure | community/customary tenure; oil-affected area | Community/customary tenure; oil-affected area | Capitalized first letter |
