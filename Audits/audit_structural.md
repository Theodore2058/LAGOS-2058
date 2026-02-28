# Structural Integrity Audit Report
**File:** `nigeria_lga_polsim_formatted.xlsx` — Sheet: `LGA_DATA`
**Date:** 2026-02-28
**Rows (data):** 774  |  **Columns:** 127

---
## 1. Row Count Check

Expected: **774** data rows
Found: **774** data rows

**PASS** — Row count matches expected 774 LGAs.

No duplicate (State, LGA Name) pairs found.

### State-Level LGA Count Comparison

| State (Official) | Official LGAs | Dataset LGAs | Diff |
|-----------------|---------------|--------------|------|
| Abia | 17 | 17 | +0 |
| Adamawa | 21 | 21 | +0 |
| Akwa Ibom | 31 | 31 | +0 |
| Anambra | 21 | 21 | +0 |
| Bauchi | 20 | 20 | +0 |
| Bayelsa | 8 | 8 | +0 |
| Benue | 23 | 23 | +0 |
| Borno | 27 | 27 | +0 |
| Cross River | 18 | 18 | +0 |
| Delta | 25 | 25 | +0 |
| Ebonyi | 13 | 13 | +0 |
| Edo | 18 | 18 | +0 |
| Ekiti | 16 | 16 | +0 |
| Enugu | 17 | 17 | +0 |
| FCT | 6 | 6 | +0 |
| Gombe | 11 | 11 | +0 |
| Imo | 27 | 27 | +0 |
| Jigawa | 27 | 27 | +0 |
| Kaduna | 23 | 23 | +0 |
| Kano | 44 | 44 | +0 |
| Katsina | 34 | 34 | +0 |
| Kebbi | 21 | 21 | +0 |
| Kogi | 21 | 21 | +0 |
| Kwara | 16 | 16 | +0 |
| Lagos | 20 | 20 | +0 |
| Nasarawa | 13 | 13 | +0 |
| Niger | 25 | 25 | +0 |
| Ogun | 20 | 20 | +0 |
| Ondo | 18 | 18 | +0 |
| Osun | 30 | 30 | +0 |
| Oyo | 33 | 33 | +0 |
| Plateau | 17 | 17 | +0 |
| Rivers | 23 | 23 | +0 |
| Sokoto | 23 | 23 | +0 |
| Taraba | 16 | 16 | +0 |
| Yobe | 17 | 17 | +0 |
| Zamfara | 14 | 14 | +0 |

---
## 2. Identification Columns

**State** (`State`): All 774 rows populated. ✓
**LGA Name** (`LGA Name`): All 774 rows populated. ✓
**Administrative Zone (Colonial Era Region)** (`Colonial Era Region`): All 774 rows populated. ✓

### Duplicate LGA Names Within Same State
No duplicates found. ✓

### Administrative Zones (Colonial Era Region)

Unique zones: **4** (expected: ~8)

| Zone | LGA Count |
|------|-----------|
| Eastern | 175 |
| Mid-Western | 43 |
| Northern | 419 |
| Western | 137 |

### States

Unique states: **37**

| State | LGA Count |
|-------|-----------|
| Abia | 17 |
| Adamawa | 21 |
| Akwa Ibom | 31 |
| Anambra | 21 |
| Bauchi | 20 |
| Bayelsa | 8 |
| Benue | 23 |
| Borno | 27 |
| Cross River | 18 |
| Delta | 25 |
| Ebonyi | 13 |
| Edo | 18 |
| Ekiti | 16 |
| Enugu | 17 |
| FCT | 6 |
| Gombe | 11 |
| Imo | 27 |
| Jigawa | 27 |
| Kaduna | 23 |
| Kano | 44 |
| Katsina | 34 |
| Kebbi | 21 |
| Kogi | 21 |
| Kwara | 16 |
| Lagos | 20 |
| Nasarawa | 13 |
| Niger | 25 |
| Ogun | 20 |
| Ondo | 18 |
| Osun | 30 |
| Oyo | 33 |
| Plateau | 17 |
| Rivers | 23 |
| Sokoto | 23 |
| Taraba | 16 |
| Yobe | 17 |
| Zamfara | 14 |

---
## 3. Ethnicity Sum Check

Ethnicity columns identified: **86** (col indices 8–93)
Range: `% Hausa` ... `% Other`

| Metric | Value |
|--------|-------|
| Min sum | 9.00 |
| Max sum | 112.00 |
| Mean sum | 91.81 |
| Median sum | 100.00 |
| Rows outside 99–101 | 318 |
| Rows deviating >1.0 from 100 | 318 |

### Rows with Ethnicity Sum Deviation > 1.0

| Row (Excel) | State | LGA | Sum |
|-------------|-------|-----|-----|
| 20 | Adamawa | Demsa | 80.00 |
| 22 | Adamawa | Ganye | 98.00 |
| 24 | Adamawa | Gombi | 85.00 |
| 26 | Adamawa | Hong | 94.00 |
| 28 | Adamawa | Lamurde | 85.00 |
| 29 | Adamawa | Madagali | 75.00 |
| 31 | Adamawa | Mayo-Belwa | 92.00 |
| 35 | Adamawa | Numan | 95.00 |
| 36 | Adamawa | Shelleng | 65.00 |
| 38 | Adamawa | Toungo | 95.00 |
| 42 | Akwa Ibom | Eastern Obolo | 95.00 |
| 48 | Akwa Ibom | Ibeno | 18.00 |
| 51 | Akwa Ibom | Ika | 79.50 |
| 52 | Akwa Ibom | Ikono | 101.90 |
| 53 | Akwa Ibom | Ikot Abasi | 106.90 |
| 55 | Akwa Ibom | Ini | 102.00 |
| 56 | Akwa Ibom | Itu | 98.50 |
| 64 | Akwa Ibom | Onna | 107.90 |
| 69 | Akwa Ibom | Uruan | 106.00 |
| 71 | Akwa Ibom | Uyo | 111.40 |
| 93 | Bauchi | Alkaleri | 60.00 |
| 94 | Bauchi | Bauchi | 79.00 |
| 95 | Bauchi | Bogoro | 27.00 |
| 96 | Bauchi | Damban | 90.00 |
| 97 | Bauchi | Darazo | 71.00 |
| 98 | Bauchi | Dass | 30.00 |
| 99 | Bauchi | Gamawa | 70.00 |
| 100 | Bauchi | Ganjuwa | 60.00 |
| 101 | Bauchi | Giade | 75.00 |
| 102 | Bauchi | Itas/Gadau | 107.00 |
| 103 | Bauchi | Jama'are | 80.00 |
| 104 | Bauchi | Katagum | 71.00 |
| 105 | Bauchi | Kirfi | 60.00 |
| 106 | Bauchi | Misau | 85.00 |
| 107 | Bauchi | Ningi | 50.00 |
| 108 | Bauchi | Shira | 82.00 |
| 109 | Bauchi | Tafawa Balewa | 44.00 |
| 110 | Bauchi | Toro | 57.00 |
| 111 | Bauchi | Warji | 32.00 |
| 112 | Bauchi | Zaki | 77.00 |
| 121 | Benue | Ado | 84.50 |
| 122 | Benue | Agatu | 27.00 |
| 123 | Benue | Apa | 98.00 |
| 124 | Benue | Buruku | 101.10 |
| 125 | Benue | Gboko | 98.50 |
| 126 | Benue | Guma | 98.50 |
| 127 | Benue | Gwer East | 102.00 |
| 129 | Benue | Katsina-Ala | 96.00 |
| 130 | Benue | Konshisha | 101.90 |
| 133 | Benue | Makurdi | 104.00 |
| 134 | Benue | Obi | 20.50 |
| 137 | Benue | Oju | 20.50 |
| 138 | Benue | Okpokwu | 105.00 |
| 139 | Benue | Otukpo | 103.90 |
| 140 | Benue | Tarka | 98.50 |
| 144 | Borno | Abadam | 95.00 |
| 145 | Borno | Askira/Uba | 72.00 |
| 146 | Borno | Bama | 102.00 |
| 147 | Borno | Bayo | 83.00 |
| 148 | Borno | Biu | 75.00 |
| 149 | Borno | Chibok | 17.00 |
| 150 | Borno | Damboa | 70.00 |
| 151 | Borno | Dikwa | 104.00 |
| 153 | Borno | Guzamala | 95.00 |
| 154 | Borno | Gwoza | 27.00 |
| 155 | Borno | Hawul | 88.00 |
| 156 | Borno | Jere | 105.00 |
| 157 | Borno | Kaga | 103.00 |
| 158 | Borno | Kala/Balge | 85.00 |
| 159 | Borno | Konduga | 102.00 |
| 160 | Borno | Kukawa | 87.00 |
| 161 | Borno | Kwaya Kusar | 97.00 |
| 162 | Borno | Mafa | 104.10 |
| 164 | Borno | Maiduguri | 104.00 |
| 165 | Borno | Marte | 102.00 |
| 166 | Borno | Mobbar | 102.00 |
| 167 | Borno | Monguno | 102.00 |
| 168 | Borno | Ngala | 104.00 |
| 170 | Borno | Shani | 51.00 |
| 171 | Cross River | Abi | 14.00 |
| 172 | Cross River | Akamkpa | 78.00 |
| 173 | Cross River | Akpabuyo | 105.00 |
| 174 | Cross River | Bakassi | 75.00 |
| 175 | Cross River | Bekwarra | 10.00 |
| 176 | Cross River | Biase | 33.00 |
| 177 | Cross River | Boki | 12.00 |
| 178 | Cross River | Calabar Municipal | 92.50 |
| 179 | Cross River | Calabar South | 75.50 |
| 180 | Cross River | Etung | 104.00 |
| 181 | Cross River | Ikom | 48.00 |
| 182 | Cross River | Obanliku | 11.50 |
| 183 | Cross River | Obubra | 15.00 |
| 184 | Cross River | Obudu | 11.50 |
| 185 | Cross River | Odukpani | 80.50 |
| 186 | Cross River | Ogoja | 40.00 |
| 187 | Cross River | Yakurr | 9.00 |
| 188 | Cross River | Yala | 15.50 |
| 189 | Delta | Aniocha North | 101.90 |
| 192 | Delta | Burutu | 106.00 |
| 194 | Delta | Ethiope West | 106.00 |
| 196 | Delta | Ika South | 106.00 |
| 199 | Delta | Ndokwa East | 107.10 |
| 203 | Delta | Oshimili South | 110.80 |
| 205 | Delta | Sapele | 107.90 |
| 210 | Delta | Uvwie | 107.10 |
| 212 | Delta | Warri South | 112.00 |
| 221 | Ebonyi | Ishielu | 97.00 |
| 225 | Ebonyi | Ohaukwu | 96.50 |
| 235 | Edo | Etsako West | 106.20 |
| 238 | Edo | Oredo | 106.00 |
| 279 | FCT | Abuja Municipal | 88.60 |
| 284 | Gombe | Akko | 95.00 |
| 285 | Gombe | Balanga | 75.00 |
| 290 | Gombe | Kaltungo | 62.00 |
| 293 | Gombe | Shongom | 75.00 |
| 324 | Jigawa | Biriniwa | 108.00 |
| 325 | Jigawa | Birnin Kudu | 104.00 |
| 334 | Jigawa | Hadejia | 108.90 |
| 339 | Jigawa | Kiri Kasama | 108.00 |
| 342 | Jigawa | Malam Madori | 107.10 |
| 349 | Kaduna | Birnin Gwari | 86.00 |
| 350 | Kaduna | Chikun | 78.00 |
| 352 | Kaduna | Igabi | 107.10 |
| 354 | Kaduna | Jaba | 103.90 |
| 355 | Kaduna | Jema'a | 51.00 |
| 356 | Kaduna | Kachia | 62.50 |
| 357 | Kaduna | Kaduna North | 108.00 |
| 358 | Kaduna | Kaduna South | 83.00 |
| 359 | Kaduna | Kagarko | 49.00 |
| 360 | Kaduna | Kajuru | 42.00 |
| 361 | Kaduna | Kaura | 12.00 |
| 362 | Kaduna | Kauru | 54.00 |
| 363 | Kaduna | Kubau | 106.10 |
| 365 | Kaduna | Lere | 91.00 |
| 368 | Kaduna | Sanga | 18.00 |
| 369 | Kaduna | Soba | 106.00 |
| 370 | Kaduna | Zangon Kataf | 83.00 |
| 371 | Kaduna | Zaria | 98.00 |
| 377 | Kano | Bunkure | 98.00 |
| 378 | Kano | Dala | 105.90 |
| 380 | Kano | Dawakin Kudu | 98.30 |
| 381 | Kano | Dawakin Tofa | 98.00 |
| 382 | Kano | Doguwa | 104.00 |
| 383 | Kano | Fagge | 109.70 |
| 385 | Kano | Garko | 98.00 |
| 386 | Kano | Garun Mallam | 98.00 |
| 389 | Kano | Gwale | 105.80 |
| 392 | Kano | Kano Municipal | 106.80 |
| 412 | Kano | Tudun Wada | 97.80 |
| 433 | Katsina | Kaita | 98.00 |
| 439 | Katsina | Mai'Adua | 98.00 |
| 450 | Kebbi | Aleiro | 98.00 |
| 451 | Kebbi | Arewa Dandi | 68.00 |
| 452 | Kebbi | Argungu | 102.00 |
| 453 | Kebbi | Augie | 102.00 |
| 454 | Kebbi | Bagudo | 71.00 |
| 455 | Kebbi | Birnin Kebbi | 83.00 |
| 456 | Kebbi | Bunza | 103.00 |
| 457 | Kebbi | Dandi | 57.00 |
| 458 | Kebbi | Fakai | 24.00 |
| 459 | Kebbi | Gwandu | 98.00 |
| 462 | Kebbi | Koko/Besse | 89.00 |
| 463 | Kebbi | Maiyama | 104.00 |
| 464 | Kebbi | Ngaski | 60.00 |
| 465 | Kebbi | Sakaba | 30.00 |
| 466 | Kebbi | Shanga | 37.00 |
| 467 | Kebbi | Suru | 104.00 |
| 468 | Kebbi | Wasagu/Danko | 32.00 |
| 469 | Kebbi | Yauri | 52.00 |
| 470 | Kebbi | Zuru | 24.00 |
| 471 | Kogi | Adavi | 98.00 |
| 472 | Kogi | Ajaokuta | 90.00 |
| 473 | Kogi | Ankpa | 98.00 |
| 474 | Kogi | Bassa | 30.00 |
| 475 | Kogi | Dekina | 97.00 |
| 477 | Kogi | Idah | 98.00 |
| 478 | Kogi | Igalamela-Odolu | 96.00 |
| 479 | Kogi | Ijumu | 98.00 |
| 480 | Kogi | Kabba/Bunu | 98.00 |
| 481 | Kogi | Kogi | 83.00 |
| 482 | Kogi | Lokoja | 85.00 |
| 483 | Kogi | Mopa-Muro | 98.00 |
| 484 | Kogi | Ofu | 97.00 |
| 485 | Kogi | Ogori/Magongo | 26.00 |
| 488 | Kogi | Olamaboro | 97.00 |
| 489 | Kogi | Omala | 103.10 |
| 490 | Kogi | Yagba East | 98.00 |
| 491 | Kogi | Yagba West | 98.00 |
| 493 | Kwara | Baruten | 25.00 |
| 494 | Kwara | Edu | 103.00 |
| 497 | Kwara | Ilorin East | 106.00 |
| 498 | Kwara | Ilorin South | 107.00 |
| 499 | Kwara | Ilorin West | 107.00 |
| 502 | Kwara | Kaiama | 53.00 |
| 503 | Kwara | Moro | 98.00 |
| 508 | Lagos | Agege | 105.90 |
| 509 | Lagos | Ajeromi-Ifelodun | 106.10 |
| 510 | Lagos | Alimosho | 104.80 |
| 511 | Lagos | Amuwo-Odofin | 109.10 |
| 512 | Lagos | Apapa | 109.00 |
| 513 | Lagos | Badagry | 48.00 |
| 514 | Lagos | Epe | 102.90 |
| 515 | Lagos | Eti-Osa | 85.00 |
| 516 | Lagos | Ibeju-Lekki | 103.90 |
| 517 | Lagos | Ifako-Ijaiye | 104.80 |
| 519 | Lagos | Ikorodu | 103.00 |
| 520 | Lagos | Kosofe | 107.10 |
| 521 | Lagos | Lagos Island | 110.20 |
| 522 | Lagos | Lagos Mainland | 88.00 |
| 523 | Lagos | Mushin | 109.40 |
| 524 | Lagos | Ojo | 107.10 |
| 525 | Lagos | Oshodi-Isolo | 110.30 |
| 526 | Lagos | Shomolu | 108.40 |
| 528 | Nasarawa | Akwanga | 21.00 |
| 529 | Nasarawa | Awe | 80.00 |
| 530 | Nasarawa | Doma | 55.00 |
| 531 | Nasarawa | Karu | 72.00 |
| 532 | Nasarawa | Keana | 50.00 |
| 533 | Nasarawa | Keffi | 54.00 |
| 534 | Nasarawa | Kokona | 32.00 |
| 535 | Nasarawa | Lafia | 59.00 |
| 536 | Nasarawa | Nasarawa | 54.00 |
| 537 | Nasarawa | Nasarawa Eggon | 22.00 |
| 538 | Nasarawa | Obi | 57.00 |
| 539 | Nasarawa | Toto | 78.00 |
| 540 | Nasarawa | Wamba | 28.00 |
| 541 | Niger | Agaie | 101.00 |
| 542 | Niger | Agwara | 27.00 |
| 543 | Niger | Bida | 98.00 |
| 544 | Niger | Borgu | 46.00 |
| 545 | Niger | Bosso | 92.00 |
| 546 | Niger | Chanchaga | 93.00 |
| 547 | Niger | Edati | 102.00 |
| 549 | Niger | Gurara | 87.00 |
| 550 | Niger | Katcha | 102.00 |
| 551 | Niger | Kontagora | 64.00 |
| 552 | Niger | Lapai | 104.10 |
| 553 | Niger | Lavun | 103.00 |
| 554 | Niger | Magama | 42.00 |
| 555 | Niger | Mariga | 45.00 |
| 556 | Niger | Mashegu | 62.00 |
| 557 | Niger | Mokwa | 103.00 |
| 558 | Niger | Munya | 85.00 |
| 559 | Niger | Paikoro | 96.00 |
| 560 | Niger | Rafi | 95.00 |
| 561 | Niger | Rijau | 40.00 |
| 562 | Niger | Shiroro | 88.00 |
| 563 | Niger | Suleja | 83.00 |
| 564 | Niger | Tafa | 60.00 |
| 565 | Niger | Wushishi | 86.00 |
| 570 | Ogun | Ifo | 108.00 |
| 576 | Ogun | Imeko Afon | 96.00 |
| 577 | Ogun | Ipokia | 95.00 |
| 584 | Ogun | Yewa North | 98.00 |
| 585 | Ogun | Yewa South | 106.00 |
| 667 | Plateau | Barkin Ladi | 75.00 |
| 668 | Plateau | Bassa | 10.00 |
| 669 | Plateau | Bokkos | 20.00 |
| 670 | Plateau | Jos East | 25.00 |
| 671 | Plateau | Jos North | 80.00 |
| 672 | Plateau | Jos South | 85.00 |
| 673 | Plateau | Kanam | 28.00 |
| 674 | Plateau | Kanke | 85.00 |
| 675 | Plateau | Langtang North | 87.00 |
| 676 | Plateau | Langtang South | 65.00 |
| 677 | Plateau | Mangu | 20.00 |
| 678 | Plateau | Mikang | 15.00 |
| 679 | Plateau | Pankshin | 49.00 |
| 680 | Plateau | Qua'an Pan | 15.00 |
| 681 | Plateau | Riyom | 65.00 |
| 682 | Plateau | Shendam | 22.00 |
| 683 | Plateau | Wase | 65.00 |
| 684 | Rivers | Abua/Odual | 15.00 |
| 685 | Rivers | Ahoada East | 25.00 |
| 686 | Rivers | Ahoada West | 50.50 |
| 687 | Rivers | Akuku-Toru | 106.10 |
| 688 | Rivers | Andoni | 11.70 |
| 689 | Rivers | Asari-Toru | 108.10 |
| 691 | Rivers | Degema | 75.00 |
| 692 | Rivers | Eleme | 21.80 |
| 695 | Rivers | Gokana | 106.90 |
| 697 | Rivers | Khana | 106.90 |
| 698 | Rivers | Obio/Akpor | 89.00 |
| 699 | Rivers | Ogba/Egbema/Ndoni | 30.50 |
| 700 | Rivers | Ogu/Bolo | 108.90 |
| 701 | Rivers | Okrika | 110.00 |
| 703 | Rivers | Opobo/Nkoro | 105.00 |
| 704 | Rivers | Oyigbo | 90.30 |
| 705 | Rivers | Port Harcourt | 89.00 |
| 706 | Rivers | Tai | 106.90 |
| 707 | Sokoto | Binji | 98.00 |
| 710 | Sokoto | Gada | 108.00 |
| 713 | Sokoto | Gwadabawa | 98.00 |
| 714 | Sokoto | Illela | 110.00 |
| 716 | Sokoto | Kebbe | 102.00 |
| 719 | Sokoto | Sabon Birni | 108.00 |
| 720 | Sokoto | Shagari | 98.00 |
| 722 | Sokoto | Sokoto North | 106.00 |
| 723 | Sokoto | Sokoto South | 101.10 |
| 731 | Taraba | Bali | 85.00 |
| 732 | Taraba | Donga | 95.00 |
| 733 | Taraba | Gashaka | 92.00 |
| 735 | Taraba | Ibi | 85.00 |
| 736 | Taraba | Jalingo | 97.00 |
| 737 | Taraba | Karim Lamido | 60.00 |
| 738 | Taraba | Kurmi | 75.00 |
| 739 | Taraba | Lau | 95.00 |
| 740 | Taraba | Sardauna | 37.00 |
| 741 | Taraba | Takum | 92.00 |
| 742 | Taraba | Ussa | 92.00 |
| 743 | Taraba | Wukari | 90.00 |
| 744 | Taraba | Yorro | 97.00 |
| 745 | Taraba | Zing | 94.00 |
| 761 | Yobe | Yunusari | 110.10 |
| 762 | Yobe | Yusufari | 110.00 |
| 763 | Zamfara | Anka | 97.00 |
| 772 | Zamfara | Maru | 102.00 |
| 776 | Zamfara | Zurmi | 106.00 |

---
## 4. Religion Sum Check

Religion columns: `% Muslim, % Christian, % Traditionalist`

| Metric | Value |
|--------|-------|
| Min sum | 90.00 |
| Max sum | 100.00 |
| Mean sum | 99.37 |
| Median sum | 100.00 |
| Rows outside 99–101 | 73 |
| Rows deviating >1.0 from 100 | 73 |

### Rows with Religion Sum Deviation > 1.0

| Row (Excel) | State | LGA | Sum |
|-------------|-------|-----|-----|
| 634 | Oyo | Afijio | 93.00 |
| 635 | Oyo | Akinyele | 95.00 |
| 636 | Oyo | Atiba | 95.00 |
| 637 | Oyo | Atisbo | 91.00 |
| 638 | Oyo | Egbeda | 94.00 |
| 639 | Oyo | Ibadan North | 96.00 |
| 640 | Oyo | Ibadan North-East | 95.00 |
| 641 | Oyo | Ibadan North-West | 96.00 |
| 642 | Oyo | Ibadan South-East | 95.00 |
| 643 | Oyo | Ibadan South-West | 95.00 |
| 644 | Oyo | Ibarapa Central | 90.00 |
| 645 | Oyo | Ibarapa East | 90.00 |
| 646 | Oyo | Ibarapa North | 90.00 |
| 647 | Oyo | Ido | 92.00 |
| 648 | Oyo | Irepo | 92.00 |
| 649 | Oyo | Iseyin | 94.00 |
| 650 | Oyo | Itesiwaju | 92.00 |
| 651 | Oyo | Iwajowa | 91.00 |
| 652 | Oyo | Kajola | 92.00 |
| 653 | Oyo | Lagelu | 94.00 |
| 654 | Oyo | Ogbomosho North | 95.00 |
| 655 | Oyo | Ogbomosho South | 95.00 |
| 656 | Oyo | Ogo Oluwa | 92.00 |
| 657 | Oyo | Olorunsogo | 92.00 |
| 658 | Oyo | Oluyole | 95.00 |
| 659 | Oyo | Ona Ara | 94.00 |
| 660 | Oyo | Orelope | 92.00 |
| 661 | Oyo | Ori Ire | 92.00 |
| 662 | Oyo | Oyo East | 95.00 |
| 663 | Oyo | Oyo West | 95.00 |
| 664 | Oyo | Saki East | 91.00 |
| 665 | Oyo | Saki West | 93.00 |
| 666 | Oyo | Surulere | 92.00 |
| 667 | Plateau | Barkin Ladi | 95.00 |
| 668 | Plateau | Bassa | 93.00 |
| 669 | Plateau | Bokkos | 93.00 |
| 670 | Plateau | Jos East | 93.00 |
| 671 | Plateau | Jos North | 95.00 |
| 672 | Plateau | Jos South | 95.00 |
| 673 | Plateau | Kanam | 93.00 |
| 674 | Plateau | Kanke | 92.00 |
| 675 | Plateau | Langtang North | 93.00 |
| 676 | Plateau | Langtang South | 93.00 |
| 677 | Plateau | Mangu | 93.00 |
| 678 | Plateau | Mikang | 92.00 |
| 679 | Plateau | Pankshin | 92.00 |
| 680 | Plateau | Qua'an Pan | 92.00 |
| 681 | Plateau | Riyom | 93.00 |
| 682 | Plateau | Shendam | 93.00 |
| 683 | Plateau | Wase | 93.00 |
| 684 | Rivers | Abua/Odual | 92.00 |
| 685 | Rivers | Ahoada East | 96.00 |
| 686 | Rivers | Ahoada West | 95.00 |
| 687 | Rivers | Akuku-Toru | 90.00 |
| 688 | Rivers | Andoni | 90.00 |
| 689 | Rivers | Asari-Toru | 91.00 |
| 690 | Rivers | Bonny | 93.00 |
| 691 | Rivers | Degema | 91.00 |
| 692 | Rivers | Eleme | 95.00 |
| 693 | Rivers | Emohua | 94.00 |
| 694 | Rivers | Etche | 96.00 |
| 695 | Rivers | Gokana | 94.00 |
| 696 | Rivers | Ikwerre | 95.00 |
| 697 | Rivers | Khana | 94.00 |
| 698 | Rivers | Obio/Akpor | 95.00 |
| 699 | Rivers | Ogba/Egbema/Ndoni | 95.00 |
| 700 | Rivers | Ogu/Bolo | 92.00 |
| 701 | Rivers | Okrika | 91.00 |
| 702 | Rivers | Omuma | 96.00 |
| 703 | Rivers | Opobo/Nkoro | 91.00 |
| 704 | Rivers | Oyigbo | 96.00 |
| 705 | Rivers | Port Harcourt | 95.00 |
| 706 | Rivers | Tai | 95.00 |

---
## 5. Numeric Validation

Numeric columns identified: **109**

### 5a. Non-Numeric Values in Numeric Columns

No non-numeric values found in numeric columns. ✓

### 5b. Null/Missing Values in Numeric Columns

| Column | Null Count |
|--------|------------|
| % Muslim | 73 |

### 5c. Out-of-Range Values

| Column | Range | Violations |
|--------|-------|------------|
| Median Age Estimate | [15, 55] | 35 below 15 |

#### Sample Out-of-Range Rows (first 5 per column)

| Row (Excel) | Column | Value | Violation |
|-------------|--------|-------|-----------|
| 100 | Median Age Estimate | 14.9000 | < 15 |
| 102 | Median Age Estimate | 14.8000 | < 15 |
| 105 | Median Age Estimate | 14.9000 | < 15 |
| 112 | Median Age Estimate | 14.9000 | < 15 |
| 154 | Median Age Estimate | 14.9000 | < 15 |

---
## 6. Categorical Consistency

### `Terrain Type`

Unique values: **8** | Nulls: **0**

| Value | Count |
|-------|-------|
| tropical_forest | 207 |
| guinea_savanna | 168 |
| sudan_savanna | 152 |
| derived_savanna | 99 |
| sahel | 70 |
| mangrove_swamp | 35 |
| freshwater_swamp | 27 |
| montane | 16 |


### `Dominant Livelihood`

Unique values: **659** | Nulls: **0**

| Value | Count |
|-------|-------|
| subsistence farming, livestock rearing | 10 |
| Subsistence farming, livestock rearing | 9 |
| subsistence farming, livestock | 9 |
| subsistence farming, millet, groundnuts | 9 |
| subsistence farming | 8 |
| subsistence farming, petty trade | 5 |
| subsistence farming, millet, cowpeas | 4 |
| subsistence farming, livestock, displaced | 4 |
| subsistence farming, livestock, petty trade | 4 |
| farming, livestock, cross-border trade | 4 |
| fishing, farming, oil community work | 3 |
| cross-border trade, farming, livestock | 3 |
| subsistence farming millet, sorghum, pastoralism | 3 |
| Subsistence farming, oil palm, cassava | 2 |
| Subsistence farming, yam, cassava, oil palm | 2 |
| Subsistence farming, cassava, oil palm | 2 |
| Farming and petty trade | 2 |
| Government, commerce, and services | 2 |
| Artisanal fishing and oil community work | 2 |
| Oil community work and subsistence farming | 2 |
| Subsistence farming of cocoyam and cassava | 2 |
| Farming, petty trade, and civil service | 2 |
| Subsistence farming of yam and cassava | 2 |
| Artisanal fishing and subsistence farming | 2 |
| farming, fishing, oil community work | 2 |
| subsistence farming, livestock herding | 2 |
| farming, fishing, petty trade | 2 |
| subsistence farming, cash crops | 2 |
| farming, trade, fishing | 2 |
| farming, fishing, small-scale trade | 2 |
| farming, yams, cassava; conflict-disrupted | 2 |
| Subsistence farming, petty trade | 2 |
| Farming disrupted, IDP aid, petty trade | 2 |
| Farming disrupted, humanitarian aid, trade | 2 |
| Pastoralism, farming disrupted by conflict | 2 |
| Subsistence farming, yam, cassava, rice | 2 |
| farming, trade, civil service | 2 |
| commerce, oil services, manufacturing | 2 |
| fishing, oil production, water transport | 2 |
| farming, petty trading | 2 |
| Farming, trading, remittances, education | 2 |
| Farming, palm oil, small trade | 2 |
| Farming, trading, civil service | 2 |
| Farming, cassava, yam, palm produce | 2 |
| Subsistence farming, fishing, pastoralism | 2 |
| Subsistence farming, livestock, fishing | 2 |
| subsistence farming, groundnuts, livestock | 2 |
| farming, millet, sorghum, commerce | 2 |
| farming, millet, sorghum, cotton | 2 |
| farming, millet, groundnuts, commerce | 2 |
| farming, cotton, livestock, displaced | 2 |
| farming, cotton, livestock | 2 |
| subsistence farming millet, sorghum, groundnuts | 2 |
| subsistence farming, hunting, artisanal mining | 2 |
| farming, fishing, artisanal gold mining | 2 |
| subsistence farming yam, cassava, maize | 2 |
| farming yam, cassava, maize, petty trade | 2 |
| Subsistence farming, livestock herding, limited trade | 2 |
| cocoa farming, food crops, education | 2 |
| yam, cassava farming, livestock rearing | 2 |
| agriculture, artisanal mining, livestock | 2 |
| subsistence farming, nomadic pastoralism | 2 |
| government, commerce, services, trade | 2 |
| farming, fishing, pastoralism | 2 |
| farming, fishing, livestock rearing | 2 |
| artisanal gold mining, subsistence farming | 2 |
| Commerce, manufacturing, and petty trade | 1 |
| Commerce, manufacturing, artisan trade | 1 |
| Subsistence farming, petty trade, remittances | 1 |
| Subsistence farming, oil palm, petty trade | 1 |
| Farming, education, oil palm processing | 1 |
| Farming, crafts, petty trade, remittances | 1 |
| Manufacturing, commerce, farming | 1 |
| Farming, fishing, marginal oil extraction | 1 |
| Oil extraction, subsistence farming, fishing | 1 |
| Government, commerce, services, education | 1 |
| Farming, petty trade, government spillover | 1 |
| Subsistence farming and Benue River fishing | 1 |
| Pastoralism and subsistence farming | 1 |
| Farming maize, sorghum, and groundnuts | 1 |
| Subsistence farming millet and sorghum | 1 |
| Subsistence farming and fishing | 1 |
| Farming maize and yams, southern highlands | 1 |
| Farming and Benue River fishing | 1 |
| Disrupted subsistence farming, displacement | 1 |
| Farming and cross-border trade | 1 |
| Farming cotton, maize, and livestock | 1 |
| Disrupted farming, displacement economy | 1 |
| Commerce, cattle trade, and farming | 1 |
| Farming and peri-urban commerce | 1 |
| Fishing, farming, and local administration | 1 |
| Farming, fishing, and irrigation | 1 |
| Farming millet, sorghum, groundnuts | 1 |
| Subsistence farming in remote mountains | 1 |
| Mixed farming, commerce, and services | 1 |
| Petty trade, farming, and oil palm | 1 |
| Oil industry services and petty trade | 1 |
| Subsistence farming of cassava and citrus | 1 |
| Farming, civil service, and petty trade | 1 |
| Subsistence farming and civil service | 1 |
| Fishing, rice farming, and palm produce | 1 |
| Subsistence farming of cassava and vegetables | 1 |
| Oil services, fishing, and industrial work | 1 |
| Commerce, raffia crafts, and petty trade | 1 |
| Farming, trade, and transport services | 1 |
| Artisanal fishing and cross-border trade | 1 |
| Subsistence farming of cassava and palm | 1 |
| Subsistence farming and palm oil processing | 1 |
| Oil industry services and farming | 1 |
| Fishing, cross-border trade, and commerce | 1 |
| Subsistence farming and palm produce trade | 1 |
| Farming, fishing, and palm produce | 1 |
| Farming, fishing, and civil service | 1 |
| subsistence farming, petty trade, transit commerce | 1 |
| subsistence farming, fishing | 1 |
| farming, wood processing, trade | 1 |
| farming, fishing, trading | 1 |
| government services, commerce, education | 1 |
| subsistence farming, rice production, fishing | 1 |
| farming, expressway commerce, petty trade | 1 |
| fishing, trading, light manufacturing | 1 |
| commerce, trade, manufacturing, crafts | 1 |
| trading, farming, commerce | 1 |
| agriculture, trade, small enterprise | 1 |
| trade, farming, timber processing | 1 |
| manufacturing, auto parts, vehicle assembly | 1 |
| farming, small-scale trade | 1 |
| wholesale trade, commerce, import distribution | 1 |
| commerce, manufacturing, hospitality | 1 |
| farming, palm oil production, animal rearing | 1 |
| farming, palm produce, petty trading | 1 |
| farming, fishing, tourism, petty trade | 1 |
| farming, livestock, mining, pastoralism | 1 |
| civil service, commerce, agriculture, crafts | 1 |
| livestock rearing, crop farming | 1 |
| rice and maize farming, mining, livestock | 1 |
| subsistence farming, pastoralism | 1 |
| farming, livestock, petty trade | 1 |
| commerce, agriculture, agro-processing, education | 1 |
| farming, fishing along Gongola River | 1 |
| farming, fishing, small-scale mining, trade | 1 |
| farming, livestock, trade, mining | 1 |
| farming, cotton, ginger, mining | 1 |
| farming, mining, livestock rearing | 1 |
| farming, cassava, maize cultivation | 1 |
| fishing, farming, oil community work, trade | 1 |
| fishing, farming, palm oil production | 1 |
| farming, fishing, education sector | 1 |
| government services, commerce, trade | 1 |
| subsistence farming, yams, cassava, rice | 1 |
| farming, fishing; conflict-displaced livelihoods | 1 |
| subsistence farming, yams, cassava, fishing | 1 |
| subsistence farming, cassava, yams, fishing | 1 |
| commerce, cement industry, civil service, farming | 1 |
| farming, fishing; severely conflict-disrupted | 1 |
| farming, petty trade, cassava processing | 1 |
| farming, trade, fishing, small-scale commerce | 1 |
| subsistence farming, yams, cassava, soybeans | 1 |
| farming, trade, yams, citrus, cassava | 1 |
| civil service, commerce, petty trade, farming | 1 |
| subsistence farming, yams, rice, cassava | 1 |
| farming, yams, cassava, palm oil production | 1 |
| subsistence farming, fishing, cassava, yams | 1 |
| subsistence farming, yams, cassava, palm produce | 1 |
| farming, yams, cassava, rice, palm oil | 1 |
| commerce, civil service, farming, yam trade | 1 |
| farming, cassava, yams, soybeans, sesame | 1 |
| farming, yam trade, soybeans, small commerce | 1 |
| farming, citrus, rice, cassava, grains | 1 |
| farming, trade, citrus, palm oil, cassava | 1 |
| Fishing, farming, livestock (pre-conflict) | 1 |
| Farming, IDP aid dependency, petty trade | 1 |
| Farming, trade, livestock rearing | 1 |
| Livelihoods collapsed; NSAG-controlled territory | 1 |
| Commerce, farming, petty trade, IDP services | 1 |
| Farming disrupted, trade along A3 highway | 1 |
| Farming and fishing disrupted by conflict | 1 |
| Farming, livestock, petty trade | 1 |
| Fishing, farming collapsed; aid dependent | 1 |
| Subsistence farming, livestock | 1 |
| Farming disrupted, humanitarian aid dependency | 1 |
| Farming disrupted, pastoralism, aid dependent | 1 |
| Commerce, civil service, petty trade | 1 |
| Fishing, farming collapsed; NSAG disruption | 1 |
| Fishing, farming disrupted, aid dependent | 1 |
| Cross-border trade disrupted, aid dependent | 1 |
| Subsistence farming, cassava, yam trading | 1 |
| Limestone quarrying, cement, farming | 1 |
| Fishing, farming, petty trading | 1 |
| Artisanal fishing, seafood trade | 1 |
| Subsistence farming, palm oil, cassava | 1 |
| Cocoa, coffee, timber, palm produce | 1 |
| Civil service, commerce, tourism, education | 1 |
| Commerce, fishing, port activities, trading | 1 |
| Cocoa farming, cross-border trade, cassava | 1 |
| Cocoa trade, commerce, farming, transport | 1 |
| Highland farming, livestock rearing | 1 |
| Farming, petty trading, palm produce | 1 |
| Tourism, highland agriculture, livestock rearing | 1 |
| Farming, trading, some industrial spillover | 1 |
| Commerce, civil service, farming, trade | 1 |
| Farming, yam, cassava, palm produce | 1 |
| farming, education, civil service | 1 |
| fishing, oil-related work, farming | 1 |
| fishing, oil work, subsistence farming | 1 |
| mixed farming, oil-related services | 1 |
| farming, trade, rubber processing | 1 |
| farming, trade, commerce | 1 |
| subsistence farming, cassava processing | 1 |
| farming, oil-related work, education | 1 |
| farming, fishing, oil-related services | 1 |
| farming, fishing, oil-related work | 1 |
| farming, oil services, trading | 1 |
| oil services, farming, trading | 1 |
| government, commerce, services | 1 |
| fishing, farming, oil-related work | 1 |
| timber, rubber, oil services, trade | 1 |
| oil production, farming, commerce | 1 |
| oil production, farming, fishing | 1 |
| farming, cassava processing, trading | 1 |
| oil industry hub, commerce, manufacturing | 1 |
| government, commerce, rice farming, mining | 1 |
| farming, trade, fishing, palm produce | 1 |
| farming, fishing along Cross River | 1 |
| farming, cassava, yam cultivation | 1 |
| farming, yam, cassava production | 1 |
| rice farming, palm wine, fishing | 1 |
| farming, stone quarrying, limestone mining | 1 |
| mining, quarrying, farming | 1 |
| farming, yam, cassava, rice production | 1 |
| salt mining, farming, trade | 1 |
| farming, cross-border trade | 1 |
| farming, quarrying, trading, hunting | 1 |
| residential, commerce, education, services | 1 |
| farming, trade, healthcare services | 1 |
| trade, farming, artisanship, services | 1 |
| farming, petty trading, civil service | 1 |
| education, farming, trade, services | 1 |
| farming, fishing, petty trading | 1 |
| education, trade, commerce, farming | 1 |
| commerce, industry, services, farming | 1 |
| government, commerce, trade, services | 1 |
| farming, oil and gas, rubber, trading | 1 |
| farming, rubber, oil exploration, trade | 1 |
| rubber, farming, timber, palm oil | 1 |
| farming, hunting, timber processing | 1 |
| farming, rubber, petty trading | 1 |
| rubber, farming, palm oil production | 1 |
| Civil service, commerce, education, cocoa trade | 1 |
| Cocoa, kola nut, maize farming, petty trade | 1 |
| Subsistence farming, yam, cassava, palm oil | 1 |
| Banana, plantain, cassava farming, petty trade | 1 |
| Cocoa farming, tourism, textile weaving, trade | 1 |
| Cassava, maize farming, small-scale trade | 1 |
| Rice, cassava, oil palm farming, petty trade | 1 |
| Rice, cassava, cocoa farming, stone quarrying | 1 |
| Cocoa farming, artisanal mining, cottage industries | 1 |
| Cocoa farming, palm oil, trade, education | 1 |
| Yam, cassava farming, agro-processing, trade | 1 |
| Pepper, coconut, cassava, cocoa subsistence farming | 1 |
| Farming, timber sawmilling, trade, tourism | 1 |
| Maize, cassava, pepper farming, palm oil trade | 1 |
| Farming, traditional economy, petty trade | 1 |
| Education services, farming, food processing, trade | 1 |
| Subsistence rice, cassava farming, petty trade | 1 |
| Cassava, yam farming, palm wine, quarrying | 1 |
| Commerce, retail, services, manufacturing, real estate | 1 |
| Government, commerce, education, professional services | 1 |
| Trade, education, tech startups, residential services | 1 |
| Cassava farming, abacha production, tourism | 1 |
| Cassava, yam, kolanut farming, pottery, trade | 1 |
| Yam, cassava farming, trade, palm wine | 1 |
| Subsistence yam, palm oil farming, crafts | 1 |
| Rice, cassava subsistence farming, border trade | 1 |
| Rice, cassava, palm produce farming, trade | 1 |
| Farming, trade, manufacturing, commuter services | 1 |
| Education, agriculture, agri-trade, weaving, commerce | 1 |
| Agriculture, palm oil, education, small commerce | 1 |
| Commerce, transit trade, agriculture, horse trading | 1 |
| Farming, palm wine, artisan crafts, tourism | 1 |
| Subsistence farming, yam, cassava, petty trade | 1 |
| Federal government, diplomacy, finance, real estate | 1 |
| Education, quarrying, commuter services, trade | 1 |
| Education, agriculture, trading, transport services | 1 |
| Agriculture, food production, livestock, real estate | 1 |
| Farming, pottery crafts, shea nut processing | 1 |
| Agriculture, commerce, livestock trading | 1 |
| Subsistence farming, fishing, livestock | 1 |
| Farming, small-scale mining, trading | 1 |
| Pastoral livestock, dryland crop farming | 1 |
| Cement manufacturing, farming, livestock | 1 |
| Commerce, civil service, farming | 1 |
| Farming, hunting, craft production, trading | 1 |
| Farming, petty trading, livestock rearing | 1 |
| Farming, pottery, livestock, craftsmanship | 1 |
| Subsistence farming, cattle rearing, hunting | 1 |
| Farming, livestock rearing, fishing | 1 |
| Farming, trading, remittances | 1 |
| Farming, palm oil, timber, trading | 1 |
| Farming, cassava, palm oil, trading | 1 |
| Farming, cassava, yam, small trade | 1 |
| Farming, trading, airport services | 1 |
| Farming, palm oil, small trading | 1 |
| Farming, trading, crafts, education | 1 |
| Farming, palm oil, trading | 1 |
| Farming, cassava, palm produce, trading | 1 |
| Oil work, fishing, farming, tourism | 1 |
| Oil work, farming, fishing, palm oil | 1 |
| Trading, education, civil service, farming | 1 |
| Commerce, pharma trade, banking, education | 1 |
| Farming, palm oil, cassava, trading | 1 |
| Oil work, farming, palm oil, trading | 1 |
| Farming, marginal oil, palm oil, trading | 1 |
| Commerce, civil service, services, education | 1 |
| Commerce, education, real estate, farming | 1 |
| Commerce, farming, real estate, services | 1 |
| Irrigation farming, fishing, livestock | 1 |
| Farming, livestock, cross-border trade | 1 |
| Subsistence farming, pastoralism, fishing | 1 |
| Commerce, farming, small-scale industry | 1 |
| Civil service, commerce, farming | 1 |
| Farming, emerging light manufacturing | 1 |
| Farming, commerce, traditional crafts | 1 |
| Farming, livestock, small-scale mining | 1 |
| Subsistence farming, pastoralism | 1 |
| Commerce, irrigation farming, fishing, trade | 1 |
| Farming, small-scale commerce, livestock | 1 |
| Farming, irrigation, livestock, education | 1 |
| Subsistence and irrigation farming, fishing | 1 |
| Education, farming, commerce, crafts | 1 |
| Farming, livestock, small trade | 1 |
| Cross-border trade, livestock, farming | 1 |
| Farming, irrigation, livestock rearing | 1 |
| Farming, commerce, livestock trade | 1 |
| Subsistence farming, pastoralism, trade | 1 |
| subsistence farming, artisanal gold mining | 1 |
| peri-urban commerce, farming, livestock | 1 |
| commerce, transport, farming, military sector | 1 |
| farming, trade, tin mining | 1 |
| government, commerce, manufacturing, services | 1 |
| commerce, manufacturing, refinery, services | 1 |
| farming, iron ore mining | 1 |
| subsistence farming, groundnuts, cereals | 1 |
| subsistence farming, trade | 1 |
| education, commerce, services | 1 |
| subsistence farming, artisanal mining | 1 |
| subsistence farming, cereals, livestock | 1 |
| education, commerce, government, crafts | 1 |
| farming, millet, rice, fishing | 1 |
| subsistence farming, millet, livestock | 1 |
| farming, groundnuts, commerce | 1 |
| irrigated farming, rice, groundnuts | 1 |
| commerce, traditional crafts, dyeing | 1 |
| farming, vegetables, peri-urban trade | 1 |
| grain trade, farming, international commerce | 1 |
| farming, cattle rearing, artisanal mining | 1 |
| commerce, wholesale, retail, transport | 1 |
| irrigated farming, rice, vegetables | 1 |
| farming, commodity trade, commerce | 1 |
| commerce, education, services | 1 |
| farming, millet, sorghum, trade | 1 |
| commerce, government, tourism, crafts | 1 |
| farming, groundnuts, livestock, trade | 1 |
| manufacturing, commerce, farming | 1 |
| irrigated rice and vegetable farming | 1 |
| farming, groundnuts, petty commerce | 1 |
| farming, millet, cowpeas, commerce | 1 |
| commerce, manufacturing, government, banking | 1 |
| farming, groundnuts, rice, commerce | 1 |
| farming, millet, cotton, artisanal mining | 1 |
| commerce, services, residential | 1 |
| urban commerce, peri-urban farming | 1 |
| livestock trading, farming, education | 1 |
| farming, cotton, grain trade, fishing | 1 |
| farming, cattle rearing, suburban trade | 1 |
| subsistence farming, cross-border trade | 1 |
| farming, livestock trade, secondhand trade | 1 |
| commerce, farming, education, government | 1 |
| farming, cotton, education, commerce | 1 |
| commerce, cotton trade, manufacturing | 1 |
| farming, kaolin processing, livestock | 1 |
| farming, groundnut oil processing | 1 |
| commerce, government, education, agriculture | 1 |
| subsistence farming, cattle rearing | 1 |
| farming, cotton ginning, grain processing | 1 |
| farming, livestock, trade | 1 |
| subsistence farming, cross-border activity | 1 |
| subsistence farming grains, onions, pastoralism | 1 |
| fishing, rice farming, tourism, petty trade | 1 |
| rice farming, fishing, livestock rearing | 1 |
| government services, commerce, rice trade | 1 |
| subsistence farming sorghum, millet, livestock | 1 |
| farming millet, rice, sorghum, commerce | 1 |
| farming millet, sorghum, rice, commerce | 1 |
| fishing, rice farming, alluvial gold panning | 1 |
| farming sorghum, millet, fishing, gold panning | 1 |
| subsistence farming millet, sorghum, rice, livestock | 1 |
| subsistence farming, fishing, artisanal mining | 1 |
| farming, artisanal gold mining, commerce | 1 |
| farming, steel company employment, mining | 1 |
| farming yam, cassava; coal mining Okaba | 1 |
| subsistence farming, fishing along rivers | 1 |
| subsistence farming yam, cassava, rice | 1 |
| rice farming, fishing, subsistence farming | 1 |
| trade, fishing on Niger River, farming | 1 |
| subsistence farming cassava, yam, rice | 1 |
| farming yam, cassava, cocoa, cashew | 1 |
| farming yam, cassava, cocoa, cashew, rice | 1 |
| farming, fishing, some mining activity | 1 |
| civil service, trade, transportation hub | 1 |
| farming cashew, gold mining, processing | 1 |
| farming yam, cassava, some mining | 1 |
| farming, iron ore mining employment | 1 |
| trade, farming, artisanal mining, commerce | 1 |
| farming, fishing along Benue, coal mining | 1 |
| farming cashew, cocoa, artisanal gold mining | 1 |
| farming cashew, artisanal gold mining | 1 |
| farming yam, maize, cattle rearing, border trade | 1 |
| farming rice, cassava, fishing on Niger River | 1 |
| farming cocoa, kola nut, cassava, yam | 1 |
| farming yam, cassava, shea butter processing | 1 |
| civil service, trade, education, urban farming | 1 |
| civil service, education, trade, services | 1 |
| civil service, commerce, artisan crafts, services | 1 |
| farming yam, cassava, trade, shea butter | 1 |
| farming yam, cassava, cocoa, kola nut | 1 |
| farming yam, soya beans, guinea corn, cassava | 1 |
| farming yam, maize, rice, dam employment | 1 |
| trade, weaving, dyeing, farming, education | 1 |
| farming cocoa, kola nut, yam, cassava | 1 |
| farming cassava, rice, fishing, artisanal mining | 1 |
| Petty trade, market commerce, artisanal work | 1 |
| Informal trade, port-related casual labor | 1 |
| Mixed trade, small manufacturing, services | 1 |
| Residential services, civil service, trade | 1 |
| Port logistics, maritime trade, warehousing | 1 |
| Fishing, farming, cross-border trade, tourism | 1 |
| Fishing, farming, small-scale trade | 1 |
| Financial services, real estate, corporate sector | 1 |
| Fishing, farming, emerging industrial zone | 1 |
| Residential services, retail trade, light industry | 1 |
| Government administration, aviation, commerce | 1 |
| Mixed farming, trade, light manufacturing | 1 |
| Commerce, transportation services, trade | 1 |
| Commerce, wholesale and retail trade | 1 |
| Education, tech startups, commerce, services | 1 |
| Informal trade, artisanal manufacturing, commerce | 1 |
| Trade, education, services, peri-urban farming | 1 |
| Transportation hub, light industry, trade | 1 |
| Printing industry, small trade, residential services | 1 |
| Residential services, entertainment, commerce | 1 |
| Subsistence farming, education, small-scale trade | 1 |
| Subsistence farming, salt mining, livestock | 1 |
| Commerce, services, transport, urban agriculture | 1 |
| Subsistence farming, artisanal salt production | 1 |
| Commerce, education, farming, livestock trade | 1 |
| Subsistence farming, small-scale trade | 1 |
| Government services, commerce, agriculture, education | 1 |
| Farming, tin and columbite mining, trade | 1 |
| Subsistence farming, small trade, crafts | 1 |
| Subsistence farming, some coal-related activity | 1 |
| Subsistence farming, artisanal mining, fishing | 1 |
| Subsistence farming, artisanal mining, tourism | 1 |
| Rice farming, yam cultivation, petty trade | 1 |
| Subsistence farming, livestock, cross-border trade | 1 |
| Rice farming, traditional crafts, trade hub | 1 |
| Fishing, farming, hydropower, tourism, livestock | 1 |
| Government services, education, urban commerce | 1 |
| Government administration, commerce, services | 1 |
| Riverine fishing, rice paddy farming, subsistence | 1 |
| Rice cultivation, yam farming, fishing | 1 |
| Farming, livestock, small-scale gold prospecting | 1 |
| Riverine fishing, rice farming, subsistence crops | 1 |
| Commerce, cotton and groundnut trade, livestock | 1 |
| Farming, small-scale trade, government services | 1 |
| Rice farming, fishing, shea nut processing | 1 |
| Subsistence farming, livestock, artisanal gold mining | 1 |
| Farming, livestock herding, artisanal gold mining | 1 |
| Farming, highway commerce, fishing, trade transit | 1 |
| Subsistence farming disrupted by banditry, livestock | 1 |
| Farming yams maize millet, livestock rearing | 1 |
| Farming severely disrupted by banditry, livestock | 1 |
| Farming, fishing, hydropower-related employment | 1 |
| Commerce, commuter services to Abuja, pottery | 1 |
| Peri-urban farming, real estate, commuter services | 1 |
| Farming rice guinea corn millet, livestock | 1 |
| civil service, trade, government, education | 1 |
| civil service, commerce, banking, education | 1 |
| manufacturing, industry, trade, services | 1 |
| cement production, quarrying, farming | 1 |
| trade, small manufacturing, services, farming | 1 |
| farming, timber, cocoa, oil palm | 1 |
| trade, farming, cocoa, kolanut, education | 1 |
| commerce, trade, education, transport services | 1 |
| education, farming, trade, cocoa | 1 |
| subsistence farming, cattle rearing, cross-border trade | 1 |
| farming, cross-border trade, fishing | 1 |
| agriculture, commuter services, Ofada rice, trade | 1 |
| farming, education, granite quarrying | 1 |
| farming, cassava, cocoa, petty trade | 1 |
| fishing, subsistence farming, waterway trade | 1 |
| farming, trade, artisanry | 1 |
| commerce, industry, cement, kolanut trade | 1 |
| farming, cross-border trade, cement industry | 1 |
| farming, education, trade, livestock rearing | 1 |
| trading, cocoa farming, kolanut, commerce | 1 |
| farming, cocoa, teaching, food crops | 1 |
| farming, cocoa, education, petty trade | 1 |
| agriculture, trading, cocoa, food crops | 1 |
| farming, trade, suburban commuter services | 1 |
| civil service, trade, education, commerce | 1 |
| fishing, subsistence farming, petty trading | 1 |
| cocoa farming, palm produce, food crops | 1 |
| fishing, oil production, palm oil, trading | 1 |
| farming, palm oil processing, cocoa, rubber | 1 |
| commerce, transit services, farming, cocoa | 1 |
| farming, cassava, cocoa, education | 1 |
| farming, palm oil, timber, local crafts | 1 |
| trade, artisanship, cocoa, education | 1 |
| cocoa farming, plantation farming, timber | 1 |
| trade, cocoa farming, education, civil service | 1 |
| cocoa farming, oil palm, trade | 1 |
| farming, livestock rearing, local trade | 1 |
| gold mining, cocoa farming, agriculture | 1 |
| cocoa farming, artisanal gold mining, oil palm | 1 |
| subsistence farming, food crops, local trade | 1 |
| agriculture, education, trade, cultural festivals | 1 |
| trade, agriculture, cocoa processing, education | 1 |
| farming, trade, services | 1 |
| agriculture, trade, civil service commuting | 1 |
| farming, food crops, trade, education | 1 |
| education, civil service, trade, cultural tourism | 1 |
| education, agriculture, trade, cassava farming | 1 |
| farming, cassava production, local trade | 1 |
| cocoa farming, oil palm, food crops | 1 |
| subsistence farming, textile dyeing, hunting | 1 |
| agriculture, trade, local commerce | 1 |
| farming, trade, local commerce | 1 |
| trade, cocoa marketing, gold mining, education | 1 |
| trade, commerce, gold mining, agriculture | 1 |
| agriculture, trade, commuter services | 1 |
| agriculture, trade, food processing, palm oil | 1 |
| farming, trade, food crops | 1 |
| education, agriculture, trade, commerce | 1 |
| agriculture, trade, cultural heritage | 1 |
| agriculture, education, trade | 1 |
| farming, timber production, local trade | 1 |
| civil service, trade, agriculture, services | 1 |
| agriculture, tourism, cocoa farming | 1 |
| farming, cassava production, trade | 1 |
| civil service, commerce, industry, tourism | 1 |
| yam and cassava farming, petty trade | 1 |
| maize and cassava farming, petty trade | 1 |
| civil service, trade, farming, tourism | 1 |
| cassava and yam farming, livestock | 1 |
| farming, petty trade, suburban development | 1 |
| education, civil service, commerce, healthcare | 1 |
| commerce, transport, artisanal trades | 1 |
| government, banking, commerce, hospitality | 1 |
| petty trade, artisanal crafts, commerce | 1 |
| commerce, banking, industry, transport | 1 |
| yam, cassava, cocoa farming, trade | 1 |
| farming, agro-processing, education | 1 |
| cassava, yam farming, livestock rearing | 1 |
| farming, logging, charcoal production | 1 |
| farming, cattle rearing, border trade | 1 |
| aso-oke weaving, farming, tobacco, trade | 1 |
| subsistence farming, hunting, livestock | 1 |
| cocoa, yam farming, cloth weaving | 1 |
| cotton, tobacco farming, weaving, trade | 1 |
| farming, petty trade, suburban housing | 1 |
| commerce, education, civil service, trade | 1 |
| farming, petty trade, artisanal crafts | 1 |
| farming, quarrying, petty trade | 1 |
| farming, commerce, light manufacturing | 1 |
| cassava, vegetable farming, petty trade | 1 |
| yam, cassava farming, livestock, trade | 1 |
| yam, cassava farming, cattle rearing | 1 |
| commerce, civil service, farming, education | 1 |
| commerce, farming, cattle, border trade | 1 |
| agriculture and artisanal tin mining | 1 |
| Irish potato farming, vegetables, mining | 1 |
| agriculture, livestock rearing, trading | 1 |
| commerce, civil service, education, trade | 1 |
| industry, tin mining, agriculture | 1 |
| farming, pastoralism, river fishing | 1 |
| agriculture, civil service, small trading | 1 |
| subsistence farming, small livestock | 1 |
| agriculture, artisanal tin mining, trade | 1 |
| subsistence farming, small-scale fishing | 1 |
| agriculture, livestock rearing, trade | 1 |
| rice farming, subsistence agriculture | 1 |
| agriculture, trading, fishing | 1 |
| farming, pastoralism, fishing, trade | 1 |
| farming, fishing, forest product trade | 1 |
| farming, fishing, timber, petty trade | 1 |
| rural farming, canoe building, trade | 1 |
| fishing, oil servicing, boat building | 1 |
| deep-sea fishing, marine produce | 1 |
| fishing, palm oil trade, commerce | 1 |
| oil-gas employment, fishing, maritime | 1 |
| fishing, river farming, local trade | 1 |
| petrochemicals, refining, port logistics | 1 |
| palm oil production, farming, trade | 1 |
| cassava and palm oil farming, trade | 1 |
| farming, fishing, environmental activism | 1 |
| farming, aviation services, petty trade | 1 |
| agriculture, education, small trade | 1 |
| commerce, real estate, private services | 1 |
| oil-related activity, farming, fishing | 1 |
| fishing, petty trading, small farming | 1 |
| fishing, petroleum product trade | 1 |
| cassava and vegetable farming, trade | 1 |
| fishing, cultural tourism, riverine trade | 1 |
| power generation, warehousing, industry | 1 |
| oil services, shipping, banking, government | 1 |
| farming, youth programs, activism | 1 |
| subsistence farming, millet, sorghum, livestock | 1 |
| farming, livestock, trade, kaolin mining | 1 |
| farming, cement production, mining, trade | 1 |
| subsistence farming, livestock, coal mining | 1 |
| irrigated farming, fishing, livestock rearing | 1 |
| farming, onion production, livestock, trade | 1 |
| subsistence farming, livestock, pastoralism | 1 |
| farming, limestone mining, peri-urban trade | 1 |
| commerce, education, crafts, services | 1 |
| farming, fishing, livestock, river trade | 1 |
| subsistence farming, pastoralism, livestock | 1 |
| subsistence farming, livestock, gold panning | 1 |
| education, commerce, farming, cement industry | 1 |
| farming, gypsum mining, livestock rearing | 1 |
| farming, gold panning, livestock, trade | 1 |
| subsistence farming, yam, maize, cassava | 1 |
| farming, trade, cattle rearing | 1 |
| subsistence farming, pastoralism, forestry | 1 |
| farming, yam, cattle rearing, fishing | 1 |
| fishing, farming, small-scale trade | 1 |
| government, commerce, services, farming | 1 |
| farming, forestry, timber extraction | 1 |
| tea farming, pastoralism, subsistence crops | 1 |
| farming, trade, timber, small commerce | 1 |
| subsistence farming, forestry, hunting | 1 |
| farming, trade, fishing, education services | 1 |
| subsistence farming, maize, sorghum, millet | 1 |
| farming, cattle rearing, small-scale trade | 1 |
| farming, fishing, livestock, petty trade | 1 |
| farming, millet, sorghum, groundnuts | 1 |
| farming, millet, sorghum, livestock trade | 1 |
| farming, groundnuts, millet, livestock | 1 |
| commerce, trade, gum arabic, farming | 1 |
| livestock trade, commerce, farming | 1 |
| subsistence farming, millet, sorghum | 1 |
| farming, livestock, fishing, Lake Chad basin | 1 |
| government, commerce, farming, trade | 1 |
| commerce, farming, cotton, groundnuts trade | 1 |
| subsistence farming, livestock, herding | 1 |
| farming, livestock, artisanal gold mining | 1 |
| farming, commerce, tobacco, groundnuts | 1 |
| subsistence farming, millet, sorghum, trade | 1 |

**Potential spelling/capitalization variants:**
  - ['Manufacturing, commerce, farming', 'manufacturing, commerce, farming']
  - ['subsistence farming, pastoralism', 'Subsistence farming, pastoralism']
  - ['farming, livestock, petty trade', 'Farming, livestock, petty trade']
  - ['subsistence farming, petty trade', 'Subsistence farming, petty trade']
  - ['Subsistence farming, livestock rearing', 'subsistence farming, livestock rearing']
  - ['Subsistence farming, livestock', 'subsistence farming, livestock']
  - ['Farming, livestock, cross-border trade', 'farming, livestock, cross-border trade']
  - ['Fishing, farming, small-scale trade', 'fishing, farming, small-scale trade']

### `Almajiri Prevalence`

Unique values: **77** | Nulls: **308**

| Value | Count |
|-------|-------|
| *(null)* | 308 |
| HIGH | 190 |
| MEDIUM | 71 |
| NONE | 68 |
| LOW | 64 |
| Sunni Maliki Islam; Anglican/CMS and Pentecostal Christianity; Egungun tradition persists | 1 |
| Tijaniyya/Sunni Islam; Baptist, Anglican, Pentecostal Christianity growing | 1 |
| Sunni Maliki/Tijaniyya dominant; Anglican CMS est. 1856; Pentecostal growing | 1 |
| Sunni Maliki/Tijaniyya Islam dominant; some Anglican/Baptist; traditional Yoruba rites | 1 |
| Tijaniyya/Sunni Islam; Pentecostal/Baptist/Catholic Christianity; some Orisa practice | 1 |
| Diverse: Pentecostal/RCCG strong; Catholic/Anglican; Sunni/Ahmadiyya Islam; university area | 1 |
| Sunni/Tijaniyya Islam; Anglican/Methodist/Pentecostal Christianity; mixed urban core | 1 |
| Sunni/Tijaniyya Islam; Baptist HQ nearby; Pentecostal growth evident | 1 |
| Mixed Sunni Islam and Pentecostal/Anglican Christianity; Catholic presence | 1 |
| Pentecostal/Baptist/Catholic strong; Sunni/Tijaniyya Islam; Aladura churches | 1 |
| Anglican CMS mission from 1853; Sunni Islam; notable traditional Yoruba religion persists | 1 |
| CMS/Anglican strong; Baptist; Sunni Islam minority; Egungun/Orisa traditions persist | 1 |
| Anglican/Methodist Christianity; Sunni Islam; strong traditional religion in rural areas | 1 |
| Sunni Islam; Anglican/Pentecostal Christianity; rural areas retain traditional practices | 1 |
| Sunni Maliki/Tijaniyya Islam dominant; small Baptist/Anglican Christian community | 1 |
| Sunni Maliki Islam dominant (mosque est. 1760); Anglican/Baptist present | 1 |
| Sunni/Tijaniyya Islam dominant; Onko dialect area; Anglican minority present | 1 |
| Sunni Maliki/Tijaniyya Islam; small Christian minority; traditional rites in villages | 1 |
| Sunni/Tijaniyya Islam dominant; HQ Okeho; some Anglican/Baptist presence | 1 |
| Sunni/Tijaniyya Islam; Pentecostal/Baptist Christianity growing; peri-urban mixed | 1 |
| Baptist stronghold (seminary and hospital since 1855); Pentecostal/RCCG growing | 1 |
| Baptist/Methodist/Pentecostal dominant; Sunni Islam present; central mosque exists | 1 |
| Baptist/Methodist influence; Sunni Islam present; rural traditional practices persist | 1 |
| Sunni Maliki/Tijaniyya Islam dominant; HQ Igbeti; some Anglican presence | 1 |
| Mixed Sunni Islam and Pentecostal/Anglican Christianity; cosmopolitan southern Ibadan | 1 |
| Sunni/Tijaniyya Islam; Pentecostal/Anglican Christianity; peri-urban Ibadan | 1 |
| Sunni Maliki/Tijaniyya Islam dominant; HQ Igboho; small Christian minority | 1 |
| Baptist/Methodist influence; Sunni Islam significant; rural traditional practices | 1 |
| Sunni Maliki/Tijaniyya Islam; Anglican CMS; Crowther University (Anglican) | 1 |
| Sunni/Tijaniyya Islam; Anglican/CMS from 1856; Pentecostal growing | 1 |
| Sunni Maliki/Tijaniyya Islam dominant; Anglican/Baptist minority; traditional in villages | 1 |
| Sunni Maliki Islam (mosque est. 1790); Tijaniyya; Baptist Hospital; Anglican minority | 1 |
| Baptist/Methodist influence; Sunni Islam significant; rural traditional religion persists | 1 |
| Berom COCIN heartland; ECWA, Catholic; small Hausa-Fulani Sunni settler minority | 1 |
| Irigwe Christian majority; COCIN, Catholic; Hausa-Fulani Sunni in Miango area | 1 |
| Ron-Kulere Christian; COCIN, ECWA dominant; small Fulani pastoralist minority | 1 |
| Afizere Christian COCIN/ECWA; some Hausa-Fulani Sunni; Fulani pastoralists | 1 |
| Hausa-Fulani Sunni/Tijaniyya; Afizere/Anaguta COCIN/Catholic/Pentecostal present | 1 |
| Berom COCIN dominant; Catholic, Pentecostal growth; Hausa-Fulani Sunni minority | 1 |
| Hausa-Fulani Sunni/Tijaniyya; emirate structure; COCIN/ECWA Christian minority | 1 |
| Ngas Christian; COCIN, ECWA dominant; small Hausa trader Muslim minority | 1 |
| Tarok Christian heartland; COCIN, Catholic, Pentecostal; minimal Muslim presence | 1 |
| Tarok and related groups Christian; COCIN, ECWA; very minimal Muslim presence | 1 |
| Mwaghavul COCIN heartland; Pyem Christian; some Hausa-Fulani Sunni settlers | 1 |
| Montol/Tehl Christian; COCIN, ECWA; negligible Muslim; some traditionalist practices | 1 |
| Ngas, Mupun, Chip Christian; COCIN dominant; small Hausa-Fulani Muslim minority | 1 |
| Kofyar subgroups Christian; COCIN, ECWA; Nteng 97% Christian per Joshua Project | 1 |
| Berom Christian; COCIN dominant; Fulani pastoralist minority; farmer-herder tensions | 1 |
| Goemai Christian majority; COCIN, Catholic; Hausa-Fulani Sunni minority present | 1 |
| Hausa-Fulani Sunni/Tijaniyya; Wase emirate; Basharawa/Tarok Christian minority | 1 |
| Anglican, Catholic, Pentecostal dominant; water-spirit and ancestral traditions in riverine areas | 1 |
| Catholic, Anglican, Pentecostal dominant; Ekpeye people strongly Christian | 1 |
| Catholic, Anglican, Pentecostal; Ekpeye/Engenni peoples; some traditional farming rites | 1 |
| Anglican, Pentecostal; Kalabari Ijaw with strong Ekine masquerade and water-spirit traditions | 1 |
| Catholic, Anglican; Obolo people Christian since 1699; Nwantam masquerade and deity worship persist | 1 |
| Anglican, Pentecostal; Kalabari Ijaw; ancestral/water-spirit traditions woven into practice | 1 |
| Strong Anglican CMS 1864 heritage; Catholic, Pentecostal growing; traditional totem rites | 1 |
| Anglican, Pentecostal; Kalabari/Ijaw area; river shrine and fishing deity traditions | 1 |
| Catholic, Anglican, Pentecostal; Ogoni sub-group; traditional practices declining | 1 |
| Catholic, Anglican, Pentecostal; Ikwerre people; Ali earth-deity traditions documented | 1 |
| Catholic, Pentecostal dominant; Etche people culturally close to Igbo; strongly Christian | 1 |
| Anglican CMS from 1908, Pentecostal; Ogoni harvest deity and farming rites observed | 1 |
| Catholic, Anglican, Pentecostal; Ikwerre upland; Ali deity syncretism; minor Hausa traders | 1 |
| Anglican, Pentecostal; Ogoni heartland; Wa-Bari creator-deity beliefs persist | 1 |
| Pentecostal, Catholic, Anglican; Ikwerre base with urban settlers; Hausa Muslim traders | 1 |
| Catholic, Pentecostal dominant; Ogba/Egbema/Ndoni peoples; some rural traditional practice | 1 |
| Anglican, Pentecostal; coastal community; fishing-deity and water-spirit traditions persist | 1 |
| Anglican, Pentecostal; island community; strong masquerade and water-spirit practices | 1 |
| Catholic, Pentecostal dominant; Ikwerre/Etche upland area; minimal traditional practice | 1 |
| Anglican heritage Kingdom of Opobo/CMS; Pentecostal; masquerade and ancestral rites persist | 1 |
| Catholic, Pentecostal; diverse Igbo/Ogoni settlers; minor Hausa Muslim presence | 1 |
| Pentecostal, Catholic, Anglican; Eckankar HQ; significant Hausa Muslim community | 1 |
| Anglican, Pentecostal; Ogoni kingdom of Tai; traditional harvest deity practices declining | 1 |


### `Urban Rural Split`

Unique values: **41** | Nulls: **0**

| Value | Count |
|-------|-------|
| 15% urban / 85% rural | 101 |
| 10% urban / 90% rural | 98 |
| 20% urban / 80% rural | 75 |
| 25% urban / 75% rural | 63 |
| 30% urban / 70% rural | 55 |
| 5% urban / 95% rural | 52 |
| 35% urban / 65% rural | 44 |
| 40% urban / 60% rural | 34 |
| 12% urban / 88% rural | 29 |
| 8% urban / 92% rural | 26 |
| 18% urban / 82% rural | 23 |
| 55% urban / 45% rural | 20 |
| 65% urban / 35% rural | 16 |
| 50% urban / 50% rural | 14 |
| 85% urban / 15% rural | 12 |
| 75% urban / 25% rural | 12 |
| 45% urban / 55% rural | 12 |
| 80% urban / 20% rural | 10 |
| 60% urban / 40% rural | 10 |
| 70% urban / 30% rural | 9 |
| 90% urban / 10% rural | 9 |
| 100% urban / 0% rural | 7 |
| 95% urban / 5% rural | 6 |
| 28% urban / 72% rural | 6 |
| 100% urban | 6 |
| 22% urban / 78% rural | 5 |
| 98% urban / 2% rural | 3 |
| 88% urban / 12% rural | 2 |
| 6% urban / 94% rural | 2 |
| 38% urban / 62% rural | 2 |
| 5%% urban / 95%% rural | 1 |
| 40%% urban / 60%% rural | 1 |
| 15%% urban / 85%% rural | 1 |
| 78% urban / 22% rural | 1 |
| 62% urban / 38% rural | 1 |
| 90% urban / 10% peri-urban | 1 |
| 85% urban / 15% peri-urban | 1 |
| 92% urban / 8% rural | 1 |
| 96% urban / 4% rural | 1 |
| 97% urban / 3% rural | 1 |
| 7% urban / 93% rural | 1 |


### `Oil Producing`

Unique values: **2** | Nulls: **0**

| Value | Count |
|-------|-------|
| N | 705 |
| Y | 69 |


### `Road Infrastructure Quality`

Unique values: **756** | Nulls: **0**

| Value | Count |
|-------|-------|
| Poor; limited road infrastructure | 3 |
| Poor to fair; main roads partly paved | 2 |
| Poor; rural roads mostly unpaved | 2 |
| Poor; largely unpaved rural roads | 2 |
| Poor earth roads; conflict-damaged infrastructure | 2 |
| Rural roads poor but passable in dry season | 2 |
| Roads poor and insecure; unpaved rural tracks | 2 |
| Poor unpaved rural roads, limited connectivity | 2 |
| Poor rural roads, limited paved sections | 2 |
| Rural roads, fair to poor condition | 2 |
| Semi-urban roads, moderate condition | 2 |
| Poor; distribution network partly rehabilitated | 2 |
| Poor; secondary roads | 2 |
| Good; on A2 Trans-Sahara Highway | 2 |
| Fair; on A9 Kano-Katsina highway | 2 |
| Poor; limited secondary roads | 2 |
| A1 federal highway passes through; paved trunk road | 2 |
| Fair; major roads paved but poorly maintained | 1 |
| Fair to poor; congested, ongoing road repairs | 1 |
| Poor; rural roads largely unpaved and seasonal | 1 |
| Fair; proximity to Umuahia improves access | 1 |
| Poor; rural roads unpaved, seasonal flooding | 1 |
| Poor; hilly terrain, largely unpaved rural roads | 1 |
| Poor; rural roads largely unpaved | 1 |
| Fair; industrial corridors, some paved roads | 1 |
| Poor; riverine terrain, roads prone to flooding | 1 |
| Poor; rural roads largely unpaved, flood prone | 1 |
| Poor; hilly terrain, rural roads largely unpaved | 1 |
| Fair to good; capital roads paved, some maintained | 1 |
| Fair; peri-urban roads partly paved near capital | 1 |
| Poor rural roads, seasonal flooding near Benue | 1 |
| Fair near Yola, poor in remote areas | 1 |
| Fair; main roads to Jada and Toungo | 1 |
| Very poor, largely unpaved, seasonal impassability | 1 |
| Conflict-damaged, partially rehabilitated | 1 |
| Poor rural roads, limited bridges | 1 |
| Conflict-damaged, partially rehabilitated main road | 1 |
| Fair; seasonal road challenges in highlands | 1 |
| Poor rural roads, seasonal flooding | 1 |
| Severely damaged by conflict, largely impassable | 1 |
| Fair on main routes; poor in rural areas | 1 |
| Fair; main road passable year-round | 1 |
| Severely damaged, mountainous terrain compounds access | 1 |
| Fair in urban core; recovering from conflict | 1 |
| Fair near Mubi; deteriorating in rural areas | 1 |
| Fair on Yola-Numan road; poor in rural areas | 1 |
| Poor rural roads; limited bridges | 1 |
| Fair on main Yola-Mubi road; poor off-road | 1 |
| Very poor; impassable in rainy season | 1 |
| Best in state; paved roads, airport access | 1 |
| Fair; paved main roads, unpaved side roads | 1 |
| Moderate; main roads fair, rural roads poor | 1 |
| Very poor; limited roads, waterways dominant | 1 |
| Good; oil company roads, state highway maintained | 1 |
| Fair; some oil company access roads present | 1 |
| Poor; unpaved rural roads, seasonal flooding | 1 |
| Poor; mostly unpaved roads in disrepair | 1 |
| Fair; Etinan-Uyo road paved, rural roads poor | 1 |
| Very poor; limited roads, waterways primary | 1 |
| Fair; benefits from proximity to Uyo roads | 1 |
| Fair; connected to Uyo-Ikot Ekpene highway | 1 |
| Poor; largely riverine, few paved roads | 1 |
| Fair; some paved roads, rural areas poor | 1 |
| Fair; industrial roads exist but deteriorating | 1 |
| Good; major highway junction, paved state roads | 1 |
| Very poor; remote, unpaved, seasonal access only | 1 |
| Fair; Uyo-Calabar highway passes through LGA | 1 |
| Poor; coastal terrain, limited road network | 1 |
| Fair; some oil company roads, otherwise poor | 1 |
| Poor; mostly unpaved, seasonal flooding | 1 |
| Fair; connected to Uyo road network | 1 |
| Fair; some paved roads, rural roads poor | 1 |
| Very poor; remote, largely unpaved roads | 1 |
| Poor; coastal terrain, limited paved roads | 1 |
| Fair to good; oil company roads maintained | 1 |
| Fair; port town roads paved, hinterland poor | 1 |
| Poor; rural roads in disrepair, border area | 1 |
| Very poor; remote, unpaved, poorly maintained | 1 |
| Fair; Uyo-Oron road passes through LGA | 1 |
| Very poor; isolated coastal settlements | 1 |
| Good; paved roads, state capital infrastructure | 1 |
| Moderate paved roads linking Awka, Nnewi, and Orlu | 1 |
| Improving; cargo airport at Umueri; flood-prone access roads | 1 |
| Very poor; many communities boat-access only; flood damage | 1 |
| Moderate paved roads linking Awka and Aguata zones | 1 |
| Moderate; benefits from Onitsha-Enugu expressway proximity | 1 |
| Good; three flyovers on Enugu-Onitsha expressway | 1 |
| Poor; flood-prone laterite roads frequently damaged | 1 |
| Good; on Onitsha-Enugu expressway; most accessible LGA | 1 |
| Moderate; connected to Nnewi and Onitsha via Owerri Road | 1 |
| Good; part of Greater Onitsha conurbation road network | 1 |
| Moderate to good; on Onitsha-Nnewi-Owerri corridor | 1 |
| Moderate; on A6 Onitsha-Owerri road; border gateway LGA | 1 |
| Good; between Awka and Onitsha on major routes | 1 |
| Moderate; federal highway congested; road dualization ongoing | 1 |
| Limited; Nnewi-Okija road under construction | 1 |
| Collapsed; bridges destroyed; many areas boat-access only | 1 |
| Congested; Niger Bridge; severe traffic; road deterioration | 1 |
| Good in GRA and Fegge; suburban sprawl in Awada | 1 |
| Limited; rural roads in varying condition | 1 |
| Limited; secondary rural roads to Ekwulobia and Awka | 1 |
| Moderate to good; on Onitsha-Enugu corridor | 1 |
| A345 highway through north; poor rural interior roads | 1 |
| Best in state; A3 highway; railway; international airport | 1 |
| Poor state roads; conflict has damaged infrastructure | 1 |
| Poor; off Kano-Maiduguri road; limited internal roads | 1 |
| Moderate along Maiduguri road; flood damage common | 1 |
| Moderate; close to Bauchi city; state roads fair | 1 |
| Very poor; 295 km from capital; poorly maintained | 1 |
| Moderate; on Ningi Road from Bauchi; market town access | 1 |
| Moderate along Trans-Sahelian Highway; poor interior | 1 |
| Poor; remote northern border area; limited road maintenance | 1 |
| Moderate; state roads near Jigawa border | 1 |
| Relatively good; multiple trunk roads converge at Azare | 1 |
| Poor; gully erosion damaging roads and bridges | 1 |
| Moderate; on Trans-Sahelian Highway; emirate road network | 1 |
| Moderate; on road to Kano from Bauchi | 1 |
| Moderate on Trans-Sahelian Highway; poor interior roads | 1 |
| Damaged by ethno-religious conflict; HQ relocated to Bununu | 1 |
| Poor across vast 6932 km2 area; road to Jos fair | 1 |
| Poor; rural roads from Ningi; limited maintenance | 1 |
| Poor; remote northeast location near Yobe border | 1 |
| Very poor; island access by boat from Nembe only | 1 |
| Very poor; primarily boat access; 60 km coastline | 1 |
| Moderate; road-connected to Yenagoa; NDDC rigid pavement | 1 |
| Road to Nembe town from Yenagoa; boat beyond town | 1 |
| Semi-accessible; road from Yenagoa; creek areas by boat | 1 |
| Moderate; road from Yenagoa; NDDC road projects completed | 1 |
| Historically boat-only; road and bridge under construction | 1 |
| Best in state; Boro Expressway to East-West Road | 1 |
| Mostly unpaved rural roads; limited federal highway access | 1 |
| Poor earth roads; largely inaccessible in rainy season | 1 |
| Mostly unpaved roads; poor connectivity to Otukpo | 1 |
| Partially paved road to Gboko; mostly earth roads | 1 |
| Paved roads to Makurdi and Katsina-Ala; fair urban roads | 1 |
| Paved road from Makurdi to Aliade; rural roads poor | 1 |
| Naka-Makurdi road unsafe; rural roads degraded | 1 |
| Federal highway A4 passes through; urban roads moderate | 1 |
| Predominantly earth roads; poor rural connectivity | 1 |
| State road to Adikpo; mostly unpaved rural feeders | 1 |
| Federal highways A3 and A4; paved main roads in city | 1 |
| Mostly unpaved roads; hilly terrain limits access | 1 |
| Rail line passes through; road to Otukpo partially paved | 1 |
| Poor unpaved roads; very limited infrastructure | 1 |
| Mostly earth roads; hilly terrain limits accessibility | 1 |
| Partially paved road to Otukpo; rural roads poor | 1 |
| Federal highway A3; rail line; partially paved urban roads | 1 |
| State road through Wannune; mostly unpaved rural roads | 1 |
| State road to Zaki-Biam; rural roads in poor condition | 1 |
| State roads partially paved; rural feeder roads poor | 1 |
| State road from Gboko; partially paved urban roads | 1 |
| Roads inaccessible; no maintained infrastructure | 1 |
| Bama-Maiduguri road partially repaired; mined areas | 1 |
| Rural roads poor; limited all-weather roads | 1 |
| Federal highway A4 fair; connects to Maiduguri | 1 |
| Roads poor and conflict-damaged; largely unpaved | 1 |
| Damboa-Maiduguri road partially secured; mined areas | 1 |
| A3 highway partially rehabilitated toward Maiduguri | 1 |
| Roads very poor; largely unpaved and insecure | 1 |
| No maintained roads; completely inaccessible to civilians | 1 |
| Mountain terrain; roads damaged and mined | 1 |
| Rural roads poor but passable; limited paving | 1 |
| Urban roads fair; some federal highways damaged | 1 |
| A3 Trans-Sahel highway passes through; poor condition | 1 |
| No maintained roads; largely inaccessible terrain | 1 |
| Maiduguri-Bama road fair near town; rural roads poor | 1 |
| Maiduguri-Kukawa road insecure and badly degraded | 1 |
| A3 highway passes through; poor condition and insecure | 1 |
| Main federal highways damaged; urban roads fair | 1 |
| Roads inaccessible; mined and conflict-damaged | 1 |
| Roads insecure and degraded; IED threats reported | 1 |
| Maiduguri-Monguno road partially secured but fragile | 1 |
| A3 highway to Cameroon border degraded; militarized | 1 |
| Road connections to Biu and Adamawa; fair condition | 1 |
| Poor rural roads; limited paved sections | 1 |
| Fair; UniCem evacuation road to Odukpani junction | 1 |
| Fair; road links to Calabar; rural roads poor | 1 |
| Very poor; water transport dominant; minimal roads | 1 |
| Poor; rural feeder roads; limited paved sections | 1 |
| Poor rural roads; frequent flooding in rainy season | 1 |
| Poor; rugged forested terrain; limited paved roads | 1 |
| Good paved roads; federal highway network | 1 |
| Good paved roads; port access; some urban congestion | 1 |
| Fair; Ikom-Cameroon highway passes through LGA | 1 |
| Good; on A4 highway Calabar-Cameroon corridor | 1 |
| Fair to poor; winding mountain roads to plateau | 1 |
| Fair; connected to Ikom-Calabar road network | 1 |
| Fair; road access to Obudu Mountain Resort area | 1 |
| Fair to good; on highway from Calabar northward | 1 |
| Fair to good; northern Cross River road hub | 1 |
| Fair; connected to main road network via Obubra | 1 |
| Poor to fair; connected to Ogoja road network | 1 |
| Laterite roads, seasonal flooding issues | 1 |
| Fair paved roads, some laterite sections | 1 |
| Very poor, water transport dependent | 1 |
| Virtually no road network, water transport only | 1 |
| Mix of paved and laterite roads, fair condition | 1 |
| Benin-Warri expressway passes through, good | 1 |
| Benin-Asaba highway, good road infrastructure | 1 |
| Secondary roads, fair to poor condition | 1 |
| Mix of paved and earth roads, fair | 1 |
| Mix of paved and laterite roads, moderate | 1 |
| Poor roads, many areas accessible only by water | 1 |
| Main road to Kwale fair, rural roads poor | 1 |
| Warri-Sapele road good, secondary roads fair | 1 |
| Good roads near Asaba, rural roads fair | 1 |
| Well-paved urban roads, good infrastructure | 1 |
| Very poor, largely water-accessible terrain | 1 |
| Good paved roads, Benin-Warri corridor | 1 |
| Fair to good, benefits from Warri proximity | 1 |
| East-West road fair, urban roads decent | 1 |
| Poor secondary roads, rural areas difficult | 1 |
| Secondary roads fair, some laterite sections | 1 |
| Good paved roads, major expressway junction | 1 |
| Very limited road network, mainly riverine access | 1 |
| Major urban road network, expressway access | 1 |
| No road network, entirely water transport | 1 |
| Federal highway A343 paved, urban roads fair | 1 |
| Afikpo-Abakaliki road partially paved, fair | 1 |
| Mostly unpaved rural roads, poor condition | 1 |
| Largely unpaved, poor rural road network | 1 |
| Poor unpaved roads, limited maintenance | 1 |
| Partially paved roads to Onueke, fair quality | 1 |
| University area roads improved, rural roads poor | 1 |
| Nkalagu road partially paved, rural roads poor | 1 |
| Enugu-Abakaliki highway passes through, fair quality | 1 |
| Largely unpaved, poor and sparse road network | 1 |
| Road to Uburu partially paved, rural areas poor | 1 |
| Border roads poor, limited paved sections | 1 |
| Onicha road partially paved, rural roads poor | 1 |
| Poor rural roads, limited paved federal highways | 1 |
| Paved urban roads, moderate maintenance levels | 1 |
| Semi-paved roads, seasonal deterioration common | 1 |
| Paved trunk roads, unpaved rural feeder roads | 1 |
| Limited paved roads, poor rural road network | 1 |
| Paved main roads, university town infrastructure | 1 |
| Largely unpaved roads, poor rural infrastructure | 1 |
| Poor road network, seasonal flooding disruptions | 1 |
| Paved trunk roads, fair urban road network | 1 |
| Paved urban roads, rapid growth outpacing infrastructure | 1 |
| Federal highways, paved urban road network | 1 |
| Semi-paved trunk road, poor rural feeder roads | 1 |
| Poor rural roads with seasonal deterioration | 1 |
| Poor rural roads, plantation access tracks only | 1 |
| Best in state; paved arterials to Akure and Ilesha | 1 |
| Fair; border LGA with Osun, limited rural network | 1 |
| Poor; farthest LGA at 65km, mostly untarred roads | 1 |
| Fair; 13km from capital but infrastructure dated 1980s | 1 |
| Moderate; tourism roads to Ikogosi improved, rural fair | 1 |
| Poor; predominantly rural with limited paved road coverage | 1 |
| Fair; created 1996, basic road network mostly untarred | 1 |
| Moderate; near Ero Dam, connected to several adjacent LGAs | 1 |
| Moderate; trunk road to Abuja passes through town | 1 |
| Good paved link to Ado-Ekiti at 13km distance | 1 |
| Fair; largest LGA by area, dispersed, untarred interior | 1 |
| Poor; smallest LGA with very limited road infrastructure | 1 |
| Moderate; 17km from capital, fair rural interior roads | 1 |
| Fair; rural roads mostly untarred, historic royal town | 1 |
| Fair; densely settled but remote at 46km from capital | 1 |
| Moderate; FUOYE presence driving road improvements nearby | 1 |
| Fair; accessible via Enugu-PH and Onitsha expressways | 1 |
| Moderate; connected to Enugu city, NYSC camp access | 1 |
| Good; urban road network with ongoing development projects | 1 |
| Excellent; best in state with major paved arterials | 1 |
| Good; urban layouts including Achara, Maryland, Awkunanaw | 1 |
| Poor to moderate; rural roads, tourist site access limited | 1 |
| Moderate; along Enugu-Nsukka Express Road corridor | 1 |
| Moderate; A3 road connection, border trade route active | 1 |
| Poor to moderate; 25km from Nsukka, rural roads | 1 |
| Poor; IFAD constructing bridges and culverts for access | 1 |
| Poor; 79km road construction flagged off in 2024 | 1 |
| Moderate to good; growing Enugu suburb, roads improving | 1 |
| Good; regular transport to Enugu, university infrastructure | 1 |
| Moderate; old Enugu-Onitsha road, border Anambra access | 1 |
| Good; North-Southeast gateway, federal dualization underway | 1 |
| Moderate; old Enugu-Onitsha road, hilly Udi terrain | 1 |
| Poor; remote, Nsukka-Onitsha road through Adani only | 1 |
| Poor; mostly unpaved rural roads, new bridge project 2025 | 1 |
| Excellent; planned highway network with international airport | 1 |
| Good in Kubwa; poor in rural hinterland villages | 1 |
| Moderate; Abuja-Lokoja highway, township roads under repair | 1 |
| Mixed; new housing zones tarred, older areas dirt roads | 1 |
| Poor; dispersed settlements, new road projects flagged 2024 | 1 |
| Federal highway A345 paved; rural roads poor | 1 |
| Mostly unpaved rural roads; poor connectivity | 1 |
| Federal highway A345 passes through; fair condition | 1 |
| Very limited paved roads; mostly earth tracks | 1 |
| A338 highway to Yobe; industrial roads near Ashaka | 1 |
| Federal highways A3 A345; airport; railway station | 1 |
| A345 highway link; rural roads mostly unpaved | 1 |
| Proximity to capital; partly paved township roads | 1 |
| State roads to Gombe; fair condition near town | 1 |
| Mostly unpaved; poor road infrastructure | 1 |
| State roads fair near Deba; poor in rural areas | 1 |
| Rural roads, fair condition, some paved links | 1 |
| Rural roads, mostly unpaved, poor state | 1 |
| Rural roads, fair condition, some erosion | 1 |
| Erosion-damaged roads, poor federal road link | 1 |
| Rural roads, erosion-prone, poor condition | 1 |
| Poorly maintained rural roads | 1 |
| Rural roads, poor to fair condition | 1 |
| Rural roads, largely unpaved, poor state | 1 |
| Mixed roads, some paved near Owerri axis | 1 |
| Mixed roads, airport access road paved | 1 |
| Rural roads, mostly unpaved, erosion risk | 1 |
| Rural roads, poor condition | 1 |
| Major roads degraded, oil company roads fair | 1 |
| Dilapidated roads, largely off national grid | 1 |
| Federal highway access, urban roads fair | 1 |
| Rural roads, poor condition, flood-prone | 1 |
| Major roads paved, commercial center well-linked | 1 |
| Rural roads, poor condition, flood risk | 1 |
| Poor rural roads, some oil company tracks | 1 |
| Mixed roads, Mgbidi junction partially paved | 1 |
| Major federal highways, best paved road network | 1 |
| Semi-urban roads, moderate to good condition | 1 |
| Mixed roads, urban sections good, rural poor | 1 |
| Unpaved rural roads, seasonal flooding risk | 1 |
| Secondary road to Kano, partly paved | 1 |
| Very poor, predominantly unpaved rural tracks | 1 |
| Federal highway A237 to Kano, paved main roads | 1 |
| Secondary roads, proximity to Dutse helps | 1 |
| Federal highway A3, paved main roads, good network | 1 |
| Paved road to Dutse, industrial park road access | 1 |
| Mostly unpaved, limited road infrastructure | 1 |
| Secondary highway to Kano and Hadejia, fair condition | 1 |
| Very poor, unpaved tracks, flood-prone areas | 1 |
| Secondary paved roads, some unpaved feeder roads | 1 |
| Poor, mostly unpaved, border area roads | 1 |
| Paved highway to Kano and Nguru, fair condition | 1 |
| Secondary highway from Kano, partly paved | 1 |
| Secondary paved road, Gaya-Kirikasamma route | 1 |
| Poor, mostly unpaved, flood-prone wetland area | 1 |
| On A2 Trans-Sahara Highway, paved roads | 1 |
| Secondary road, partly paved toward Jahun | 1 |
| Secondary road via Dutse to Bauchi, some paved | 1 |
| Paved road from Gumel, border crossing infrastructure | 1 |
| Poor, unpaved roads, flood-prone areas | 1 |
| Secondary roads, some paved sections to Dutse | 1 |
| Paved road to Kano, fair local road network | 1 |
| Poor, mostly unpaved rural roads | 1 |
| Poor, unpaved, border area feeder roads | 1 |
| Secondary roads, some paved sections | 1 |
| Very poor, unpaved rural tracks | 1 |
| Poor; main highway insecure and degraded | 1 |
| Mixed; Abuja-Kaduna highway under reconstruction | 1 |
| Poor; rural feeder roads inadequate | 1 |
| Good near Rigasa rail station; rural poor | 1 |
| Poor; connected to Zaria-Kano corridor | 1 |
| Fair; railway junction, roads under rehabilitation | 1 |
| Poor; Kachia-Zonkwa road but rural access poor | 1 |
| Good; flyovers, streetlights, paved urban roads | 1 |
| Good; urban road network being upgraded | 1 |
| Fair; on Abuja-Kaduna highway corridor | 1 |
| Very poor; minimal paved roads | 1 |
| Very poor; remote with limited paved roads | 1 |
| Poor; remote rural area, limited connectivity | 1 |
| Fair; along Kaduna-Zaria corridor | 1 |
| Fair; on Kaduna-Jos highway corridor | 1 |
| Good; Zaria urban network, ABU campus roads | 1 |
| Very poor; some asphaltic roads recently reopened | 1 |
| Poor; some access roads recently revitalized | 1 |
| Poor; Madauchi-Kafanchan road links to Jema'a | 1 |
| Good; Abuja-Kano highway, railway junction | 1 |
| Poor; secondary roads, limited access | 1 |
| Improving; major road to Jigawa under construction | 1 |
| Fair; Gwarzo-Bagwai-Bichi road | 1 |
| Poor; secondary roads in interior | 1 |
| Good; on A9 Trans-Sahelian Highway | 1 |
| Fair; on Kano-Rano-Bunkure road | 1 |
| Fair; dense old urban infrastructure | 1 |
| Good; on A2 Trans-Sahara Highway north | 1 |
| Fair; connected to Kano metro, feeder roads | 1 |
| Good; on Kano-Katsina highway, market roads | 1 |
| Poor; extreme south, remote and poorly connected | 1 |
| Good; new flyover, heavily commercial area | 1 |
| Fair; on Kano-Ringim road, transit point | 1 |
| Fair; road construction ongoing | 1 |
| Fair; connected to Kano, near Tiga Dam | 1 |
| Fair; state roads link to Wudil and A237 | 1 |
| Fair; on Kano-Gumel road, feeder roads | 1 |
| Good; urban roads, Bayero University area | 1 |
| Fair; road connects to Bichi on A9 | 1 |
| Good; flyovers, paved urban roads, A2 highway | 1 |
| Fair; state roads, feeder roads under construction | 1 |
| Fair; on Kano-Rano-Kibiya road | 1 |
| Fair; Kiru-Rurum road, secondary roads | 1 |
| Good; Challawa Industrial Area road network | 1 |
| Poor; secondary roads, remote NW Kano | 1 |
| Improving; road and underpass under construction | 1 |
| Poor; secondary roads in NW Kano | 1 |
| Fair; state roads NE of Kano | 1 |
| Good; flyover expansions, Bompai Industrial area | 1 |
| Fair; on Kano-Rano road, new water plant | 1 |
| Fair; road under construction near western metro | 1 |
| Improving; major N13.3bn road project ongoing | 1 |
| Poor; Gwarzo-Shanono road only link | 1 |
| Fair; road construction from Gani to Dagora | 1 |
| Good; on A237 highway to Jigawa | 1 |
| Good; newer urban development area | 1 |
| Fair; feeder roads under construction | 1 |
| Good; on A9 highway toward Katsina | 1 |
| Poor; secondary roads, relatively remote south | 1 |
| Fair; northern metro edge, some feeder roads | 1 |
| Fair; state roads near metro | 1 |
| Good; on A237 highway, bridges Hadejia River | 1 |
| Fair; Bakori-Funtua road, dam access road | 1 |
| Good; connected to Katsina city road network | 1 |
| Poor; degraded roads, insecurity restricts travel | 1 |
| Poor; border roads, limited paved routes | 1 |
| Very poor; roads degraded, insecurity limits travel | 1 |
| Poor; Funtua-Dandume road exists but insecure | 1 |
| Poor; between Bakori and Funtua | 1 |
| Fair; connected to Katsina and Funtua roads | 1 |
| Poor; near Zamfara border, degraded roads | 1 |
| Fair; A126 highway from Kaduna passes through | 1 |
| Fair; A9 to Niger, international border crossing | 1 |
| Fair; road between Katsina and Funtua | 1 |
| Poor; Kaita Road north from Katsina | 1 |
| Poor; Kankara road degraded, federal contract cancelled | 1 |
| Fair; roads connecting to Katsina and Daura | 1 |
| Good; airport, A9 junction, university, paved roads | 1 |
| Poor; on Katsina-Safana-Kankara road | 1 |
| Fair; road to Niger Republic, customs facilities | 1 |
| Fair; road connections to Funtua and Katsina | 1 |
| Fair; one of earliest LGAs, established roads | 1 |
| Fair; on Katsina-Daura road | 1 |
| Very poor; N18.5bn road project just flagged off | 1 |
| Poor; Katsina-Safana road degraded by conflict | 1 |
| Poor; secondary road east from A2 | 1 |
| Fair; A2 highway to Niger Republic at Kongolam | 1 |
| Laterite roads dominate; seasonal accessibility issues | 1 |
| Mostly laterite roads; borders Niger Republic; poor access | 1 |
| Paved road to Birnin Kebbi; fair federal highway link | 1 |
| Secondary laterite roads; links to Sokoto-Kebbi corridor | 1 |
| Some paved roads; vast area with laterite tracks; seasonal flooding | 1 |
| Federal highways A1 and A2; paved trunk roads; airport nearby | 1 |
| Paved road to Kamba-Niger border; secondary laterite roads | 1 |
| Mostly laterite roads; connects to Niger Republic border | 1 |
| Earth-laterite roads; poor seasonal access; hilly terrain | 1 |
| Paved road to Birnin Kebbi; secondary laterite roads | 1 |
| Secondary laterite roads; close to Birnin Kebbi | 1 |
| A1 federal highway passes through Koko; paved trunk road | 1 |
| Mostly laterite and earth roads; poor rainy season access | 1 |
| Mostly laterite roads; riverine terrain complicates access | 1 |
| Laterite-earth roads; hilly terrain; seasonal access issues | 1 |
| On Birnin Kebbi-Yauri road; partially paved; laterite secondary | 1 |
| Secondary laterite roads; moderate connectivity | 1 |
| Laterite-earth roads; hilly terrain; Zuru-Mahuta road link | 1 |
| Zuru-Mahuta road; Rijau-Zuru to Niger State; partially paved | 1 |
| State roads fair; links to Okene on A2 highway | 1 |
| Ajaokuta-Itobe Bridge over Niger; federal road links; paved | 1 |
| A233 highway through town; links to Benue State | 1 |
| Poor rural roads; recurrent flood damage; limited paved roads | 1 |
| State roads; large area with laterite roads; links to Anyigba | 1 |
| Very poor; roads destroyed by annual floods; boat transport only | 1 |
| State roads to Dekina-Ankpa; riverfront port; some paved | 1 |
| Mostly laterite rural roads; flood-affected areas | 1 |
| Links to Kabba; state roads; paved and laterite mix | 1 |
| A123 highway Ilorin-Kabba-Okene; paved federal road; fair | 1 |
| A2 highway passes through; links Lokoja-Abuja; flood damage | 1 |
| A2 highway Abuja-Lokoja; A233 junction; paved dual carriageway | 1 |
| Rural laterite roads; links to Kabba area; smallest LGA | 1 |
| State roads link to Anyigba and Idah; some laterite roads | 1 |
| Links to Okene on A2 corridor; small LGA; some paved | 1 |
| Links to Okene-Ajaokuta; federal road; paved near mine sites | 1 |
| A2 highway passes through; A123 junction; paved federal roads | 1 |
| Mostly laterite roads; borders Benue-Enugu; poor infrastructure | 1 |
| Mostly laterite roads; near Benue River; some flood damage | 1 |
| State roads; links to Kwara; paved and laterite mix | 1 |
| Links to Kwara border; mostly laterite rural roads | 1 |
| Fair near Ilorin; rural roads deteriorate seasonally | 1 |
| Very poor; roads impassable in rainy season; extremely remote | 1 |
| Fair to Lafiagi town; poor in interior riverine areas | 1 |
| Poor to fair; secondary roads in variable condition | 1 |
| Fair on main roads; interior roads poor seasonally | 1 |
| Good within urban areas; fair at peri-urban fringe | 1 |
| Good; major roads well-maintained; university area roads good | 1 |
| Good; well-developed road network; A1-A5-A6 highway junction | 1 |
| Fair to good on Ilorin-Omu-Aran road; interior variable | 1 |
| Poor; mostly unpaved secondary roads | 1 |
| Very poor; 5-hour drive from Ilorin; impassable in rain | 1 |
| Good on A1 highway Lagos-North; poor secondary; Jebba bridge | 1 |
| Good; on Lagos railway line; junction of multiple roads | 1 |
| Poor; secondary roads; seasonally impassable | 1 |
| Fair; main roads to Offa reasonable; interior roads poor | 1 |
| Poor; 164km from Ilorin; no bridge; ferry only over Niger | 1 |
| Poor to fair, congested narrow roads, drainage issues | 1 |
| Very poor, waterlogged, narrow, largely unpaved interior | 1 |
| Fair, major roads adequate, internal roads poor | 1 |
| Fair to good, Festac planned estate, some flooding | 1 |
| Very poor, extreme congestion from port trucks, gridlock | 1 |
| Poor, Lagos-Badagry expressway under expansion | 1 |
| Fair on main road, poor internal rural roads | 1 |
| Good in VI and Ikoyi, deteriorating toward Ajah | 1 |
| Poor, limited road network, development outpacing infra | 1 |
| Fair, major roads adequate, internal roads mixed | 1 |
| Good, well-maintained arterial roads, GRA areas excellent | 1 |
| Fair on main corridor, poor in rural interiors | 1 |
| Fair, major roads congested, Mile 12 area chaotic | 1 |
| Fair, very congested, narrow historic streets, bridges | 1 |
| Fair to good, major roads functional, some congestion | 1 |
| Poor, narrow, congested, poorly drained roads | 1 |
| Poor to fair, Badagry expressway up, internal roads weak | 1 |
| Fair, Oshodi interchange improved, Isolo industrial fair | 1 |
| Poor to fair, congested narrow streets, Bariga slums | 1 |
| Good, well-maintained major roads, National Stadium area | 1 |
| On A234 highway, fair in town, poor rural roads | 1 |
| Secondary roads, limited, remote from major highways | 1 |
| Secondary roads, 32km from Lafia, moderate condition | 1 |
| Expressway to Abuja, urban roads congested, poor planning | 1 |
| Poor rural roads, limited connectivity to highways | 1 |
| On A234 Abuja-Keffi highway, flyover under construction | 1 |
| On Keffi-Akwanga road, fair near highway, poor interior | 1 |
| On A3 highway, railway, cargo airport, best in state | 1 |
| Local roads to Keffi, Loko-Oweto Bridge completed 2022 | 1 |
| Between Akwanga and Lafia, fair on main road | 1 |
| South of Lafia, secondary roads, fair to capital | 1 |
| Road from Abaji FCT via Toto, poor rural roads | 1 |
| On A3 Lafia-Jos road, fair on highway, poor interior | 1 |
| Fair, on Minna-Bida road A124, secondary roads poor | 1 |
| Very poor, remote, unpaved roads, near Benin border | 1 |
| Good, on A124 highway, Federal Polytechnic access road | 1 |
| Fair, A1 highway passes through, internal roads poor | 1 |
| Good, urban roads, FUT Minna Bosso campus well-connected | 1 |
| Good, state capital, paved roads, rail line through Minna | 1 |
| Poor, rural, limited all-season roads, riverine terrain | 1 |
| Fair, proximity to Bida gives some road access | 1 |
| Fair, southern Niger, proximity to FCT improves access | 1 |
| Poor, rural riverine area, limited paved roads | 1 |
| Good, on A1 Trans-Saharan highway, major junction town | 1 |
| Fair, on Minna-Abuja road corridor, improving access | 1 |
| Poor, rural, riverine, limited paved road network | 1 |
| Very poor, remote, near Kebbi border, unpaved tracks | 1 |
| Very poor, remote western Niger, unpaved, insecurity | 1 |
| Poor, rural, limited road infrastructure, insecurity | 1 |
| Good, on A1 highway, Jebba bridge crosses Niger River | 1 |
| Very poor, insecurity blocks road maintenance and travel | 1 |
| Fair, road from Minna to Paiko, secondary routes unpaved | 1 |
| Poor, insecurity limits road use, 78 of 127 schools closed | 1 |
| Very poor, remote northwestern Niger, limited paved roads | 1 |
| Poor, dam access road fair, rural areas very poor | 1 |
| Good, close to Abuja, major road links, rapidly urbanizing | 1 |
| Good, between Suleja and Abuja, benefits from FCT roads | 1 |
| Fair, secondary road from Minna, mostly unpaved tracks | 1 |
| Good; Lagos-Abeokuta Expressway, paved state roads | 1 |
| Good; paved roads, expressway hub, well-maintained | 1 |
| Good; borders Lagos, Sango-Ota-Idiroko highway | 1 |
| Moderate; on Lagos-Abeokuta Expressway at km 64 | 1 |
| Moderate; Lagos-Abeokuta Expressway, rapid growth strain | 1 |
| Poor; expressway at Ogbere but interior roads lacking | 1 |
| Moderate; state roads to Ijebu-Ode and Sagamu | 1 |
| Poor; secondary roads, 20 km from Ijebu-Ode | 1 |
| Good; on Sagamu-Benin Expressway, paved urban roads | 1 |
| Good; near Lagos-Ibadan Expressway, Gateway airport | 1 |
| Very poor; remote border area, unpaved internal roads | 1 |
| Moderate; Idiroko border crossing road, secondary roads | 1 |
| Mixed; Lagos-Ibadan Expressway south, poor roads north | 1 |
| Moderate; on Abeokuta-Ibadan road, 15 km from capital | 1 |
| Moderate; roads to Ijebu-Ode, secondary road network | 1 |
| Very poor; many communities accessible only by boat | 1 |
| Moderate; state roads to Sagamu, partially paved | 1 |
| Excellent; junction Lagos-Ibadan and Sagamu-Benin roads | 1 |
| Poor; Abeokuta-Ilaro road, poor internal rural roads | 1 |
| Moderate; on Abeokuta-Ilaro road, partially paved | 1 |
| Moderate; road from Owo, hilly terrain, 100 km Akure | 1 |
| Poor; hilly terrain, secondary roads from Ikare | 1 |
| Moderate; Akoko road network, Ajasin University area | 1 |
| Moderate; roads from Owo, hilly terrain | 1 |
| Good; adjacent to Akure on Akure-Owo road corridor | 1 |
| Good; major highway junction, well-paved urban roads | 1 |
| Very poor; riverine terrain, access primarily by boat | 1 |
| Moderate; 20 km from Akure, Akure-Ondo road nearby | 1 |
| Good; on Akure-Ilesa expressway, nodal location | 1 |
| Very poor; mostly boat access, no paved interior roads | 1 |
| Moderate; connected to Ondo-Akure road corridor | 1 |
| Poor; Ore-Irele road in historically bad condition | 1 |
| Good; on Lagos-Benin expressway, major national highway | 1 |
| Moderate; on Ore-Okitipupa road, partially paved | 1 |
| Poor; secondary roads, adjacent to Ondo West | 1 |
| Good; on Akure-Ondo-Ore road, well-connected corridor | 1 |
| Moderate; on Benin-Owo Express Road, rural interior | 1 |
| Good; on Akure-Owo-Benin highway, well-connected | 1 |
| Moderate; on Gbongan-Ibadan road, paved main corridor | 1 |
| Poor; secondary roads west of Osogbo | 1 |
| Poor; mining roads in bad condition, 60 km from Osogbo | 1 |
| Moderate; Ife-Ilesa express road passes through Osu | 1 |
| Poor; secondary roads in northern Osun zone | 1 |
| Good; on Osogbo-Ikirun road, paved main road | 1 |
| Good; on Osogbo-Iwo road, railway access at Ede | 1 |
| Moderate; connected via Ede road network | 1 |
| Good; paved roads to Osogbo, just 12 km away | 1 |
| Moderate; Ede-Ejigbo road toward Ogbomosho | 1 |
| Good; on A122 Osogbo-Ife road, paved urban roads | 1 |
| Good; contiguous with Ife Central, major paved roads | 1 |
| Moderate; on Ile-Ife to Osogbo road corridor | 1 |
| Poor; secondary roads toward Ondo State border | 1 |
| Very poor; bad roads, most remote LGA in Osun | 1 |
| Good; on Osogbo-Ikirun-Ilorin major highway | 1 |
| Moderate; on Osogbo-Ikirun-Ila road, being dualised | 1 |
| Good; major junction linking Ife, Osogbo, and Akure | 1 |
| Good; part of Ilesa city road network | 1 |
| Good; very close to Osogbo, on road toward Ikirun | 1 |
| Moderate; on Gbongan-Ibadan road, paved | 1 |
| Moderate; secondary roads southeast from A122 highway | 1 |
| Moderate; Osogbo-Iwo road under reconstruction, railway | 1 |
| Moderate; road construction recent, via Ilesa access | 1 |
| Moderate; northern Osun roads toward Ikirun, Osogbo | 1 |
| Poor; secondary roads in western Osun, isolated area | 1 |
| Good; contiguous with Osogbo, shared road network | 1 |
| Moderate; via Ilesa, road to waterfalls undeveloped | 1 |
| Moderate; central-northern Osun road connections | 1 |
| Good; road hub all corridors, railway on Western Line | 1 |
| Oyo-Ibadan highway corridor fair; side roads poor | 1 |
| Moniya-Iseyin road rehabilitated; rural roads poor | 1 |
| A1 highway fair; Oyo-Iseyin road improved | 1 |
| Poor; rural roads in deteriorated condition | 1 |
| Major roads fair near Ibadan; rural areas poor | 1 |
| Major roads fair; some inner roads poor | 1 |
| Major arteries fair; inner roads often congested | 1 |
| Good; includes GRA and government reservation | 1 |
| Old core city; narrow degraded roads; some repairs | 1 |
| Commercial roads fair; Ring Road well-maintained | 1 |
| Town roads fair; Igbo-Ora to Ibadan partial | 1 |
| Ido-Eruwa road under construction; mixed quality | 1 |
| Poor; mostly unpaved roads; security concerns | 1 |
| Ido-Eruwa road under construction; poor internally | 1 |
| Poor; Kishi-Igboho roads deteriorated | 1 |
| Oyo-Iseyin road rehabilitated; town roads fair | 1 |
| Very poor; remote area with mostly unpaved roads | 1 |
| Very poor; hilly terrain; deplorable conditions | 1 |
| Okeho-Iganna road poor; some town roads fair | 1 |
| Improving along major corridors; rural roads poor | 1 |
| Main highways fair; intra-city roads moderate | 1 |
| Main Ogbomosho roads fair; rural roads poor | 1 |
| Mostly poor rural roads; limited paved surfaces | 1 |
| Igbeti-Ilorin and Igbeti-Igboho roads poor | 1 |
| Ibadan-Ijebu road fair; estate roads mixed | 1 |
| Akanran road recently reconstructed; rural poor | 1 |
| Saki-Igboho road rehabilitated; others poor | 1 |
| Predominantly unpaved rural roads; poor quality | 1 |
| Oyo-Awe road fair; rural roads mostly unpaved | 1 |
| A1 Lagos-North highway; main roads fair | 1 |
| Poor; mostly unpaved rural roads | 1 |
| Township fair; Saki-Igboho road rehabilitated | 1 |
| Mostly poor rural roads; limited paving | 1 |
| Jos-Shendam highway traverses; rural roads poor | 1 |
| Fair to poor; some paved roads, many earth roads | 1 |
| Fair; connected to Jos via Barkin Ladi road | 1 |
| Fair; Jos proximity provides decent road access | 1 |
| Good; major highways, paved roads, airport | 1 |
| Good; Bukuru expressway and paved urban roads | 1 |
| Poor; remote northeastern area; limited paving | 1 |
| Fair to poor; near Barkin Ladi-Pankshin road | 1 |
| Fair; paved roads to Jos, Shendam, and Wase | 1 |
| Poor; limited paved roads in remote area | 1 |
| Fair; connected to Jos via major road | 1 |
| Poor; very remote southern LGA; earth roads | 1 |
| Fair; Pankshin-Jos road; Catholic diocese seat | 1 |
| Poor to fair; limited paved road network | 1 |
| Fair; military checkpoints; rural tracks common | 1 |
| Fair; on Jos-Lafia road; historic route | 1 |
| Poor; 216km from Jos; remote southeastern area | 1 |
| Poor; largely unpaved; seasonal flooding disrupts | 1 |
| Moderate; East-West Road traverses; internal poor | 1 |
| Poor; mostly unpaved roads; frequent flooding | 1 |
| Very poor; mostly riverine; waterway dominant | 1 |
| Very poor; almost entirely waterway access | 1 |
| Poor; riverine terrain; Buguma road-accessible | 1 |
| Limited; island access by boat; town roads fair | 1 |
| Poor; riverine access dominant; internal degraded | 1 |
| Moderate to good near refinery; rural areas poor | 1 |
| Fair; road link to PH exists; internal unpaved | 1 |
| Fair; some paved roads; border link to Imo | 1 |
| Poor; rural roads unpaved; oil-damaged surfaces | 1 |
| Fair to moderate; Airport Road; internal mixed | 1 |
| Poor to fair; Bori accessible; internal poor | 1 |
| Fair to good; paved dual carriageways; flooding | 1 |
| Fair in Omoku town; rural roads very poor | 1 |
| Poor; mixed road and waterway access | 1 |
| Fair; island connected by bridge to PH | 1 |
| Poor; largely rural unpaved; seasonal flooding | 1 |
| Very poor; primarily waterway access; isolated | 1 |
| Fair; road connectivity to PH; Abia border | 1 |
| Good; paved dual carriageways; soot pollution | 1 |
| Poor; rural unpaved roads; oil-damaged surfaces | 1 |
| Unpaved rural roads, limited federal highway access | 1 |
| State road from Sokoto, partly paved | 1 |
| Paved road to Sokoto, industrial road access | 1 |
| Mostly unpaved rural roads, limited access | 1 |
| State road partly paved to Goronyo Dam | 1 |
| Very poor unpaved roads, remote border area | 1 |
| On Sokoto-Illela highway, partly paved | 1 |
| Federal highway to Niger Republic, paved | 1 |
| Unpaved roads, banditry disrupts movement | 1 |
| Poor roads, remote from state capital | 1 |
| On Sokoto-Illela highway, paved road | 1 |
| Poor unpaved roads, insecurity limits movement | 1 |
| Poor roads, frequent bandit attacks on routes | 1 |
| Unpaved rural roads, limited connectivity | 1 |
| Unpaved roads, limited state road access | 1 |
| Federal highways, mostly paved urban roads | 1 |
| Paved urban roads, university campus access | 1 |
| State road partly paved, Sokoto River bridge | 1 |
| Poor roads, border insecurity limits access | 1 |
| Unpaved roads, limited state road connection | 1 |
| Paved roads linking Sokoto city, university area | 1 |
| State road partly paved from Sokoto | 1 |
| State road partly paved, near Sokoto corridor | 1 |
| Mostly unpaved seasonal roads near Jalingo corridor | 1 |
| Unpaved roads; not connected to national grid | 1 |
| Poor rural roads, conflict-disrupted maintenance | 1 |
| Very poor, mostly unpaved tracks, remote terrain | 1 |
| A4 highway corridor; rural roads mostly poor | 1 |
| Road access from Wukari; some paved sections | 1 |
| Federal highway hub, mostly paved roads | 1 |
| Poor road network, seasonal flooding affects access | 1 |
| Very poor roads, limited access in rainy season | 1 |
| Rural roads; some access via Jalingo-north route | 1 |
| Very remote mountain roads, two-day drive from Abuja | 1 |
| Road to Wukari and Benue State; partial paving | 1 |
| Poor roads, Cameroon border, difficult terrain | 1 |
| Federal highway A4 corridor; some paved roads | 1 |
| Mostly unpaved rural roads, limited connectivity | 1 |
| Road link to Jalingo and Adamawa; partially paved | 1 |
| Nguru-Gashua road partly paved, fair condition | 1 |
| Dapchi-Damaturu road largely unpaved, insecure | 1 |
| Federal highway A3 hub, partly paved, flyover built | 1 |
| A338 secondary road, partly unpaved laterite | 1 |
| Trunk roads largely unpaved, long rural distances | 1 |
| Nguru-Geidam road conflict-damaged, insecure stretches | 1 |
| Damaturu-Buni Yadi road conflict-damaged, partly restored | 1 |
| Poor rural roads; first grid connection achieved 2025 | 1 |
| Jakusko-Potiskum road partly paved, fair condition | 1 |
| Unpaved rural roads, limited connectivity to Nguru | 1 |
| Nguru-Machina road partly paved, border area | 1 |
| On Gashua road, secondary roads partly paved | 1 |
| Railway terminus from Kano, Nguru-Gashua road paved | 1 |
| A3 highway hub, paved roads to Damaturu and Kano | 1 |
| On Gashua road, secondary roads largely unpaved | 1 |
| Poor unpaved roads, severe conflict damage, insecure | 1 |
| Poor unpaved roads, Niger Republic border area | 1 |
| Secondary roads, severely degraded by conflict | 1 |
| Secondary roads, mostly unpaved, poor condition | 1 |
| Secondary roads, poor condition, insecurity disruptions | 1 |
| Unpaved roads, conflict-damaged, highly insecure | 1 |
| Gusau-Sokoto highway passes through; secondary roads poor | 1 |
| Road to Anka and Sokoto state, partially paved | 1 |
| Federal highway A126, mostly paved; railway to Zaria | 1 |
| Railway terminus from Zaria; secondary highway paved | 1 |
| Secondary roads, mostly unpaved, highly insecure | 1 |
| Mostly unpaved, frequently attacked by bandits | 1 |
| Kaura Namoda-Shinkafi road partially paved, insecure | 1 |
| Secondary highway connecting Gusau to Sokoto | 1 |
| A126 Katsina-Gusau highway passes through town | 1 |
| Border road to Niger, mostly unpaved, highly insecure | 1 |


### `Market Access`

Unique values: **762** | Nulls: **0**

| Value | Count |
|-------|-------|
| Very limited, isolated from major trade routes | 3 |
| Moderate; proximity to Eket commercial center | 2 |
| Weekly markets, limited road access | 2 |
| Very limited, remote periodic markets only | 2 |
| Limited, some cross-border trade with Niger | 2 |
| Severely disrupted by armed banditry | 2 |
| Limited but improving with road investment | 2 |
| Limited; interior rural LGA | 2 |
| Good; proximity to Kano city markets | 2 |
| Severely disrupted; frontline banditry zone | 2 |
| Limited; dependent on Ogbomosho for trade | 2 |
| Strong; direct access to Aba commercial district | 1 |
| Excellent; Ariaria International Market hub | 1 |
| Limited; remote border area, periodic markets | 1 |
| Moderate; periodic local markets, some commerce | 1 |
| Moderate; university presence, Umuahia market access | 1 |
| Limited; periodic rural markets, palm oil trade | 1 |
| Limited; periodic rural markets, palm oil sales | 1 |
| Limited; remote hilly area, periodic markets only | 1 |
| Limited; proximity to Aba aids periodic trade | 1 |
| Moderate; periodic markets, local crafts trade | 1 |
| Strong; part of greater Aba industrial zone | 1 |
| Limited; small rural markets, some Aba trade links | 1 |
| Limited; riverine access, periodic local markets | 1 |
| Limited; remote oil area, periodic rural markets | 1 |
| Limited; remote hilly area, periodic local markets | 1 |
| Good; state capital with active daily markets | 1 |
| Moderate; spillover from Umuahia capital markets | 1 |
| Limited; weekly markets, river transport access | 1 |
| Moderate; proximity to Yola improves access | 1 |
| Moderate; weekly markets, agricultural produce trade | 1 |
| Very limited; isolated from major trade routes | 1 |
| Disrupted by insecurity, recovering weekly markets | 1 |
| Limited; small weekly markets along Benue | 1 |
| Disrupted by insecurity, weekly markets recovering | 1 |
| Moderate; local weekly markets, farm produce | 1 |
| Limited; weekly markets, some river transport | 1 |
| Collapsed; markets destroyed, insecurity limits trade | 1 |
| Some cross-border trade with Cameroon | 1 |
| Moderate; weekly markets for agricultural produce | 1 |
| Severely disrupted by conflict, limited activity | 1 |
| Major cattle market, cross-border trade hub | 1 |
| Benefits from proximity to Mubi commercial center | 1 |
| Moderate; Numan market serves surrounding LGAs | 1 |
| Limited; weekly markets, some Benue trade | 1 |
| Moderate; along main transport corridor | 1 |
| Extremely limited; isolated from trade networks | 1 |
| Strong; main commercial center, diverse markets | 1 |
| Good; benefits from proximity to Yola North | 1 |
| Good; major market serves surrounding LGAs | 1 |
| Very poor; isolated, dependent on water transport | 1 |
| Good; active commercial hub with daily markets | 1 |
| Limited; periodic markets, poor road linkages | 1 |
| Poor; limited market infrastructure and access | 1 |
| Moderate; proximity to Uyo improves access | 1 |
| Very poor; isolated fishing settlements | 1 |
| Good; close to Uyo markets and commerce | 1 |
| Moderate; benefits from Uyo proximity | 1 |
| Poor; periodic markets, water transport needed | 1 |
| Moderate; periodic markets serve farm communities | 1 |
| Moderate; historical port, some commercial activity | 1 |
| Excellent; major trade hub, raffia city markets | 1 |
| Very poor; isolated, minimal market infrastructure | 1 |
| Moderate; Itam junction market is significant | 1 |
| Poor; informal cross-border trade with Cameroon | 1 |
| Limited; small periodic markets, poor linkages | 1 |
| Poor; limited market access and infrastructure | 1 |
| Moderate; benefits from proximity to Uyo | 1 |
| Moderate; periodic rural markets operational | 1 |
| Very poor; far from major market centers | 1 |
| Poor; small fishing markets, limited access | 1 |
| Good; active port, cross-border trade with Cameroon | 1 |
| Limited; periodic markets, some cross-river trade | 1 |
| Poor; depends on Oron market for trade access | 1 |
| Very poor; isolated from major trade routes | 1 |
| Moderate; proximity to Uyo and Oron markets | 1 |
| Very poor; minimal market infrastructure | 1 |
| Excellent; main commercial center of the state | 1 |
| 45 km to Awka; Ekwulobia is regional hub | 1 |
| 30 km to Onitsha; cargo airport at Umueri | 1 |
| 60+ km to Awka; flooding disrupts access regularly | 1 |
| 15 km to Awka; well-connected to Onitsha corridor | 1 |
| Adjacent to Awka; 35 km to Onitsha | 1 |
| State capital; 50 km to Onitsha; all major banks | 1 |
| 70+ km to Awka; limited access due to poor roads | 1 |
| 25 km to Awka; 25 km to Onitsha; excellent access | 1 |
| 15 km to Nnewi; 25 km to Onitsha | 1 |
| Adjacent to Onitsha; major relocated markets at Obosi | 1 |
| 30 km to Onitsha; 15 km to Nnewi | 1 |
| 35 km to Onitsha; borders Imo and Delta states | 1 |
| 15 km to Awka; 30 km to Onitsha | 1 |
| 20 km to Onitsha; exports nationally and internationally | 1 |
| 20 km to Nnewi; 40 km to Onitsha | 1 |
| Adjacent to Onitsha but internal roads impassable | 1 |
| West Africa's largest market; $3-5 billion annual trade | 1 |
| Part of Onitsha commercial hub; multiple major markets | 1 |
| 55 km to Awka; depends on Ekwulobia market center | 1 |
| 60 km to Awka; Ekwulobia nearest significant market | 1 |
| 15 km to Onitsha; 30 km to Awka | 1 |
| 60 km to Bauchi on trunk road; interior very remote | 1 |
| State capital; major road, rail, air hub for NE | 1 |
| 107 km to Bauchi; access through Tafawa Balewa | 1 |
| 200 km to Bauchi; very remote; depends on Azare | 1 |
| 100 km to Bauchi; on major route; weekly markets | 1 |
| 50 km to Bauchi; rice and maize supply nearby states | 1 |
| Most remote LGA; 295 km to Bauchi; minimal trade | 1 |
| 50 km to Bauchi; Kafin Madaki market serves district | 1 |
| 200 km to Bauchi; some highway corridor trade | 1 |
| 256 km to Bauchi; depends on Azare for commerce | 1 |
| 230 km to Bauchi; emirate town with established markets | 1 |
| Azare is second-largest town; major commercial crossroads | 1 |
| 84 km to Bauchi; limited; depends on Alkaleri corridor | 1 |
| 150 km to Bauchi; on highway; emirate town markets | 1 |
| 125 km to Bauchi; emirate town; large weekly markets | 1 |
| 205 km to Bauchi; highway corridor provides some access | 1 |
| 88 km to Bauchi; conflict disrupts market activities | 1 |
| 90 km to Bauchi; dispersed across Nigeria's largest LGA | 1 |
| 115 km to Bauchi; depends on Ningi for market access | 1 |
| 240 km to Bauchi; some access through Azare market | 1 |
| Very limited; isolated island; boat-dependent supply chain | 1 |
| Very limited; remote riverine; local water-based trade only | 1 |
| Close to Yenagoa; moderate agricultural market access | 1 |
| 40 min drive to Yenagoa; transit point for Brass | 1 |
| Moderate; road link to Yenagoa; Federal University Otuoke | 1 |
| Road-connected to Yenagoa; University of Africa nearby | 1 |
| Extremely limited; boat to Yenagoa; road by 2025-26 | 1 |
| State capital; Swali Market; banking and services hub | 1 |
| Periodic rural markets; limited commercial infrastructure | 1 |
| Severely disrupted by herder-farmer conflict | 1 |
| Periodic markets; limited trade routes to Otukpo | 1 |
| Limited markets; trade linked to Gboko corridor | 1 |
| Major commercial hub; second largest city; active markets | 1 |
| Markets disrupted by recurrent herder-farmer violence | 1 |
| Aliade market active; trade links to Makurdi | 1 |
| Markets disrupted; Naka-Adoka road reported dangerous | 1 |
| Active market town; trade hub along Katsina-Ala River | 1 |
| Periodic rural markets; limited commercial activity | 1 |
| Adikpo market active; trade links to Cross River | 1 |
| Markets severely disrupted by herder-farmer violence | 1 |
| State capital; major markets, banks, and trade hub | 1 |
| Small periodic markets; limited trade infrastructure | 1 |
| Otukpa market active; rail link to wider region | 1 |
| Minimal market infrastructure; limited trade access | 1 |
| Local periodic markets; Igede ethnic capital | 1 |
| Okpoga market serves local trade; linked to Otukpo | 1 |
| Major southern commercial hub; active Otukpo market | 1 |
| Wannune market active; limited commercial infrastructure | 1 |
| Zaki-Biam yam market; regional agricultural trade center | 1 |
| Lessel market; trade linked to Gboko corridor | 1 |
| Vandeikya market active; links to Cross River border | 1 |
| No functional markets; area under NSAG control | 1 |
| Local weekly markets functional; trade links via Biu | 1 |
| Garrison town market only; supply chains severely disrupted | 1 |
| Local markets functional; linked to Biu trade network | 1 |
| Major southern Borno trade hub; weekly market active | 1 |
| Limited market access; insecurity disrupts trade routes | 1 |
| Garrison town market only; Sambisa forest border risk | 1 |
| Humanitarian hub market; cross-border trade limited | 1 |
| Markets severely disrupted; limited commercial activity | 1 |
| No functional markets; zero civilian governance decade-plus | 1 |
| Garrison town market; Cameroon cross-border trade limited | 1 |
| Local markets functional; connected via Biu network | 1 |
| Integrated with Maiduguri markets; IDP economy active | 1 |
| Benisheikh market partially active; insecurity limits trade | 1 |
| Rann garrison market only; humanitarian supply dependent | 1 |
| Weekly markets near Maiduguri; disrupted farther out | 1 |
| Markets non-functional; ISWAP actively threatening residents | 1 |
| Local markets active; linked to Biu trade network | 1 |
| Markets limited; conflict disrupts supply routes | 1 |
| Limited market activity; humanitarian supply dependent | 1 |
| Major regional commercial hub; Monday Market active | 1 |
| No functional civilian markets; NSAG-controlled areas | 1 |
| Damasak garrison market; very limited trade activity | 1 |
| Garrison town market active; humanitarian economy dominant | 1 |
| Gamboru market formerly major; now severely limited | 1 |
| Gajiram market limited; conflict restricts trade severely | 1 |
| Local markets functional; some regional trade activity | 1 |
| Limited; depends on Ikom for major trade | 1 |
| Moderate; cement industry boosts local commerce | 1 |
| Moderate; proximity to Calabar aids market access | 1 |
| Very limited; remote island; waterway dependent | 1 |
| Limited; depends on nearby Ogoja market hub | 1 |
| Limited; poor road access constrains market linkages | 1 |
| Limited; cocoa traded via Ikom; Cameroon border trade | 1 |
| State capital; excellent market access and commerce | 1 |
| Good; Watt Market; Calabar port; commercial centers | 1 |
| Moderate; Cameroon border trade; near cocoa hub | 1 |
| Major commercial hub; cocoa trade center for region | 1 |
| Limited; seasonal tourism boost from Obudu Resort nearby | 1 |
| Moderate; local trading center for surrounding LGAs | 1 |
| Moderate; tourism economy around Obudu Mountain Resort | 1 |
| Good; benefits from Calabar proximity and highway | 1 |
| Major commercial hub for northern Cross River LGAs | 1 |
| Moderate; Ugep is local trading center; Leboku festival | 1 |
| Limited; depends on Ogoja as nearest commercial hub | 1 |
| 50km to Asaba, fair road connection | 1 |
| 30km to Asaba, moderate market access | 1 |
| Remote, limited road access, boat transport primary | 1 |
| Very remote, accessible mainly by boat | 1 |
| Near Benin-Warri highway, moderate market access | 1 |
| On major highway, good market connectivity | 1 |
| On major highway, strong market linkage | 1 |
| 20km to Agbor, moderate market access | 1 |
| 80km to Warri, moderate road access | 1 |
| 85km to Warri, fair road connection | 1 |
| Remote, 120km to Asaba, poor road access | 1 |
| 60km to Asaba, fair road connection | 1 |
| Near Sapele and Warri, good connectivity | 1 |
| 15km to Asaba, good road connection | 1 |
| State capital, major hub, expressway access | 1 |
| Remote riverine, very limited road market access | 1 |
| Major town, road and river transport access | 1 |
| Adjacent to Warri, strong market access | 1 |
| Ughelli town is regional trade center | 1 |
| 30km to Ughelli, limited rural market access | 1 |
| 45km to Asaba, moderate road access | 1 |
| Part of Warri metropolis, excellent market access | 1 |
| Remote, Koko port provides some market access | 1 |
| Primary commercial hub, excellent market access | 1 |
| Very remote coastal, accessible only by boat | 1 |
| State capital, largest commercial hub in Ebonyi | 1 |
| Second largest town, regional trade center | 1 |
| Limited market access, remote rural communities | 1 |
| Limited, reliance on local weekly markets | 1 |
| Periodic rural markets, limited trade links | 1 |
| Onueke market serves as senatorial zone hub | 1 |
| Growing market near AE-FUNAI Federal University | 1 |
| Nkalagu has moderate industrial and trade links | 1 |
| Mining hub, Ishiagu has active commercial activity | 1 |
| Iboko weekly market, limited trade infrastructure | 1 |
| Uburu and Okposi markets, moderate commercial activity | 1 |
| Ezzamgbo market, some cross-border trade with Benue | 1 |
| Onicha town market, moderate local trade activity | 1 |
| Limited market access, remote northern Edo location | 1 |
| Strong urban commercial activity, Benin City metro | 1 |
| Moderate market access, Irrua specialist hospital hub | 1 |
| Active regional trading center for Esan communities | 1 |
| Moderate market access, local agricultural markets | 1 |
| Good market access, AAU university-driven local economy | 1 |
| Limited market access, small local markets only | 1 |
| Limited market access, riverine community constraints | 1 |
| Major commercial hub, active trade center in Edo North | 1 |
| Poor market access, small rural markets only | 1 |
| Strong commercial access, Benin City expansion area | 1 |
| State capital, major commercial and administrative hub | 1 |
| Limited market access despite oil resources present | 1 |
| Moderate market access, Okada junction trading point | 1 |
| Limited market access, remote forested areas | 1 |
| Limited market access, small local agricultural markets | 1 |
| Limited market access, local agricultural trading | 1 |
| Limited market access, plantation-dependent economy | 1 |
| Excellent; commercial hub with multiple major markets | 1 |
| Limited; small border town with Oka market active | 1 |
| Poor; most remote LGA with limited market connectivity | 1 |
| Moderate; Ojulawe market draws regional traders regularly | 1 |
| Moderate; tourism traffic and multiple commercial centers | 1 |
| Limited; rural character constrains market connectivity | 1 |
| Limited to moderate; local markets serve dispersed communities | 1 |
| Moderate; active markets with decent road connectivity | 1 |
| Moderate; cottage industries and growing commercial activity | 1 |
| Good; close to state capital, active trade routes | 1 |
| Limited to moderate; agro-processing investment hubs emerging | 1 |
| Poor; smallest population, minimal commercial infrastructure | 1 |
| Moderate to good; timber industry drives commercial activity | 1 |
| Limited to moderate; local periodic markets present | 1 |
| Limited to moderate; dense population supports local markets | 1 |
| Moderate to good; university boosts commercial activity | 1 |
| Moderate; vibrant local markets at Nnenwe, Mpu, Okpanku | 1 |
| Moderate; divisional market centers serve the population | 1 |
| Excellent; metro commercial hub with multiple centers | 1 |
| Excellent; Ogbete Main Market, banking, commercial districts | 1 |
| Good; full Enugu metro access to all major markets | 1 |
| Limited; local markets, Ezeagu Tourist Complex draws visitors | 1 |
| Moderate; central location with multiple marketplaces | 1 |
| Good; vibrant Eke Ozzi market, strong inter-state trade | 1 |
| Moderate; rotational market system on Igbo calendar | 1 |
| Limited; border LGA with seasonal road access challenges | 1 |
| Limited; IFAD-built markets improving access gradually | 1 |
| Good; Eke Agbani Market, proximity to Enugu city | 1 |
| Good; large market, second largest urban center in state | 1 |
| Moderate; principal town with transit commerce present | 1 |
| Excellent; Obollo-Afor major transit commercial hub | 1 |
| Moderate; local markets, Enugu proximity aids access | 1 |
| Limited; local periodic markets in scattered settlements | 1 |
| Limited; 85km from Abuja city, poor road connectivity | 1 |
| Excellent; national commercial hub, diplomatic zone, markets | 1 |
| Good; Kubwa near city, Dei-Dei livestock market active | 1 |
| Moderate to good; Abuja-Lokoja highway, regional market | 1 |
| Moderate; major food market, airport proximity aids access | 1 |
| Limited; remote from Abuja, agricultural trade mostly local | 1 |
| Kumo 2nd largest hub; multiple weekly markets | 1 |
| Kindiyo market serves area; limited trade access | 1 |
| Billiri grains market; Kantoma Market rebuilt | 1 |
| Cattle and grain markets; remote from highways | 1 |
| Bajoga commercial center; new market shops built | 1 |
| State capital; major markets; best trade access | 1 |
| Local weekly markets; cross-LGA trade moderate | 1 |
| Near Gombe capital; moderate market access | 1 |
| Donfa market; Nafada Game Reserve tourism minor | 1 |
| Lalaipido international cattle market serves area | 1 |
| Kuri Cattle Market major; NALDA Market Kwadon | 1 |
| Local periodic markets, 30km to Owerri | 1 |
| Local markets, 35km to Owerri hub | 1 |
| Local markets, proximity to Owerri | 1 |
| Periodic markets, fair regional access | 1 |
| Local markets, limited city access | 1 |
| Sparse markets, limited connectivity | 1 |
| Good market access, close to Owerri | 1 |
| Weekly markets, limited road connectivity | 1 |
| Sparse periodic markets, weak connectivity | 1 |
| Good access to Owerri central market | 1 |
| Local markets, airport proximity aids trade | 1 |
| Periodic local markets, Eke Njaba notable | 1 |
| Local market, near Orlu commercial center | 1 |
| Periodic markets, moderate connectivity | 1 |
| Local markets, lake-based tourism potential | 1 |
| Isolated markets, poor road connectivity | 1 |
| Regional market hub, former railway junction | 1 |
| Sparse markets, weak road connectivity | 1 |
| Major hub, Imo International Market present | 1 |
| Periodic markets, limited connectivity | 1 |
| Local markets, Breweries at Awo-Omamma | 1 |
| Market junction town, regional trade node | 1 |
| State capital, central market hub, banking | 1 |
| Close to Owerri markets, university area | 1 |
| Proximity to Owerri, growing residential suburb | 1 |
| Limited, local periodic markets, near Hadejia hub | 1 |
| Cross-border trade with Niger, weekly markets | 1 |
| Major market center, good road links to Kano | 1 |
| Moderate, benefits from proximity to state capital | 1 |
| State capital, best regional market access in Jigawa | 1 |
| Near Gagarawa Industrial Park, improving access | 1 |
| Limited, small periodic markets | 1 |
| Emirate town, chief market for northern Jigawa | 1 |
| Moderate, periodic markets, road to Birnin Kudu | 1 |
| Major trade hub, large market, river-basin commerce | 1 |
| Moderate weekly market, road link east to Kano | 1 |
| Moderate, periodic markets, Sule Lamido University | 1 |
| Limited, isolated periodic markets near wetlands | 1 |
| Good market access, major highway link to Kano | 1 |
| Limited, small periodic markets along road | 1 |
| Moderate access, benefits from Dutse proximity | 1 |
| International border market, Export Processing Zone | 1 |
| Moderate, proximity to Dutse aids market access | 1 |
| Good weekly market, emirate seat, Kano road links | 1 |
| Very limited, small periodic markets | 1 |
| Limited, Khadija University nearby boosts activity | 1 |
| Moderate; highway corridor but insecurity disrupts | 1 |
| Limited; disrupted by banditry spillover | 1 |
| Good; major transport hub, Abuja-Kaduna rail | 1 |
| Limited; rural feeder roads to Zaria | 1 |
| Limited; conflict disrupts local market activity | 1 |
| Moderate; Kafanchan is Southern Kaduna trade hub | 1 |
| Limited; rural market access constrained | 1 |
| Excellent; state capital with diverse markets | 1 |
| Excellent; Panteka market, major commercial hub | 1 |
| Moderate; highway transit, mining provides jobs | 1 |
| Severely limited; conflict displaces markets | 1 |
| Very limited; rural and conflict-affected | 1 |
| Very limited; remote with poor roads | 1 |
| Limited; rural feeder roads to Zaria corridor | 1 |
| Moderate; proximity to Kaduna-Zaria highway | 1 |
| Moderate; highway market town, transit trade | 1 |
| Limited; rural with slowly improving connectivity | 1 |
| Good; Zaria commercial center, university economy | 1 |
| Very limited; severe displacement from conflict | 1 |
| Limited; agrarian area with poor road network | 1 |
| Limited; displacement severely disrupts trade | 1 |
| Good; historic commercial center, ABU hub | 1 |
| Limited; depends on feeder roads to Gaya | 1 |
| Moderate; connected to Bichi trade network | 1 |
| Good; highway town, regional trade center | 1 |
| Moderate; irrigated produce traded to Kano | 1 |
| Good; traditional craft and trade center | 1 |
| Moderate; highway commercial hub | 1 |
| Excellent; Dawanau Intl Grains Market, W Africa hub | 1 |
| Very limited; remote with mining as alternative | 1 |
| Excellent; Sabon Gari Market, Singer Market | 1 |
| Moderate; transit route to Jigawa | 1 |
| Moderate; irrigated produce, Kano proximity | 1 |
| Moderate; regional center for southern Kano | 1 |
| Good; Gezawa Commodity Market, Kano proximity | 1 |
| Good; residential-commercial, university economy | 1 |
| Moderate; local trade center | 1 |
| Limited; rural area in Kano North | 1 |
| Excellent; Kurmi Market, Kano commercial center | 1 |
| Moderate; local emirate with market activity | 1 |
| Moderate; road access toward Bauchi state | 1 |
| Moderate; larger rural LGA with local markets | 1 |
| Excellent; Challawa Industrial Area, Dawanau nearby | 1 |
| Very limited; remote rural area | 1 |
| Good; highway access, irrigated produce trade | 1 |
| Moderate; SW of Kano metro influence zone | 1 |
| Limited; remote rural area | 1 |
| Moderate; growing peri-urban area near Kano | 1 |
| Excellent; Bompai Industrial Estate, wholesale trade | 1 |
| Moderate; southern Kano commercial hub | 1 |
| Moderate; near western Kano metro boundary | 1 |
| Limited; rural with poor road network | 1 |
| Limited; historic town with local market | 1 |
| Moderate; highway access provides trade link | 1 |
| Good; suburban commercial activity | 1 |
| Moderate; near metro influence zone | 1 |
| Moderate; highway provides transit trade | 1 |
| Limited; remote southern Kano | 1 |
| Moderate; growing peri-urban near Kano city | 1 |
| Good; Wudil Cattle Market, major livestock hub | 1 |
| Moderate; Kasuwar Sama grain market active | 1 |
| Good; suburban growth area of Katsina city | 1 |
| Severely disrupted by banditry displacement | 1 |
| Limited; some cross-border trade with Niger | 1 |
| Limited; rural interior area | 1 |
| Moderate; Charanchi Central Market, highway access | 1 |
| Disrupted; large market affected by banditry | 1 |
| Limited; rural area between major towns | 1 |
| Good; historic trade center, Federal University | 1 |
| Limited; remote small northern LGA | 1 |
| Moderate; Federal University, zonal admin center | 1 |
| Severely disrupted; forest corridor to Zamfara | 1 |
| Good; major textile and cotton commercial center | 1 |
| Limited; remote rural eastern Katsina | 1 |
| Moderate; border market but insecurity disrupts | 1 |
| Limited; rural area with some conflict spillover | 1 |
| Limited; northern rural near Niger border | 1 |
| Disrupted; Funtua-Kankara corridor is insecure | 1 |
| Moderate; oil extraction facility boosts economy | 1 |
| Excellent; state capital, commercial and admin hub | 1 |
| Limited; conflict spillover disrupts trade | 1 |
| Limited; small remote rural LGA | 1 |
| Good; international market, major cross-border hub | 1 |
| Moderate; major market, grain processing center | 1 |
| Moderate; old trading center with zonal store | 1 |
| Limited; northern rural LGA | 1 |
| Limited; small rural LGA | 1 |
| Limited; ongoing banditry incidents disrupt trade | 1 |
| Moderate; highway access, dam economic potential | 1 |
| Limited; remote northern rural LGA | 1 |
| Limited; some cross-border trade potential | 1 |
| 30km from Birnin Kebbi; limited secondary road access | 1 |
| Very remote from Birnin Kebbi; limited market integration | 1 |
| Regional market center; fishing festival hub; 100km from capital | 1 |
| Moderate distance to Birnin Kebbi; some Niger border trade | 1 |
| Lolo Central Market active; borders Niger and Benin Republic | 1 |
| State capital; primary commercial and rice trade hub | 1 |
| Regional market noted; moderate distance to Birnin Kebbi | 1 |
| Remote from Birnin Kebbi; limited market access | 1 |
| Very remote; nearest major market via Zuru town | 1 |
| 35km from Birnin Kebbi; emirate market town; moderate access | 1 |
| Major commercial center on A1; 50km from Birnin Kebbi | 1 |
| 20km from Birnin Kebbi; relatively good capital access | 1 |
| A1 highway transit point; Koko market; 120km from capital | 1 |
| Remote from major commercial centers; limited integration | 1 |
| Niger River trade routes; limited road-based market access | 1 |
| Very remote from Birnin Kebbi; nearest hub is Zuru | 1 |
| On road between Birnin Kebbi and Yauri; some transit trade | 1 |
| Suru regional market noted; moderate distance to capital | 1 |
| Very remote; nearest significant market is Zuru town | 1 |
| Major market center; international onion market; A1 highway | 1 |
| Emirate HQ; regional market center for southern Kebbi | 1 |
| Moderate; proximity to Okene commercial hub aids trade | 1 |
| Moderate; Itobe bridge links east Kogi; steel complex nearby | 1 |
| Major Igala town on A233; periodic markets active | 1 |
| Poor; flood disruptions limit access; remote from highways | 1 |
| Fair; periodic rural markets; Anyigba university town nearby | 1 |
| Very poor; boat transport to Idah 42km; seasonal access only | 1 |
| Good; Niger River trade routes; links to Onitsha, Lokoja | 1 |
| Poor; remote rural area; limited market infrastructure | 1 |
| Fair; links to Kabba commercial center; periodic markets | 1 |
| Good; A123 highway access; major agricultural trade center | 1 |
| On A2 highway corridor; flood disruptions affect access | 1 |
| Excellent; state capital; Niger-Benue confluence trade hub | 1 |
| Poor to fair; gold processing plant may boost activity | 1 |
| Fair; Ugwolawo market; links to Anyigba educational hub | 1 |
| Fair; proximity to Okene provides market access | 1 |
| Moderate; near Okene commercial center; mine infrastructure | 1 |
| Major commercial center on A2; large markets; transport hub | 1 |
| Poor; remote rural area; limited periodic markets | 1 |
| Poor; rural area; limited market infrastructure | 1 |
| Fair; Isanlu market town; Kwara State border trade | 1 |
| Fair; border trade with Kwara-Ekiti; periodic markets | 1 |
| Moderate; close to Ilorin markets via A1 highway | 1 |
| Poor; 5+ hours from Ilorin; cross-border trade with Benin | 1 |
| Moderate; river transport links to other Niger towns | 1 |
| Limited; periodic local markets; transport to Ilorin needed | 1 |
| Moderate; Share has periodic markets; road links to Ilorin | 1 |
| Good; integrated into Ilorin commercial network | 1 |
| Good; connected to Ilorin markets and university economy | 1 |
| Excellent; Oja-Oba central market; major North-South junction | 1 |
| Good; Omu-Aran is regional market for Kwara South | 1 |
| Limited; relies on Omu-Aran and Offa for major trade | 1 |
| Poor; periodic markets only; very remote from centers | 1 |
| Moderate; Jebba is trade crossroads on Lagos-North highway | 1 |
| Very good; Owode Market 3820 shops; regional trade hub | 1 |
| Limited; nearest major market in Omu-Aran or Offa | 1 |
| Moderate; accessible to Offa Owode Market; periodic markets | 1 |
| Poor; periodic markets; Regatta Festival seasonal tourism | 1 |
| Strong, Agege market one of Lagos largest | 1 |
| Moderate, proximity to Apapa port, local markets | 1 |
| Good, multiple markets, Ikotun trade hub | 1 |
| Good, Mile 2 corridor, proximity to Apapa port | 1 |
| Excellent, Nigeria primary port, major trade gateway | 1 |
| Moderate, cross-border trade with Benin Republic | 1 |
| Moderate, fish market significant, growing connectivity | 1 |
| Excellent, Nigeria financial hub, premium retail district | 1 |
| Growing, Lekki FTZ and Dangote Refinery transforming area | 1 |
| Good, Ogba market, proximity to Ikeja commercial hub | 1 |
| Excellent, state capital, airport, Computer Village hub | 1 |
| Good, large markets, industrial zones, growing satellite | 1 |
| Good, Mile 12 market largest food market in Lagos | 1 |
| Excellent, Idumota and Balogun markets, TBS hub | 1 |
| Excellent, Yaba tech hub, UNILAG, major commercial area | 1 |
| Good, dense commercial activity, Mushin market thriving | 1 |
| Good, Alaba International electronics market is major hub | 1 |
| Excellent, major transport interchange, industrial area | 1 |
| Moderate, local markets, printing hub near mainland | 1 |
| Good, established commercial areas, stadium district | 1 |
| Moderate, on major highway, education hub, local markets | 1 |
| Poor, remote location, limited road infrastructure | 1 |
| Moderate to poor, herder-farmer conflict disrupts trade | 1 |
| Excellent, Karu International Market, direct Abuja access | 1 |
| Poor, remote rural, conflict-affected, small population | 1 |
| Good, 50km from Abuja, cattle market, university town | 1 |
| Moderate, along major road but largely rural hinterland | 1 |
| Best in state, capital, railway, airport, major market | 1 |
| Moderate, historic market center, Federal Polytechnic town | 1 |
| Moderate, between two major towns, hilly terrain limits | 1 |
| Poor, rural, conflict-displaced communities, limited infra | 1 |
| Moderate to poor, transit route FCT-Nasarawa, rural | 1 |
| Poor to moderate, remote hilly terrain, small population | 1 |
| Moderate, Minna-Bida road provides market corridor access | 1 |
| Very poor, extremely remote, limited transport links | 1 |
| Good, major regional trade hub, Nupe cultural center | 1 |
| Moderate, Kainji Dam area commerce, vast rural hinterland | 1 |
| Good, part of Minna urban area, university campus economy | 1 |
| Excellent, state capital, major markets, road and rail hub | 1 |
| Poor, isolated riverine communities, limited market infra | 1 |
| Moderate, near Bida market hub, agricultural trade corridor | 1 |
| Moderate, near FCT border, Gurara Falls tourism potential | 1 |
| Poor, remote southern LGA, seasonal river access only | 1 |
| Good, major regional trade center, A1 highway junction | 1 |
| Moderate, along Minna-Abuja road, university boosts economy | 1 |
| Poor to moderate, Baro historical river port, limited | 1 |
| Very poor, extremely remote, insecurity limits market access | 1 |
| Very poor, banditry severely disrupts farming and trade | 1 |
| Poor, insecurity constrains market, gold trading informal | 1 |
| Good, major A1 highway transit town, regional farming trade | 1 |
| Very poor, banditry severely limits farming and markets | 1 |
| Moderate, accessible from Minna, local periodic markets | 1 |
| Very poor, grain trade collapsed due to banditry | 1 |
| Very poor, insecurity and remoteness severely limit trade | 1 |
| Poor, banditry severely disrupts farming and markets | 1 |
| Excellent, Abuja commuter hub, vibrant markets, trade | 1 |
| Good, peri-urban Abuja overflow, growing commercial activity | 1 |
| Moderate, periodic local markets, agricultural trade to Minna | 1 |
| Excellent; state capital with direct expressway to Lagos | 1 |
| Excellent; administrative hub, direct Lagos expressway | 1 |
| Excellent; borders Lagos directly, major industrial estates | 1 |
| Good; 30 km to Abeokuta, 60 km to Lagos via expressway | 1 |
| Good; borders Lagos at Ojodu-Berger, strong connectivity | 1 |
| Poor; vast area, remote interior, limited road network | 1 |
| Moderate; 30 km from Ijebu-Ode, 60 km from Sagamu | 1 |
| Moderate; close to Ijebu-Ode but limited local roads | 1 |
| Good; on expressway, 30 km to Sagamu, 110 km Lagos | 1 |
| Good; 10 km from Sagamu, Babcock University area | 1 |
| Very poor; far from Abeokuta, 93 km Benin border | 1 |
| Moderate; Idiroko border post, 80 km from Lagos | 1 |
| Good in south; Mowe-Ibafo 30 min from Lagos | 1 |
| Moderate; adjacent to Abeokuta, FUNAAB campus present | 1 |
| Moderate; 15 km from Ijebu-Ode, borders Lagos State | 1 |
| Very poor; remote, waterway-dependent, far from Abeokuta | 1 |
| Moderate; 20 km from Sagamu via state roads | 1 |
| Excellent; strategic highway junction, 60 km from Lagos | 1 |
| Moderate; 35 km from Abeokuta, border trade at Eggua | 1 |
| Moderate; 50 km from Abeokuta, Federal Polytechnic town | 1 |
| Moderate; largest Akoko commercial center, 100 km Akure | 1 |
| Poor; remote northern highland, 110+ km from Akure | 1 |
| Moderate; connected to Owo and Akure via Akoko roads | 1 |
| Moderate; gateway from Owo into Akoko area | 1 |
| Excellent; immediately adjacent to state capital Akure | 1 |
| Excellent; state capital and central market hub | 1 |
| Very poor; remote, waterway-dependent, far from Akure | 1 |
| Good; close proximity to Akure on road corridor | 1 |
| Good; on expressway, 30 km from Akure | 1 |
| Very poor; waterway-based trade, very remote from Akure | 1 |
| Moderate; connected to Ondo town and Akure | 1 |
| Moderate; connected via Ore junction and Okitipupa | 1 |
| Good; major transit hub on busiest national highway | 1 |
| Moderate; connected to Ore and southern Ondo towns | 1 |
| Moderate; proximity to Ondo town aids market access | 1 |
| Good; historic city on major highway, 45 km from Akure | 1 |
| Moderate; connected to Owo but largely remote interior | 1 |
| Good; on major highway, 80 km from Akure | 1 |
| Good; on Osogbo-Ibadan corridor, 30 km from Osogbo | 1 |
| Moderate; close to Osogbo but off major highway | 1 |
| Moderate; connected via Ilesa, mining traffic present | 1 |
| Moderate; on express road, cocoa marketed via Ilesa | 1 |
| Poor; relatively remote from Osogbo, northern area | 1 |
| Good; close to Osogbo on major northward road | 1 |
| Good; 30 km from Osogbo on Ibadan corridor, railway | 1 |
| Good; part of Ede urban area, close to Osogbo | 1 |
| Excellent; virtually contiguous with Osogbo capital | 1 |
| Moderate; connected via Ede, UNIOSUN campus present | 1 |
| Good; major road intersection, OAU-driven economic hub | 1 |
| Good; part of greater Ile-Ife urban zone | 1 |
| Good; between Osogbo and Ile-Ife on main road | 1 |
| Poor; distant from Osogbo, southern peripheral LGA | 1 |
| Very poor; farthest from Osogbo, bad road access | 1 |
| Good; 20 km north of Osogbo on major highway | 1 |
| Moderate; 50 km from Osogbo on northern road corridor | 1 |
| Good; strategic gateway city at major road intersection | 1 |
| Good; part of Ilesa commercial zone | 1 |
| Excellent; virtually adjacent to state capital Osogbo | 1 |
| Good; on major route to Ibadan, 50 km from Osogbo | 1 |
| Moderate; connected to major roads via Gbongan area | 1 |
| Good; 35 km from Osogbo on major Ibadan corridor | 1 |
| Moderate; accessible through Ilesa road network | 1 |
| Moderate; 40 km from Osogbo, UNIOSUN campus at Okuku | 1 |
| Poor; western periphery, limited road connectivity | 1 |
| Excellent; part of greater Osogbo metropolitan area | 1 |
| Moderate; 10 km north of Ilesa, tourism potential | 1 |
| Moderate; central area with road access to Osogbo | 1 |
| Excellent; state capital, central market and transport hub | 1 |
| Moderate; near Oyo town on Lagos-North highway | 1 |
| Moderate; Moniya market and railway terminal | 1 |
| Good; Oyo town on Lagos-North highway corridor | 1 |
| Limited; local markets and some border trade | 1 |
| Moderate; close proximity to Ibadan markets | 1 |
| Excellent; Bodija market, UCH, state institutions | 1 |
| Very good; Iwo Road major transport-commerce hub | 1 |
| Excellent; Dugbe market and state secretariat | 1 |
| Good; Oje and Agbeni traditional markets | 1 |
| Excellent; Bola Ige market, Challenge zone | 1 |
| Moderate; Towobowo market regional trade center | 1 |
| Moderate; Eruwa agribusiness hub developing | 1 |
| Limited; local periodic markets in Ayete | 1 |
| Limited; dependent on Ibadan for commerce | 1 |
| Limited; Kishi is a border market town | 1 |
| Moderate; Oke-Ogun zonal administrative hub | 1 |
| Very limited; isolated from major markets | 1 |
| Very limited; remote from commercial centers | 1 |
| Moderate; Okeho significant Oke-Ogun market town | 1 |
| Moderate; proximity to Ibadan urban core | 1 |
| Good; Aarada market; LAUTECH university town | 1 |
| Moderate; proximity to Ogbomosho urban markets | 1 |
| Limited; local markets; quarry underexploited | 1 |
| Good; industrial estate; Ibadan market access | 1 |
| Moderate; local markets; Ibadan proximity helps | 1 |
| Moderate; Owode market Igboho regional hub | 1 |
| Limited; local periodic markets only | 1 |
| Limited; dependent on Oyo town markets | 1 |
| Good; Oyo town major market and commercial center | 1 |
| Very limited; dependent on Saki town for trade | 1 |
| Good; major Oke-Ogun hub; Benin border trade | 1 |
| Moderate; weekly markets; 50km from Jos | 1 |
| Limited; weekly markets; borders Kaduna, Bauchi | 1 |
| Moderate; major Irish potato trading hub | 1 |
| Moderate; weekly markets; Jos proximity benefits | 1 |
| Excellent; Terminus Market, banks, commercial hub | 1 |
| Good; industrial markets; close to Jos center | 1 |
| Limited; weekly Dengi markets; 180km from Jos | 1 |
| Limited; small weekly markets; transit route | 1 |
| Moderate; Langtang is historic market center | 1 |
| Limited; small markets; dependent on Langtang | 1 |
| Moderate; historic colonial-era market center | 1 |
| Very limited; smallest local markets in state | 1 |
| Moderate; Pankshin divisional trading center | 1 |
| Limited; rice production center; Nasarawa border | 1 |
| Limited; weekly markets; conflict disrupts trade | 1 |
| Moderate; Shendam colonial-era market center | 1 |
| Limited; weekly Wase markets; very far from Jos | 1 |
| Limited; local weekly markets; poor road links | 1 |
| Fair; Ahoada regional market; East-West link | 1 |
| Poor; limited road connectivity; partly waterway | 1 |
| Limited; waterway-dependent; local markets only | 1 |
| Very limited; isolated coastal; boat-only trade | 1 |
| Moderate in Buguma; limited in riverine parts | 1 |
| Moderate; NLNG economic activity; boat-dependent | 1 |
| Limited; historic port now underused | 1 |
| Good; Onne Free Trade Zone; industrial corridor | 1 |
| Moderate; Emohua and Elele local market centers | 1 |
| Moderate; Okehi local market; Imo State links | 1 |
| Limited; Kpor and Bodo local markets only | 1 |
| Good; PH proximity; airport corridor access | 1 |
| Moderate in Bori town; limited in rural areas | 1 |
| Excellent; major retail hubs and supermarkets | 1 |
| Moderate in Omoku; rural areas poorly connected | 1 |
| Limited; local markets; some PH linkage | 1 |
| Good; PH proximity; active petroleum trade | 1 |
| Limited; Eberi local markets; Imo border link | 1 |
| Limited; boat-dependent; historically isolated town | 1 |
| Good; PH satellite; industrial-commercial hub | 1 |
| Excellent; Mile 1 and 3 markets; major seaport | 1 |
| Very limited; Sakpenwa small market; poor access | 1 |
| Limited, small local weekly market only | 1 |
| Regional market center near state capital | 1 |
| CCNN cement factory provides economic anchor | 1 |
| Weekly market in Gada, Niger border proximity | 1 |
| Moderate, dam-area boosts agricultural trade | 1 |
| Commercial hub on major Illela trade route | 1 |
| Major cross-border trade hub with Niger Republic | 1 |
| Severely disrupted by insecurity and banditry | 1 |
| Limited, weekly rural markets, Kebbi border trade | 1 |
| Good access, proximity to Sokoto city markets | 1 |
| Very limited, disrupted by banditry | 1 |
| Severely disrupted by insecurity and displacement | 1 |
| Small weekly market, limited trade connectivity | 1 |
| Limited, small weekly market only | 1 |
| State capital, excellent market connectivity | 1 |
| Urban commercial center, strong market access | 1 |
| Regional trading center, river-area agriculture | 1 |
| Limited, disrupted by banditry and remoteness | 1 |
| Small market town, limited trade infrastructure | 1 |
| Strong access, peri-urban to state capital | 1 |
| Moderate, mineral deposits attract some trade | 1 |
| Moderate, on route from Sokoto southward | 1 |
| Close to Jalingo, moderate local market access | 1 |
| Major commercial center, cross-LGA trade hub | 1 |
| Donga River trade; conflict disrupts market access | 1 |
| Very limited; isolated from main trade routes | 1 |
| Dan-Anacha largest yam market in Taraba State | 1 |
| Benue River fishing port and trade point | 1 |
| State capital, central market hub | 1 |
| Limited; Benue River corridor for local trade | 1 |
| Remote; timber trade near Cameroon border | 1 |
| Benue River fishing trade; local weekly markets | 1 |
| Limited; tea and livestock; Cameroon border trade | 1 |
| Significant commercial center; border area trade | 1 |
| Very limited; some cross-border Cameroon trade | 1 |
| Major trade center; Federal University present | 1 |
| Limited local markets; some trade via Jalingo | 1 |
| Moderate access along Adamawa road corridor | 1 |
| Gashua is regional trading hub, moderate access | 1 |
| Limited market access, conflict-disrupted trade routes | 1 |
| State capital, government hub, moderate market access | 1 |
| Moderate access via proximity to Potiskum hub | 1 |
| Limited, long distances to Potiskum and Damaturu | 1 |
| Severely conflict-disrupted, OCHA Tier 1 priority LGA | 1 |
| Severely limited, active conflict zone, OCHA Tier 1 | 1 |
| Very limited, remote and conflict-affected area | 1 |
| Moderate, junction town on Potiskum-Gashua route | 1 |
| Limited, remote with periodic insecurity disruptions | 1 |
| Limited, Niger Republic border, small cross-border trade | 1 |
| Moderate, connected to Potiskum and Gashua corridor | 1 |
| Significant commercial hub, railway link to Kano | 1 |
| Largest commercial center, major West African cattle market | 1 |
| Limited, transit corridor between Damaturu and north | 1 |
| Very limited, Niger border, conflict-disrupted trade | 1 |
| Very limited, remote border area with Niger Republic | 1 |
| Market access disrupted by insecurity and lockdowns | 1 |
| Limited; depends on access to Gummi and Talata Mafara | 1 |
| Limited; bandit taxation and raids disrupt trade | 1 |
| Severely disrupted; markets closed during lockdowns | 1 |
| Moderate access via highway to Gusau and Sokoto | 1 |
| Moderate; weekly markets, road link to Sokoto | 1 |
| State capital, central market hub, railway terminus | 1 |
| Major collecting point for cotton and groundnuts | 1 |
| Limited; displacement and banditry disrupt farming | 1 |
| Limited; insecurity disrupts trade and farm access | 1 |
| Cross-border trade with Niger disrupted by banditry | 1 |
| Regional trade center, active weekly markets | 1 |
| Fair highway corridor access; banditry affects rural | 1 |
| Severely disrupted; highest bandit incident count | 1 |


### `Traditional Authority Influence`

Unique values: **630** | Nulls: **0**

| Value | Count |
|-------|-------|
| High — emirate ward heads and mosque networks | 47 |
| High — emir endorses candidates via ward and mosque networks | 19 |
| High — emirate networks dominate urban wards | 11 |
| High — emirate ward network and mosque influence | 10 |
| High — Daura emirate ward and mosque networks | 8 |
| Medium — banditry crisis undermines traditional authority reach | 7 |
| High — Emirate system shapes local governance and land matters | 6 |
| High — resident emir directly mobilises voters and endorses candidates | 5 |
| Medium — ethnic chief arbitration and mobilization | 5 |
| Medium — fragmented multi-ethnic chieftaincies | 5 |
| High — Emirate system shapes politics and land allocation | 5 |
| Medium — Annang clan system guides disputes and politics | 3 |
| Medium — clan-based system active amid oil dynamics | 3 |
| High — emir endorses via district heads and mosque networks | 3 |
| High — emirate networks despite moderate banditry | 3 |
| Medium — influence eroded by severe insecurity | 3 |
| Medium — influence eroded by insecurity | 3 |
| High — Emirate council controls chieftaincy and land matters | 3 |
| Medium — Annang clan system guides local disputes | 2 |
| Medium — clan heads retain influence near state capital | 2 |
| Medium — clan-based system guides local disputes | 2 |
| Medium — Oron clan system guides disputes and politics | 2 |
| Medium — Biu Emirate council authority over rural area | 2 |
| Medium — diluted by urban diversity | 2 |
| High — emir mediates banditry peace talks | 2 |
| Medium — district head channels emirate authority locally | 2 |
| High — emirate controls customary affairs and land allocation | 2 |
| High — Sultanate council dominates local governance norms | 2 |
| High — Emirate authority central to community mediation | 2 |
| High — Sultanate council guides peri-urban governance | 2 |
| Low — insurgency displaced traditional rulers, authority collapsed | 2 |
| Low — fragmented Igbo system, urban commercial hub | 1 |
| Low — fragmented Igbo system, dense commercial center | 1 |
| Medium — hereditary Eze Aro stool, Aro Confederacy legacy | 1 |
| Low — fragmented clan system, dispersed rural communities | 1 |
| Low — fragmented Igbo system, university town influence | 1 |
| Low — fragmented Ngwa clan system, semi-urban area | 1 |
| Low — fragmented Ngwa clan system, rural settlements | 1 |
| Medium — strong Imenyi kingdom identity, clan cohesion | 1 |
| Low — fragmented Ngwa system, peri-urban Aba corridor | 1 |
| Medium — warrior-town heritage, strong age-grade system | 1 |
| Low — fragmented Ngwa system, peri-urban Aba sprawl | 1 |
| Low — fragmented Igbo system, small semi-rural LGA | 1 |
| Low — fragmented Igbo system, rural riverine area | 1 |
| Low — fragmented Asa-Igbo system, rural southern LGA | 1 |
| Low — fragmented Igbo system, rural hilly terrain | 1 |
| Low — fragmented Igbo system, state capital governance hub | 1 |
| Low — fragmented Igbo system, state capital periphery | 1 |
| Medium — Bachama/Bata district heads mediate local disputes | 1 |
| High — new emirate consolidates Fulani authority in area | 1 |
| High — Chamba paramount ruler commands strong loyalty | 1 |
| High — core Lamido domain retains strong political influence | 1 |
| Medium — new chiefdom, influence partly disrupted by conflict | 1 |
| Medium — Longuda traditional ruler influences local governance | 1 |
| Medium — new chiefdom amid ongoing Boko Haram disruption | 1 |
| Medium — district heads under Gangwari moderate local affairs | 1 |
| High — spiritual seat of Bachama Kingdom, strong authority | 1 |
| Medium — new chiefdom; authority disrupted by Boko Haram | 1 |
| Medium — new emirate rebuilding authority near conflict zone | 1 |
| Medium — district heads manage affairs post-emirate restructuring | 1 |
| Medium — new Kamwe chiefdom; authority disrupted by insurgency | 1 |
| High — historic emirate retains strong commercial/political sway | 1 |
| High — Mubi emirate influence extends to semi-urban hinterland | 1 |
| High — paramount Bachama ruler, Numan Federation political hub | 1 |
| Medium — district heads under Numan Federation influence | 1 |
| Medium — new Yungur chiefdom building authority in rural area | 1 |
| Medium — remote area, district heads under Gangwari authority | 1 |
| High — Lamido system retains strong political mobilisation power | 1 |
| High — Lamido palace located here; cultural/political centre | 1 |
| Medium — Annang clan system active in local governance | 1 |
| Medium — clan-based system complicated by oil politics | 1 |
| Medium — clan heads retain social influence in oil hub | 1 |
| Medium — clan heads active amid oil-resource dynamics | 1 |
| Medium — clan heads retain social influence near capital | 1 |
| Medium — clan system complicated by oil-resource politics | 1 |
| Medium — clan heads retain influence in peri-urban area | 1 |
| Medium — clan-based system guides disputes and politics | 1 |
| Medium — clan-based system; sacred Ibibio origin site | 1 |
| Medium — Annang heartland; clan system active in politics | 1 |
| Medium — clan-based system guides disputes; food-basket LGA | 1 |
| Medium — Oron clan system; influence shaped by oil politics | 1 |
| High — seat of Oku Ibom Ibibio; strong clan influence | 1 |
| Medium — Oron traditional council active; fishing hub | 1 |
| Medium — Annang clan system guides disputes; largest LGA | 1 |
| Medium — Oron elder; chairs Supreme Council of TRs | 1 |
| Medium — clan heads retain social influence in capital | 1 |
| Medium — community Igwes mediate land disputes | 1 |
| Medium — Eri dynasty ritual authority shapes community affairs | 1 |
| Medium — rulers mediate land affairs in remote riverine area | 1 |
| High — Eze Nri holds unique pan-Igbo spiritual authority | 1 |
| Medium — community Igwes handle dispute resolution locally | 1 |
| Medium — state capital context dilutes traditional authority | 1 |
| Medium — strong influence in dispersed riverine communities | 1 |
| Medium — community governance in semi-urban transitional zone | 1 |
| Medium — Igwes active in dispute resolution and development | 1 |
| High — Chairman, Anambra State Traditional Rulers Council | 1 |
| Medium — multiple community Igwes share authority across LGA | 1 |
| Medium — community Igwes active in rural governance | 1 |
| Medium — strong cultural identity anchored by Igu Aro festival | 1 |
| High — longest-reigning monarch over major industrial city | 1 |
| Medium — multiple community Igwes share rural authority | 1 |
| Medium — rulers important in riverine land and flood disputes | 1 |
| High — one of Nigeria's most prominent traditional stools | 1 |
| Medium — Obi authority diluted by large non-indigene population | 1 |
| Medium — many small-community Igwes share local authority | 1 |
| Medium — rulers govern local land and cultural affairs | 1 |
| Medium — community Igwes active in local governance | 1 |
| High — emirate district heads control grassroots mobilisation | 1 |
| High — paramount emir; mosque and ward head networks | 1 |
| Medium — emerging chiefdom; church and elder networks | 1 |
| High — emirate district structure and Islamic institutions | 1 |
| High — emirate ward heads and Islamic institution networks | 1 |
| Medium — non-Muslim origin emirate in mixed community | 1 |
| High — Katagum emirate ward and mosque networks | 1 |
| High — senior Madaki district head governs directly | 1 |
| High — Katagum emirate ward heads and Islamic networks | 1 |
| High — Katagum emirate district and mosque structure | 1 |
| High — autonomous first-class emirate since 1835 | 1 |
| High — major emirate HQ in Azare; ward and mosque networks | 1 |
| High — Bauchi Emirate district and ward head controls | 1 |
| High — autonomous emirate; mosque and district head networks | 1 |
| High — first-class emirate controls Ningi and Warji LGAs | 1 |
| High — Katagum emirate; district head reserved for emir's son | 1 |
| Medium — contested authority; church and community elders | 1 |
| High — new Toro Emirate created 2025; active governance | 1 |
| Medium — emerging Warji emirate; ethnic identity in transition | 1 |
| High — Katagum emirate historical heartland; strong ward system | 1 |
| Medium — ex-military governor; former state council chairman | 1 |
| Low — fragmented clan structure; remote terrain limits authority | 1 |
| Medium — dual monarchy mediates between Kolokuma-Opokuma clans | 1 |
| Medium — former OPEC Secretary-General; oil-sector connections | 1 |
| Medium — rotational kingship; oil industry presence adds leverage | 1 |
| Medium — kingdom spans multiple LGAs; ceremonial-mediatory role | 1 |
| Low — dispersed clan heads across extremely remote riverine area | 1 |
| Medium — chairs Bayelsa State Traditional Rulers Council | 1 |
| Medium-High — Och'Idoma authority via district heads | 1 |
| Medium-High — Och'Idoma hails from Agatu, direct influence | 1 |
| Medium-High — Och'Idoma authority through intermediate council | 1 |
| Medium — Ter chief mediates clan disputes at LGA level | 1 |
| Medium-High — Tor Tiv palace seat elevates traditional governance | 1 |
| Medium — Ter chief active but insecurity limits reach | 1 |
| Medium — Ter chief mediates disputes across kindreds | 1 |
| Medium — Ter chief vocal on security, mediates disputes | 1 |
| Medium — Ter chief in semi-urban market town setting | 1 |
| Medium — Ter chief in remote hilly terrain community | 1 |
| Medium — Ter chief in Tor Tiv home LGA, cultural weight | 1 |
| Medium — Ter chief in conflict-prone area, limited reach | 1 |
| Low-Medium — urban state capital dilutes traditional authority | 1 |
| Medium — dual Igede-Idoma authority, shared governance | 1 |
| Medium-High — Och'Idoma IV from Ogbadibo, strong local ties | 1 |
| Medium-High — Och'Idoma authority via intermediate council | 1 |
| Medium — multiple traditional authorities, Igede-Idoma area | 1 |
| Medium-High — Och'Idoma oversees districts via council | 1 |
| Medium-High — Och'Idoma palace seat, direct governance influence | 1 |
| Medium — Ter chief mediates local Tiv clan matters | 1 |
| Medium — Ter chief in Zaki Biam yam market area | 1 |
| Medium — Ter chief in rural Tiv clan area | 1 |
| Medium — Ter chief in semi-urban Jechira area center | 1 |
| High — paramount Kanuri authority, area inaccessible to insurgency | 1 |
| Medium-High — first-class emir over mixed-ethnic area | 1 |
| Medium-High — newly crowned shehu, emirate rebuilding post-conflict | 1 |
| Medium-High — first-class emir, southern Borno admin hub | 1 |
| Medium — influence via district heads, partially conflict-disrupted | 1 |
| Medium — reconstituted emirate, partially rebuilt post-conflict | 1 |
| Medium-High — second-ranking Borno ruler, invested Feb 2025 | 1 |
| Medium-Low — district head authority, conflict-disrupted | 1 |
| Low — severely devastated, active insurgent zone | 1 |
| Medium — active emir, partially recovered from BH occupation | 1 |
| Medium — Biu Emirate council authority, relatively stable | 1 |
| High — peri-urban Maiduguri, strong Shehu institutional presence | 1 |
| Medium — rural emirate authority via district heads | 1 |
| Low — severely conflict-devastated, authority displaced | 1 |
| Medium — near Maiduguri, Sambisa-adjacent, partially affected | 1 |
| Low — severely devastated, historic capital destroyed | 1 |
| Medium-Low — conflict-affected along Trans-Sahel Highway | 1 |
| Medium-Low — recurrent insurgent attacks disrupt governance | 1 |
| Medium — urbanization dilutes traditional authority despite palace | 1 |
| Low — severely devastated, telecom towers destroyed | 1 |
| Low — severely conflict-devastated Lake Chad border area | 1 |
| Medium — garrison town, traditional authority partially restored | 1 |
| Low — severely devastated border town, authority displaced | 1 |
| Low — conflict-affected, limited traditional governance reach | 1 |
| Medium — first-class emir, culturally active Menwara festival | 1 |
| Medium — advisory role in communal dispute mediation | 1 |
| Medium — mediates land and chieftaincy matters | 1 |
| Medium — cultural authority in Efik-Qua coastal communities | 1 |
| Low-Medium — authority limited by ICJ cession dispute | 1 |
| Medium — leads clan heads council on security matters | 1 |
| Medium — mediates inter-community land and boundary disputes | 1 |
| Medium — confers chieftaincy titles as cultural custodian | 1 |
| Medium — co-presides traditional council in state capital | 1 |
| Medium — shares governance with Obong in urban Calabar | 1 |
| Medium — authority contested due to prior suspension dispute | 1 |
| Medium — presides over multi-ethnic secondary urban center | 1 |
| Low-Medium — remote highland area limits institutional reach | 1 |
| Medium — mediates land and communal affairs in Mbembe area | 1 |
| Medium — newly installed Dec 2023, rebuilding institutional authority | 1 |
| Medium — Efik traditional authority near state capital | 1 |
| Medium — heads traditional council in historic admin center | 1 |
| Medium-High — strong communal authority, mobilizes public campaigns | 1 |
| Medium — presides over multi-clan traditional council | 1 |
| Medium — cultural custodianship and community mediation | 1 |
| Medium — land governance and cultural stewardship | 1 |
| Medium — Ijaw clan mediation and cultural custodianship | 1 |
| Low — fragmented authority across many Ijaw clans | 1 |
| Medium — Urhobo kingdom governance and dispute mediation | 1 |
| Medium — cultural authority and community arbitration | 1 |
| High — longest-reigning monarch, ex-Council chairman | 1 |
| High — historic Benin-linked monarchy, wide recognition | 1 |
| Medium — community mediation and cultural leadership | 1 |
| Medium — community governance and cultural custodianship | 1 |
| Medium — historic kingdom with reduced modern influence | 1 |
| Low — gerontocratic system with dispersed authority | 1 |
| High — chairs Delta State Traditional Rulers Council | 1 |
| Medium — dispersed authority among community Obis | 1 |
| High — state capital influence, political and cultural weight | 1 |
| Low — dispersed Ijaw clan authority, limited reach | 1 |
| Medium — Okpe suzerainty over Sapele territory | 1 |
| Medium — Urhobo kingdom governance near Warri metro | 1 |
| Medium — major Urhobo kingdom, 31-plus years reign | 1 |
| Medium — Urhobo kingdom, ex-Urhobo rulers chairman | 1 |
| Low — gerontocratic system, no single paramount ruler | 1 |
| Medium — chairs Urhobo Traditional Rulers Council | 1 |
| Medium — shared Itsekiri-Ijaw jurisdiction area | 1 |
| High — paramount Itsekiri ruler, strong national profile | 1 |
| Medium — Ijaw clan authority in oil-producing area | 1 |
| Low — fragmented across multiple autonomous community Ezes | 1 |
| Low — multiple community Ezes, no single paramount ruler | 1 |
| Medium — hereditary Ezeogo respected across Edda clan | 1 |
| Low — fragmented authority among multiple community-level Ezes | 1 |
| Low — multiple Ezes with council-based coordination only | 1 |
| Medium — Mkpuma chairs Ebonyi State and Southeast TRC | 1 |
| Low — multiple community Ezes, no single paramount chief | 1 |
| Low — fragmented across multiple clan-based communities | 1 |
| Low — multiple community Ezes, limited cross-community authority | 1 |
| Low — fragmented across Izzi autonomous communities | 1 |
| Low — multiple clan Ezes, no single paramount ruler | 1 |
| Low — fragmented across diverse multi-clan groups | 1 |
| Medium — historically prominent stool, pioneer State TRC chair | 1 |
| Medium — multiple autonomous clan chieftaincies | 1 |
| High — direct Benin palace authority in metro area | 1 |
| Medium — senior hereditary Esan Onojie title | 1 |
| Medium — autonomous hereditary Esan kingship | 1 |
| Medium — hereditary Onojie with village elder councils | 1 |
| Medium — hereditary Onojie in university town | 1 |
| Medium — decentralized clan-based chieftaincy system | 1 |
| Medium — traditional riverine kingdom authority | 1 |
| High — paramount Islamic monarchy over Auchi kingdom | 1 |
| Medium — hereditary Onojie with elder councils | 1 |
| High — direct Benin palace authority in peri-urban belt | 1 |
| High — seat of Benin monarchy and royal palace | 1 |
| High — Benin vassal chiefs under direct Oba authority | 1 |
| High — Benin palace authority via local Enigie | 1 |
| Medium — Benin authority moderated by remoteness | 1 |
| Medium — decentralized elder-based clan governance | 1 |
| Medium — gerontocratic system without central king | 1 |
| High — Benin kingdom authority via local Enigie | 1 |
| High — state-capital throne, politically consulted, national stature | 1 |
| Medium — Pelupelu Oba, respected but smaller LGA | 1 |
| Medium — Pelupelu Oba, commercial town near Kogi border | 1 |
| Medium-High — appointed State Traditional Council chair by Fayemi | 1 |
| Medium — Pelupelu throne, succession pending court-settled dispute | 1 |
| Medium — Pelupelu Oba, newly installed mid-2025 | 1 |
| Medium-Low — smaller LGA, not among Pelupelu Obas | 1 |
| Medium-High — Pelupelu Oba, former State Traditional Council chair | 1 |
| High — historically 2nd-ranked Ekiti Oba, culturally significant | 1 |
| High — current State Obas Chairman, second-largest Ekiti town | 1 |
| High — supreme throne, paramount over 24 sub-Obas | 1 |
| Low-Medium — smallest Ekiti LGA, rural, limited reach | 1 |
| Medium — on throne since 1959, revered for extreme longevity | 1 |
| Medium-High — Pelupelu Oba, largest kingdom land area | 1 |
| High — traditionally 1st-ranked Ekiti Oba, installed 2020 | 1 |
| Medium-High — Pelupelu Oba, hosts Federal University Oye-Ekiti | 1 |
| Medium — rural, consulted by politicians, limited direct power | 1 |
| Medium — semi-rural, social influence, limited political power | 1 |
| Low-Medium — urban, hereditary throne, largely ceremonial | 1 |
| Low — urban Enugu core, purely ceremonial role | 1 |
| Low — fully urban, fragmented authority, ceremonial only | 1 |
| Medium — rural, traditional rulers retain social influence | 1 |
| Medium — rural, decentralised authority across multiple communities | 1 |
| Medium-High — strong spiritual authority, state TRC Grand Patron | 1 |
| Medium — rural LGA, moderate traditional authority | 1 |
| Medium — remote rural, dispute resolution, Ikem throne vacant | 1 |
| Medium — rural, social authority, active in land disputes | 1 |
| Medium — peri-urban, politically connected, state-level role | 1 |
| Medium — university town, academic influence dilutes authority | 1 |
| Medium — semi-rural, moderate traditional influence | 1 |
| Medium — major transit town on A3 highway, moderate | 1 |
| Medium — semi-urban, historically important divisional HQ | 1 |
| Medium — remote rural, social influence, limited political power | 1 |
| Low-Medium — 1st-class chief, FCT Traditional Council chairman | 1 |
| Very Low — cosmopolitan capital, traditional authority minimal | 1 |
| Low-Medium — Gbagyi ancestral homeland, cultural preservation role | 1 |
| Low-Medium — peri-urban, Gbagyi/Gade community influence | 1 |
| Low-Medium — semi-rural, active in community governance | 1 |
| Low-Medium — rural, ceremonial with some community influence | 1 |
| High — emirate ward-head network and candidate endorsement | 1 |
| Medium — fragmented among Cham, Waja, Dadiya chiefs | 1 |
| Medium-high — paramount Tangale chiefdom, contested 2021 appointment | 1 |
| High — emirate mosque networks and traditional title system | 1 |
| High — emirate structure with ward and village heads network | 1 |
| Very high — first-class emir, chairs State Council of Chiefs | 1 |
| High — Deputy Chairman State Council; respected non-emirate chiefdom | 1 |
| High — governed through Gombe Emirate ward-head hierarchy | 1 |
| High — emirate structure with historical political influence | 1 |
| Low-medium — fragmented authority among multiple community chiefs | 1 |
| High — three emirates in LGA; strong ward-head networks | 1 |
| Medium — settles community disputes and mobilises voters | 1 |
| Medium — mediates land disputes; influences local mobilization | 1 |
| Medium — cultural custodianship; moderate electoral influence rurally | 1 |
| Medium — settles inter-community disputes; moderate political influence | 1 |
| Medium — custodian of traditions; influences community voting patterns | 1 |
| Medium — cultural authority strong; limited formal political power | 1 |
| Medium — moral authority via church and dispute resolution | 1 |
| Medium — close to Owerri; moderate governance influence | 1 |
| Medium — settles inter-village disputes; respected but fragmented | 1 |
| Medium — traditional Obi title; arbitrates community land disputes | 1 |
| Medium — proximity to Owerri boosts relevance; political mobilization | 1 |
| Medium — near Owerri and airport; moderate local influence | 1 |
| Medium — Obi title carries cultural weight; arbitrates disputes | 1 |
| Medium — market town prominence; moderate political consultation | 1 |
| Medium — rural authority significant; community dispute settlement | 1 |
| Medium — community governance role; moderate electoral influence | 1 |
| Medium — historic lakeside town; respected cultural authority | 1 |
| Medium — oil community dynamics; mediates company-community relations | 1 |
| Medium — major town; zonal political and electoral influence | 1 |
| Medium — rural authority; community cultural custodianship role | 1 |
| Medium — major commercial town; significant political mobilization | 1 |
| Low-medium — remote rural; limited influence beyond community | 1 |
| Medium — community governance; some oil-related mediation role | 1 |
| Medium — market town influence; moderate political consultation | 1 |
| Low — urban state capital; modern governance fully dominates | 1 |
| Low-medium — peri-urban; traditional authority diluted by urbanization | 1 |
| Low-medium — hosts FUTO; authority diluted by urbanization | 1 |
| Medium — influence limited by banditry crisis | 1 |
| High — emirate seat with direct influence | 1 |
| Medium — district head mediates land and community disputes | 1 |
| Medium — emirate authority moderated by Niger border remoteness | 1 |
| High — direct emirate seat; fishing festival amplifies influence | 1 |
| Medium — district head mediates in remote riverine area | 1 |
| High — emirate palace in state capital; chairs Council of Chiefs | 1 |
| Medium — district head administers local traditional affairs | 1 |
| Medium — emirate authority in Zabarmawa-inhabited border zone | 1 |
| Medium — chiefdom head in remote multi-ethnic area | 1 |
| High — historic emirate seat; Sokoto Caliphate western flag | 1 |
| Medium — university town; moderate emirate influence persists | 1 |
| Medium — proximate to emirate seat; strong traditional reach | 1 |
| Medium — district head mediates in distant LGA from seat | 1 |
| Medium — emirate authority in Kainji Lake riverine district | 1 |
| Medium — chiefdom head administers mixed Dakarkari-Kambari area | 1 |
| Medium — district head channels emirate authority in riverine area | 1 |
| Medium — district head mediates in rural agricultural area | 1 |
| Medium — chiefdom head in remote banditry-affected area | 1 |
| High — direct emirate seat; riverine cultural and scholarly authority | 1 |
| High — direct emirate seat; multi-ethnic chiefdom council | 1 |
| High — paramount Ebira throne governs via clan district heads | 1 |
| Medium — Ebira paramount influence moderated by federal industrial zone | 1 |
| High — Attah authority cascades through district clan chiefs | 1 |
| High — Attah authority through clan heads in rural hinterland | 1 |
| High — major Igala population center under Attah's district chiefs | 1 |
| High — Attah authority strong but remoteness limits state reach | 1 |
| High — seat of Attah Igala; paramount traditional authority hub | 1 |
| High — Igalamela kingmakers hold ceremonial role in Attah selection | 1 |
| High — Olujumu chairs Ijumu Traditional Council of Okun Obas | 1 |
| High — Obaro chairs Okun Area Traditional Council statewide | 1 |
| High — Ohimegye governs Bassa Nge kingdom via hereditary chiefs | 1 |
| Medium — Maigari role largely ceremonial in multi-ethnic state capital | 1 |
| High — Elulu chairs Mopamuro Traditional Council of Okun chiefs | 1 |
| High — Attah authority through district and clan heads | 1 |
| Medium — dual community structures; Olu Magongo stool disputed since 2024 | 1 |
| High — Ohinoyi paramount authority via Ebira clan system | 1 |
| High — seat of Ohinoyi; paramount Ebira traditional authority | 1 |
| High — Attah authority strong in remote agrarian Igala area | 1 |
| High — Attah authority via local Onu chiefs and clan heads | 1 |
| High — Agbana chairs Yagba East Traditional Council | 1 |
| High — Elegbe chairs Yagba West Traditional Council | 1 |
| High — emirate district heads govern peri-urban areas | 1 |
| Medium — authority shared among four Borgu district emirs | 1 |
| High — Nupe emirate authority over rural communities | 1 |
| Low — multiple small-town Obas with limited joint authority | 1 |
| Medium — senior Oba among several Igbomina rulers | 1 |
| High — paramount emirate seat; very strong political influence | 1 |
| Medium — foremost Igbomina Oba with consultative authority | 1 |
| Low — small rural LGA with limited Oba jurisdiction | 1 |
| High — Borgu emirate with strong community authority | 1 |
| High — emirate district heads administer rural areas | 1 |
| High — 1st Class Oba; paramount Ibolo Kingdom ruler | 1 |
| Medium — local Oba with community advisory role | 1 |
| Medium — local Yoruba Oba within Offa sphere of influence | 1 |
| High — 1st Class Nupe emirate; vice-chair traditional council | 1 |
| Low — migrants vastly outnumber Awori indigenes | 1 |
| Low — extremely diverse migrant settlement area | 1 |
| Low — massive migrant population, fragmented authority | 1 |
| Low — Festac/Satellite Town migrant-dominated | 1 |
| Low — commercial port zone, few indigenes remain | 1 |
| Medium — strong Egun/Ogu indigenous community | 1 |
| Medium — strong indigenous fishing community presence | 1 |
| Medium — influential in land and development matters | 1 |
| Medium — active amid rapid Lekki corridor development | 1 |
| Low — suburban area, Egba settlers predominate | 1 |
| Medium — state capital, strong Awori cultural presence | 1 |
| Medium — strong Ijebu community, growing peri-urban | 1 |
| Low — urbanised, migrants outnumber Awori indigenes | 1 |
| Medium — paramount Oba, political counsel sought | 1 |
| Low — cosmopolitan area, Awori minority now | 1 |
| Low — dense migrant population overwhelms indigenes | 1 |
| Low — some Awori indigenous presence persists | 1 |
| Low — industrial/commercial, mostly migrant residents | 1 |
| Low — dense migrant settlement, limited influence | 1 |
| Low — no indigenous community, entirely settlers | 1 |
| Medium — ethnic chief, respected but contested historically | 1 |
| High — emirate tradition, rural area limits scope | 1 |
| Medium — Alago chief, socially active and respected | 1 |
| Medium — multi-ethnic peri-urban, diluted by growth | 1 |
| Medium — traditional Alago authority, remote area | 1 |
| High — historic emirate, strong political connections | 1 |
| Medium — Gwandara chief, recently elevated first class | 1 |
| High — chairs State Council, top Muslim leader | 1 |
| High — historic emirate, deep-rooted political influence | 1 |
| Medium — commands strong Eggon ethnic loyalty | 1 |
| Medium — fragmented, two first class stools in LGA | 1 |
| Medium — Egbura chief, 30 yrs on throne, respected | 1 |
| Medium — Rindre chief, rural, socially respected | 1 |
| High — first-class emir with direct emirate authority | 1 |
| High — Borgu Emirate covers Agwara; remote area | 1 |
| High — paramount Nupe ruler, chairs state council | 1 |
| High — first-class emir over Borgu/Bariba area | 1 |
| High — Minna Emirate peri-urban area, FUT campus | 1 |
| High — emirate seat in state capital Minna | 1 |
| High — Bida Emirate domain; carved from Lavun | 1 |
| High — Nupe heartland near Bida city | 1 |
| Medium — Gbagyi area; emirate influence moderate | 1 |
| High — Nupe area carved from Gbako LGA | 1 |
| High — powerful first-class emir, major town | 1 |
| High — first-class emir; LGA adjoins FCT | 1 |
| High — Bida Emirate; Nupe heartland | 1 |
| High — Kontagora Kingdom territory; Kambari area | 1 |
| High — old Kontagora domain; banditry-affected | 1 |
| High — carved from Wushishi; Kontagora domain | 1 |
| High — Nupe area on major A1 highway | 1 |
| Medium — Gwari area; insecurity reduces influence | 1 |
| Medium — Gbagyi area; emirate-Gbagyi dynamics mixed | 1 |
| High — first-class emirate stool at Kagara | 1 |
| Medium — Dukawa/Kambari area; remote influence | 1 |
| Medium — Gwari/Kadara area; severe banditry zone | 1 |
| High — first-class emir; urban Abuja-adjacent | 1 |
| Medium — peri-urban Abuja corridor; mixed population | 1 |
| Medium — Wushishi chiefdom under Kontagora emirate | 1 |
| High — convenes Egba consensus, shapes state elections | 1 |
| High — paramount Egba seat, directs political alignment | 1 |
| Medium — chairs Awori Obas Forum, no formal council | 1 |
| High — Alake endorsement sways local voter turnout | 1 |
| High — Alake covers Egba south, peri-urban bloc | 1 |
| Medium — interregnum limits coordination in rural zone | 1 |
| Medium — Awujale vacancy; local Obas fill political gap | 1 |
| Low — vacant throne plus rural setting, minimal reach | 1 |
| High — Awujale seat; institutional weight persists | 1 |
| Medium — Remo paramount; moderate election influence | 1 |
| Medium — Yewa paramount; border area dilutes reach | 1 |
| Medium — Yewa paramount; border trade area influence | 1 |
| High — Alake endorsement sways expressway-corridor voters | 1 |
| High — Alake covers Egba north; rural dampens pull | 1 |
| Medium — Awujale interregnum; Dagburewe fills local gap | 1 |
| Low — remote riverine; vacant throne, minimal reach | 1 |
| Medium — Remo paramount; rural limits direct reach | 1 |
| Medium — Remo paramount seat; shapes local politics | 1 |
| Medium — Yewa paramount; rural north, moderate sway | 1 |
| Medium — Yewa paramount seat; local political weight | 1 |
| Medium — first-class Oba; authority contested by Owa-Ale | 1 |
| Low — four co-equal monarchs; fragmented authority | 1 |
| Low — small rural LGA; limited political mobilisation | 1 |
| Medium — veteran first-class Oba; state-level recognition | 1 |
| Medium — state capital throne; claims three-LGA domain | 1 |
| Medium — Deji paramount seat; chairs Council of Obas | 1 |
| Medium — Ijaw paramount; ethnic bloc electoral leverage | 1 |
| Medium — first-class throne vacant; succession pending | 1 |
| Low — jurisdiction contested by Deji; limited scope | 1 |
| Medium — wealthiest Nigerian monarch; patronage network | 1 |
| Low — secondary throne; limited state-level influence | 1 |
| Low — contested with Abodi of Ikale; fragmented pull | 1 |
| Low — dual kingdoms in LGA; transit town dilutes pull | 1 |
| Low — highly disputed paramountcy; court challenges | 1 |
| Medium — ancient throne; rural fringe of Ondo Kingdom | 1 |
| Medium — Ondo paramount seat; 500-year-old kingdom | 1 |
| Low — Oba murdered 2020; five-year vacuum erodes pull | 1 |
| Medium — premier Yoruba throne; historical political weight | 1 |
| Low — secondary throne; limited electoral mobilisation | 1 |
| Medium — Iwo zone paramount; vocal political actor | 1 |
| Medium — newly installed 2024; Ijesa bloc shapes elections | 1 |
| Medium — Ijesa paramount covers area; rural dampens pull | 1 |
| Low — independent local throne; rural, limited influence | 1 |
| Medium — deputy chair Council of Obas; conflict mediator | 1 |
| Medium — ancient Oyo-era throne; Ede political broker | 1 |
| Medium — Timi jurisdiction covers both Ede LGAs | 1 |
| Low — stool contested; peri-urban Osogbo satellite area | 1 |
| Medium — 52 years on throne; commands deep local loyalty | 1 |
| High — foremost Yoruba throne; national political broker | 1 |
| High — Ooni domain; Modakeke peri-urban expansion zone | 1 |
| High — Ooni covers Ife North; university town presence | 1 |
| High — Ooni domain; rural setting reduces direct pull | 1 |
| Low — smallest Osun LGA; remote Igbomina throne | 1 |
| Low — vacant since 2021; political vacuum near Osogbo | 1 |
| Medium — premier Igbomina throne; historical political weight | 1 |
| Medium — paramount Ijesa seat; bloc electoral influence | 1 |
| Medium — Ijesa paramount; co-urban with Ilesa East | 1 |
| Medium — 50-plus years on throne; mediates communal disputes | 1 |
| Medium — transit-town Oba; contested but locally powerful | 1 |
| Low — small ancient town; limited political mobilisation | 1 |
| Medium — Iwo paramount seat; outspoken political actor | 1 |
| Medium — Ijesa paramount zone; Ibokun is vassal town | 1 |
| Low — local crown Oba; university town, limited reach | 1 |
| Medium — Iwo zone paramount; rural dampens influence | 1 |
| Medium — state capital Oba; UNESCO festival prestige | 1 |
| Medium — Ijesa zone; Elegboro of Ijebu-Jesa is local | 1 |
| Low — local Oba embroiled in communal land disputes | 1 |
| Medium — state capital paramount; peace committee chair | 1 |
| Medium — rotating local Oba council; land and dispute arbitration | 1 |
| High — Olubadan chieftaincy hierarchy governs peri-urban Ibadan | 1 |
| High — imperial Oyo heritage; apex Yoruba throne mediates | 1 |
| Low — remote LGA; Okere chairs Oke-Ogun traditional council | 1 |
| High — Olubadan chieftaincy hierarchy extends to Egbeda zone | 1 |
| High — direct Olubadan authority over urban Ibadan core | 1 |
| High — direct Olubadan authority; most populous Oyo LGA | 1 |
| High — direct Olubadan authority; Bodija/university zone | 1 |
| High — Olubadan palace zone; historic Mapo Hall core | 1 |
| High — direct Olubadan authority; dense residential zone | 1 |
| Medium — community arbitration and land allocation in Ibarapa | 1 |
| Medium — Ibarapa zone HQ; community dispute mediation role | 1 |
| Medium — security-crisis prominence; community cohesion role | 1 |
| Medium — Olubadan influence; rural Ibadan fringe area | 1 |
| Medium — historic northern Oke-Ogun throne; community mediation | 1 |
| Medium — Oke-Ogun capital; historic textile-economy throne | 1 |
| Low — local Oba; limited state-level political influence | 1 |
| Low — local throne; limited influence beyond community level | 1 |
| Medium — leads eight-town Kajola traditional council | 1 |
| High — Olubadan chieftaincy hierarchy; peri-urban Ibadan belt | 1 |
| High — paramount Ogbomoso ruler; state council co-chair | 1 |
| Medium — ancient Oduduwa-crowned throne; Ijeru domain head | 1 |
| Medium — Soun influence extends; shared with Onpetu zone | 1 |
| Low — remote Oke-Ogun LGA; local community arbitration only | 1 |
| High — Olubadan authority; suburban Ibadan industrial zone | 1 |
| High — Olubadan hierarchy; peri-urban land administration | 1 |
| Medium — old Oyo Empire capital site; community mediation | 1 |
| Medium — one of five original Oyo Empire crowned Obas | 1 |
| High — Alaafin domain extends across Oyo town environs | 1 |
| High — Alaafin palace in Oyo town; direct royal authority | 1 |
| Low — rural Saki hinterland; Okere indirect influence | 1 |
| Medium — Oke-Ogun traditional council chair; border commerce | 1 |
| Medium — ancient Oyo Empire second-rank throne; active voice | 1 |
| Medium — Gbong Gwom paramount but conflict weakens enforcement | 1 |
| Low — fragmented multi-ethnic authority; Irigwe/Rukuba competing | 1 |
| Medium — authority present but severe herder-farmer conflict | 1 |
| Medium — unified Izere authority; insecurity moderates influence | 1 |
| High — multiple first-class chiefs; urban cosmopolitan base | 1 |
| High — paramount ruler chairs state traditional council | 1 |
| Medium — emirate structure with cross-ethnic Muslim leadership | 1 |
| Medium — newly installed paramount ruler rebuilding authority | 1 |
| Low — stool vacant since Bali death; sub-chiefs dispute | 1 |
| Low — paramount stool vacant; authority dispersed among sub-chiefs | 1 |
| Medium — active council but periphery conflict with herders | 1 |
| Medium — small Tehl/Youm ethnic authority in remote area | 1 |
| High — first-class chief over Ngas majority trade hub | 1 |
| Medium — Pan/Pyem authority; multiple sub-groups in hilly terrain | 1 |
| Medium — newly elevated first-class; severe conflict constraints | 1 |
| High — well-established paramount ruler; peacemaker role | 1 |
| High — strong emirate authority; chairs Plateau Muslim community | 1 |
| Low — fragmented clan-based authority across four clans | 1 |
| Medium — Eze-based authority in Ekpeye heartland | 1 |
| Low — multiple autonomous Ekpeye/Engenni communities | 1 |
| Medium — Kalabari traditional system via Abonnema kingdom | 1 |
| Low — fragmented Obolo clans; remote riverine setting | 1 |
| Medium — historic Kalabari Kingdom seat at Buguma | 1 |
| High — historic Bonny Kingdom; NLNG economic hub | 1 |
| Medium — Kalabari-linked riverine traditional system | 1 |
| Medium — Eleme Kingdom council; refinery-zone prominence | 1 |
| Medium — strong Eze system in rural Ikwerre area | 1 |
| Medium — Ochie paramount with clan-head structure | 1 |
| Low — Ogoni fragmented; MOSOP activism legacy shapes politics | 1 |
| Medium — active Eze system in rural Ikwerre LGA | 1 |
| Low — Ogoni fragmented; Bori administrative center | 1 |
| Low — urban commercial hub; migrants outnumber indigenes | 1 |
| Medium — Eze Ogba paramount over Ogba; oil-producing zone | 1 |
| Low — small riverine LGA linked to Okrika kingdom | 1 |
| Medium — historic Okrika Kingdom with Amanyanabo system | 1 |
| Low — small rural LGA; Etche sub-group community | 1 |
| High — historic Opobo Kingdom; Jaja of Opobo lineage | 1 |
| Low — industrial/migrant area; mixed Igbo-Ndoki groups | 1 |
| Low — state capital metropolis; migrants dominate demographics | 1 |
| Low — Ogoni fragmented; oil-affected rural area | 1 |
| High — Emirate system guides dispute resolution and land access | 1 |
| High — Emirate authority central to community governance | 1 |
| High — Emirate system shapes politics and dispute resolution | 1 |
| High — Emirate authority central despite insecurity crisis | 1 |
| High — Emirate council dominates local governance norms | 1 |
| High — Sultan's emirate council dominates local governance | 1 |
| High — Sultan's palace and emirate council seat of power | 1 |
| High — Historic caliphate seat; emirate system deeply rooted | 1 |
| High — Emirate council controls local chieftaincy and land | 1 |
| Medium — Muri Emirate nominal; Mumuye chief locally active | 1 |
| Medium — Chief of Bali moderates diverse Chamba-Jibawa-Fulani area | 1 |
| Medium — Gara paramount among Chamba but Tiv tensions present | 1 |
| Medium — Lamdo first-class chief but remote terrain limits reach | 1 |
| Medium — Lamido and Muri Emirate share authority over LGA | 1 |
| Medium — Jukun chief active but herder-farmer tensions recurrent | 1 |
| Medium — Emir of Muri influential but state capital dilutes | 1 |
| Medium — Wurkum chief active but Karimjo-Fulani tensions persist | 1 |
| Low — fragmented ethnic groups with no paramount authority | 1 |
| Medium — Chief of Lau active under Muri Emirate influence | 1 |
| Low — fragmented highland communities, weak central authority | 1 |
| Medium — newly installed chief; Kuteb-Chamba succession tensions | 1 |
| Low — Kuteb local chiefs only; no separate paramount ruler | 1 |
| High — Aku Uka paramount over Jukun political affairs | 1 |
| Low — multiple small ethnic communities, no paramount chief | 1 |
| Medium — Kpanti first-class but Mumuye historically decentralized | 1 |
| High — Mai of Bade retains strong customary authority | 1 |
| Medium — state capital governance dilutes traditional authority | 1 |
| High — Fika Emirate council influential in local politics | 1 |
| Medium — Fune Emirate pluralistic, moderate local influence | 1 |
| Low — ISWAP attacks displaced rulers, authority disrupted | 1 |
| Low — insurgency destroyed governance, rulers displaced | 1 |
| Low — insurgency weakened traditional authority structures | 1 |
| Medium — district head under Bade Emirate, semi-urban hub | 1 |
| Medium — Tikau Emirate council, remote Manga Kanuri area | 1 |
| High — Mai Machina retains deep customary and cultural authority | 1 |
| Medium — Fika Emirate district head moderates local governance | 1 |
| High — Nguru Emirate retains strong trade-center authority | 1 |
| High — Fika and Potiskum Emirate councils very influential | 1 |
| Medium — Tikau Emirate council, remote Niger border area | 1 |
| Medium — Yusufari Emirate council, remote desert border area | 1 |
| High — Emir of Gusau influential in state capital politics | 1 |


### `Tertiary Institution Present`

Unique values: **2** | Nulls: **0**

| Value | Count |
|-------|-------|
| N | 447 |
| Y | 327 |


### `Predominant Land Tenure`

Unique values: **89** | Nulls: **0**

| Value | Count |
|-------|-------|
| Emirate customary tenure under Land Use Act | 203 |
| Community/customary tenure | 161 |
| Mixed: customary rural / state leasehold urban | 56 |
| Community/customary tenure under Land Use Act | 48 |
| community/customary tenure | 32 |
| State leasehold / Certificate of Occupancy | 31 |
| community/customary tenure under Land Use Act | 30 |
| Customary communal tenure under Land Use Act | 18 |
| mixed: customary rural / state leasehold urban | 15 |
| Community/customary land tenure system predominant | 14 |
| Mixed: customary / state leasehold urban | 10 |
| Emirate customary tenure, largely disrupted by conflict | 9 |
| Emirate customary tenure, partially disrupted | 9 |
| mixed: customary / state leasehold urban | 8 |
| FCT federal leasehold | 6 |
| Community/customary tenure, fishing rights | 5 |
| Community/customary tenure, oil-company impact | 5 |
| Community/customary riverine tenure | 5 |
| Customary tenure disrupted by insurgency displacement | 5 |
| Mixed: state leasehold urban / emirate customary rural | 4 |
| Mixed: state leasehold urban / customary tenure rural | 4 |
| Chamba customary tenure under Land Use Act | 3 |
| Mixed: customary and emirate tenure | 3 |
| Mixed: customary / state leasehold peri-urban | 3 |
| community/customary tenure; oil-producing area | 3 |
| community/customary riverine tenure | 3 |
| Mixed: state leasehold urban / emirate customary peri-urban | 3 |
| Mixed: emirate customary and state leasehold | 2 |
| Community/customary tenure, conflict-disrupted | 2 |
| Community/customary tenure; oil-lease overlays | 2 |
| Mixed: customary rural / statutory urban | 2 |
| Customary dominant; some statutory in town | 2 |
| Community/customary tenure; Igede patrilineal | 2 |
| Mixed: customary / state leasehold | 2 |
| Community/customary tenure; some oil lease overlays | 2 |
| Mixed: customary rural / statutory elements in town | 2 |
| Mixed: customary rural / state leasehold urban areas | 2 |
| State leasehold / C of O; some customary | 2 |
| Mixed: state leasehold urban / customary peri-urban | 2 |
| Community/customary Remo tenure | 2 |
| mixed: customary rural / state leasehold semi-urban | 2 |
| customary tenure with emirate/caliphate elements | 2 |
| community/customary tenure; oil-affected area | 2 |
| Mixed: customary communal / institutional land | 1 |
| Mixed: customary / emerging urban leasehold | 1 |
| Bachama customary tenure under Land Use Act | 1 |
| Mixed: emirate and customary tenure | 1 |
| Mixed: Bachama customary and state leasehold | 1 |
| Mixed: state leasehold and emirate customary | 1 |
| Mixed: customary / oil-company leasehold impact | 1 |
| Mixed: customary rural / semi-urban leasehold | 1 |
| Mixed: emirate customary / semi-urban leasehold | 1 |
| Mixed: emirate customary / statutory urban | 1 |
| Community/customary; some state leasehold | 1 |
| Disputed: customary tenure affected by ICJ ruling | 1 |
| Mixed: customary rural / state leasehold in Onueke | 1 |
| mixed: customary / some state leasehold | 1 |
| Tangale customary communal tenure under Land Use Act | 1 |
| State leasehold and C-of-O in urban areas | 1 |
| Community/customary tenure; some statutory near Owerri | 1 |
| Mixed: customary rural / some statutory peri-urban | 1 |
| Community/customary tenure; marginal oil lease presence | 1 |
| Customary tenure predominant; oil lease overlays present | 1 |
| Customary tenure; oil/gas lease overlays present | 1 |
| Community/customary tenure; marginal oil lease areas | 1 |
| Mixed: customary elements / state leasehold predominant | 1 |
| State leasehold and C-of-O in urban Dutse core | 1 |
| Emirate customary tenure; semi-urban C-of-O emerging | 1 |
| Mixed: state leasehold urban / customary rural | 1 |
| Mixed: emirate customary / state leasehold peri-urban | 1 |
| State leasehold / C of O; peri-urban customary | 1 |
| State leasehold / C of O; Idejo customary pockets | 1 |
| Community/customary; some state leasehold in town | 1 |
| Mixed: customary rural / some state leasehold | 1 |
| Mixed: customary / state leasehold industrial | 1 |
| Mixed: customary / state leasehold transitional | 1 |
| Mixed: customary / commercial transitional | 1 |
| Community/customary Ijebu tenure | 1 |
| community/customary tenure; fishing-based | 1 |
| customary/community; NLNG industrial leasehold | 1 |
| customary tenure; oil-refinery impact zone | 1 |
| customary tenure; airport impact zone | 1 |
| customary tenure; major oil-producing area | 1 |
| community/customary fishing-based tenure | 1 |
| community/customary; oil-affected riverine | 1 |
| mixed: customary / state industrial leasehold | 1 |
| Mixed: emirate customary and Mumuye community tenure | 1 |
| Mixed: community customary and Jukun traditional tenure | 1 |
| Mixed: community customary and emirate tenure | 1 |

**Potential spelling/capitalization variants:**
  - ['Mixed: customary rural / state leasehold urban', 'mixed: customary rural / state leasehold urban']
  - ['Community/customary tenure', 'community/customary tenure']
  - ['Community/customary tenure under Land Use Act', 'community/customary tenure under Land Use Act']
  - ['Mixed: customary / state leasehold urban', 'mixed: customary / state leasehold urban']
  - ['Community/customary riverine tenure', 'community/customary riverine tenure']

### `Major Urban Center`

Unique values: **751** | Nulls: **1**

| Value | Count |
|-------|-------|
| Kano | 8 |
| Enugu | 3 |
| Itu | 2 |
| Azare | 2 |
| Kaiama | 2 |
| Calabar | 2 |
| Aboh | 2 |
| Koko | 2 |
| Kaduna | 2 |
| Zaria | 2 |
| Minna | 2 |
| Abeokuta | 2 |
| Ede | 2 |
| Ilesa | 2 |
| Sokoto city | 2 |
| Eziama | 1 |
| Aba | 1 |
| Arochukwu | 1 |
| Bende | 1 |
| Isiala Oboro | 1 |
| Isiala Ngwa | 1 |
| Omoba | 1 |
| Mbalano | 1 |
| Mgboko | 1 |
| Amaekpu Ohafia | 1 |
| Osisioma | 1 |
| Ugwunagbo | 1 |
| Akwete | 1 |
| Oke Ikpe | 1 |
| Nwoagu Isuochi | 1 |
| Umuahia | 1 |
| Apumiri | 1 |
| Demsa | 1 |
| Fufore | 1 |
| Ganye | 1 |
| *(null)* | 1 |
| Gombi | 1 |
| Gayuk | 1 |
| Hong | 1 |
| Jada | 1 |
| Lamurde | 1 |
| Gulak | 1 |
| Maiha | 1 |
| Mayo-Belwa | 1 |
| Michika | 1 |
| Mubi | 1 |
| Gella | 1 |
| Numan | 1 |
| Shelleng | 1 |
| Song | 1 |
| Toungo | 1 |
| Jimeta | 1 |
| Yola Town | 1 |
| Abak | 1 |
| Okoroete | 1 |
| Eket | 1 |
| Uquo | 1 |
| Afaha Ikot Ebak | 1 |
| Utu Etim Ekpo | 1 |
| Etinan | 1 |
| Upenekang | 1 |
| Nung Udoe | 1 |
| Oko Ita | 1 |
| Urua Inyang | 1 |
| Ibiaku Ntok Okpo | 1 |
| Ikot Abasi | 1 |
| Ikot Ekpene | 1 |
| Odoro Ikpe | 1 |
| Enwang | 1 |
| Mkpat Enin | 1 |
| Odot Afaha | 1 |
| Afaha Offiong | 1 |
| Ikot Edibon | 1 |
| Nto Edino | 1 |
| Okopedi | 1 |
| Abat | 1 |
| Oron | 1 |
| Ikot Ibritam | 1 |
| Eyofin | 1 |
| Ikot Akpa Nkuk | 1 |
| Idu | 1 |
| Urue Offong | 1 |
| Uyo | 1 |
| Ekwulobia | 1 |
| Otuocha | 1 |
| Nzam | 1 |
| Neni | 1 |
| Achalla | 1 |
| Awka | 1 |
| Anaku | 1 |
| Ukpo | 1 |
| Ozubulu | 1 |
| Ogidi | 1 |
| Ojoto | 1 |
| Ihiala | 1 |
| Abagana | 1 |
| Nnewi | 1 |
| Ukpor | 1 |
| Atani | 1 |
| Onitsha | 1 |
| Fegge | 1 |
| Ajalli | 1 |
| Umunze | 1 |
| Nteje | 1 |
| Alkaleri | 1 |
| Bauchi | 1 |
| Bogoro | 1 |
| Dambam | 1 |
| Darazo | 1 |
| Dass | 1 |
| Gamawa | 1 |
| Kafin Madaki | 1 |
| Giade | 1 |
| Itas | 1 |
| Jama'are | 1 |
| Kirfi | 1 |
| Misau | 1 |
| Ningi | 1 |
| Yana | 1 |
| Bununu | 1 |
| Toro | 1 |
| Warji | 1 |
| Katagum | 1 |
| Twon-Brass | 1 |
| Ekeremor | 1 |
| Nembe | 1 |
| Ogbia Town | 1 |
| Sagbama | 1 |
| Oporoma | 1 |
| Yenagoa | 1 |
| Igumale | 1 |
| Obagaji | 1 |
| Ugbokpo | 1 |
| Buruku | 1 |
| Gboko | 1 |
| Gbajimba | 1 |
| Aliade | 1 |
| Naka | 1 |
| Katsina-Ala | 1 |
| Tse-Agberagba | 1 |
| Adikpo | 1 |
| Ugba | 1 |
| Makurdi | 1 |
| Obarike-Ito | 1 |
| Otukpa | 1 |
| Idekpa | 1 |
| Oju | 1 |
| Okpoga | 1 |
| Otukpo | 1 |
| Wannune | 1 |
| Zaki-Biam | 1 |
| Lessel | 1 |
| Vandeikya | 1 |
| Mallam Fatori | 1 |
| Askira | 1 |
| Bama | 1 |
| Fikayel | 1 |
| Biu | 1 |
| Chibok | 1 |
| Damboa | 1 |
| Dikwa | 1 |
| Gubio | 1 |
| Gudumbali | 1 |
| Gwoza | 1 |
| Khaddamari | 1 |
| Benisheikh | 1 |
| Rann | 1 |
| Konduga | 1 |
| Baga | 1 |
| Kwaya Kusar | 1 |
| Mafa | 1 |
| Magumeri | 1 |
| Maiduguri | 1 |
| Marte | 1 |
| Damasak | 1 |
| Monguno | 1 |
| Gamboru-Ngala | 1 |
| Gajiram | 1 |
| Shani | 1 |
| Itigidi | 1 |
| Akamkpa | 1 |
| Ikot Nakanda | 1 |
| Ikang | 1 |
| Abuochiche | 1 |
| Akpet Central | 1 |
| Boje | 1 |
| Effraya | 1 |
| Ikom | 1 |
| Sankwala | 1 |
| Obubra | 1 |
| Obudu | 1 |
| Odukpani | 1 |
| Ogoja | 1 |
| Ugep | 1 |
| Okpoma | 1 |
| Issele-Uku | 1 |
| Ogwashi-Uku | 1 |
| Bomadi | 1 |
| Burutu | 1 |
| Isiokolo | 1 |
| Oghara | 1 |
| Agbor | 1 |
| Owa-Oyibu | 1 |
| Ozoro | 1 |
| Oleh | 1 |
| Kwale | 1 |
| Orerokpe | 1 |
| Akwukwu-Igbo | 1 |
| Asaba | 1 |
| Patani | 1 |
| Sapele | 1 |
| Ovwian-Aladja | 1 |
| Ughelli | 1 |
| Otu-Jeremi | 1 |
| Obiaruku | 1 |
| Effurun | 1 |
| Warri | 1 |
| Ogbe-Ijoh | 1 |
| Abakaliki | 1 |
| Afikpo | 1 |
| Edda | 1 |
| Ugbodo | 1 |
| Ebiaji | 1 |
| Onueke | 1 |
| Ndufu-Alike | 1 |
| Ezillo | 1 |
| Ishiagu | 1 |
| Iboko | 1 |
| Uburu | 1 |
| Ezzamgbo | 1 |
| Onicha | 1 |
| Igarra | 1 |
| Uselu | 1 |
| Irrua | 1 |
| Uromi | 1 |
| Ubiaja | 1 |
| Ekpoma | 1 |
| Fugar | 1 |
| Agenebode | 1 |
| Auchi | 1 |
| Igueben | 1 |
| Aduwawa | 1 |
| Benin City | 1 |
| Abudu | 1 |
| Okada | 1 |
| Iguobazuwa | 1 |
| Afuze | 1 |
| Sabongida-Ora | 1 |
| Ehor | 1 |
| Ado-Ekiti | 1 |
| Efon-Alaaye | 1 |
| Omuo-Ekiti | 1 |
| Ilawe-Ekiti | 1 |
| Aramoko-Ekiti | 1 |
| Emure-Ekiti | 1 |
| Ode-Ekiti | 1 |
| Ido-Ekiti | 1 |
| Ijero-Ekiti | 1 |
| Ikere-Ekiti | 1 |
| Ikole-Ekiti | 1 |
| Iye-Ekiti | 1 |
| Igede-Ekiti | 1 |
| Ise-Ekiti | 1 |
| Otun-Ekiti | 1 |
| Oye-Ekiti | 1 |
| Ndeaboh | 1 |
| Awgu | 1 |
| Aguobu-Owa | 1 |
| Ogbede | 1 |
| Enugu-Ezike | 1 |
| Ibagwa-Aka | 1 |
| Ikem | 1 |
| Amagunze | 1 |
| Agbani | 1 |
| Nsukka | 1 |
| Oji River | 1 |
| Obollo-Afor | 1 |
| Udi | 1 |
| Umulokpa | 1 |
| Abaji | 1 |
| Abuja | 1 |
| Kubwa | 1 |
| Gwagwalada | 1 |
| Kuje | 1 |
| Kwali | 1 |
| Kumo | 1 |
| Tallase | 1 |
| Billiri | 1 |
| Dukku | 1 |
| Bajoga | 1 |
| Gombe | 1 |
| Kaltungo | 1 |
| Mallam Sidi | 1 |
| Nafada | 1 |
| Boh | 1 |
| Deba | 1 |
| Ahiazu | 1 |
| Ehime | 1 |
| Urualla | 1 |
| Dikenafai | 1 |
| Isinweke | 1 |
| Iho | 1 |
| Umuelemai | 1 |
| Umundugba | 1 |
| Nwaorieubi | 1 |
| Umuneke | 1 |
| Nnenasa | 1 |
| Nkwerre | 1 |
| Amaigbo | 1 |
| Otoko | 1 |
| Oguta | 1 |
| Mmahu-Egbema | 1 |
| Okigwe | 1 |
| Okwe | 1 |
| Orlu | 1 |
| Awo-Idemili | 1 |
| Omuma | 1 |
| Mgbidi | 1 |
| Owerri | 1 |
| Orie Uratta | 1 |
| Umuguma | 1 |
| Auyo | 1 |
| Babura | 1 |
| Biriniwa | 1 |
| Birnin Kudu | 1 |
| Buji | 1 |
| Dutse | 1 |
| Gagarawa | 1 |
| Garki | 1 |
| Gumel | 1 |
| Guri | 1 |
| Gwaram | 1 |
| Gwiwa | 1 |
| Hadejia | 1 |
| Jahun | 1 |
| Kafin Hausa | 1 |
| Kaugama | 1 |
| Kazaure | 1 |
| Kiri Kasama | 1 |
| Kiyawa | 1 |
| Maigatari | 1 |
| Malam Madori | 1 |
| Miga | 1 |
| Ringim | 1 |
| Roni | 1 |
| Sule Tankarkar | 1 |
| Taura | 1 |
| Yankwashi | 1 |
| Birnin Gwari | 1 |
| Kujama | 1 |
| Giwa | 1 |
| Rigasa | 1 |
| Ikara | 1 |
| Kwoi | 1 |
| Kafanchan | 1 |
| Kachia | 1 |
| Kagarko | 1 |
| Kajuru | 1 |
| Kaura | 1 |
| Kauru | 1 |
| Kubau | 1 |
| Hunkuyi | 1 |
| Saminaka | 1 |
| Makarfi | 1 |
| Gwantu | 1 |
| Soba | 1 |
| Zonkwa | 1 |
| Ajingi | 1 |
| Albasu | 1 |
| Bagwai | 1 |
| Bebeji | 1 |
| Bichi | 1 |
| Bunkure | 1 |
| Dambatta | 1 |
| Dawakin Kudu | 1 |
| Dawakin Tofa | 1 |
| Riruwai | 1 |
| Zakirai | 1 |
| Garko | 1 |
| Garun Mallam | 1 |
| Gaya | 1 |
| Gezawa | 1 |
| Gwarzo | 1 |
| Kabo | 1 |
| Karaye | 1 |
| Kibiya | 1 |
| Kiru | 1 |
| Kunchi | 1 |
| Kura | 1 |
| Madobi | 1 |
| Makoda | 1 |
| Minjibir | 1 |
| Rano | 1 |
| Rimin Gado | 1 |
| Rogo | 1 |
| Shanono | 1 |
| Sumaila | 1 |
| Takai | 1 |
| Tofa | 1 |
| Tsanyawa | 1 |
| Tudun Wada | 1 |
| Warawa | 1 |
| Wudil | 1 |
| Bakori | 1 |
| Batagarawa | 1 |
| Batsari | 1 |
| Baure | 1 |
| Bindawa | 1 |
| Charanchi | 1 |
| Danmusa | 1 |
| Dandume | 1 |
| Danja | 1 |
| Daura | 1 |
| Dutsi | 1 |
| Dutsin-Ma | 1 |
| Faskari | 1 |
| Funtua | 1 |
| Ingawa | 1 |
| Jibia | 1 |
| Kafur | 1 |
| Kaita | 1 |
| Kankara | 1 |
| Kankia | 1 |
| Katsina | 1 |
| Kurfi | 1 |
| Kusada | 1 |
| Mai'Adua | 1 |
| Malumfashi | 1 |
| Mani | 1 |
| Mashi | 1 |
| Matazu | 1 |
| Musawa | 1 |
| Rimi | 1 |
| Sabuwa | 1 |
| Safana | 1 |
| Sandamu | 1 |
| Zango | 1 |
| Aleiro | 1 |
| Arewa Dandi | 1 |
| Argungu | 1 |
| Augie | 1 |
| Bagudo | 1 |
| Birnin Kebbi | 1 |
| Bunza | 1 |
| Dandi | 1 |
| Fakai | 1 |
| Gwandu | 1 |
| Jega | 1 |
| Kalgo | 1 |
| Maiyama | 1 |
| Ngaski | 1 |
| Sakaba | 1 |
| Shanga | 1 |
| Suru | 1 |
| Wasagu | 1 |
| Yelwa | 1 |
| Zuru | 1 |
| Ogaminana | 1 |
| Ajaokuta | 1 |
| Ankpa | 1 |
| Oguma | 1 |
| Dekina | 1 |
| Onyedega | 1 |
| Idah | 1 |
| Ajaka | 1 |
| Iyara | 1 |
| Kabba | 1 |
| Koton Karfe | 1 |
| Lokoja | 1 |
| Mopa | 1 |
| Ugwolawo | 1 |
| Ogori | 1 |
| Obangede | 1 |
| Okene | 1 |
| Okpo | 1 |
| Abejukolo | 1 |
| Isanlu | 1 |
| Odo Ere | 1 |
| Afon | 1 |
| Kosubosu | 1 |
| Lafiagi | 1 |
| Araromi-Opin | 1 |
| Share | 1 |
| Oke-Oyi | 1 |
| Fufu | 1 |
| Ilorin | 1 |
| Omu-Aran | 1 |
| Owu-Isin | 1 |
| Bode Saadu | 1 |
| Offa | 1 |
| Iloffa | 1 |
| Ilemona | 1 |
| Patigi | 1 |
| Agege | 1 |
| Ajegunle | 1 |
| Ikotun | 1 |
| Festac Town | 1 |
| Apapa | 1 |
| Badagry | 1 |
| Epe | 1 |
| Victoria Island | 1 |
| Ibeju | 1 |
| Ogba | 1 |
| Ikeja | 1 |
| Ikorodu | 1 |
| Ketu | 1 |
| Lagos Island | 1 |
| Yaba | 1 |
| Mushin | 1 |
| Ojo | 1 |
| Oshodi | 1 |
| Shomolu | 1 |
| Surulere | 1 |
| Akwanga | 1 |
| Awe | 1 |
| Doma | 1 |
| Mararaba | 1 |
| Keana | 1 |
| Keffi | 1 |
| Garaku | 1 |
| Lafia | 1 |
| Nasarawa Town | 1 |
| Nasarawa Eggon | 1 |
| Obi | 1 |
| Toto | 1 |
| Wamba | 1 |
| Agaie | 1 |
| Agwara | 1 |
| Bida | 1 |
| New Bussa | 1 |
| Enagi | 1 |
| Lemu | 1 |
| Gawu | 1 |
| Katcha | 1 |
| Kontagora | 1 |
| Lapai | 1 |
| Kutigi | 1 |
| Nasko | 1 |
| Bangi | 1 |
| Mashegu | 1 |
| Mokwa | 1 |
| Sarkin Pawa | 1 |
| Paiko | 1 |
| Kagara | 1 |
| Rijau | 1 |
| Kuta | 1 |
| Suleja | 1 |
| Sabon Wuse | 1 |
| Wushishi | 1 |
| Ota | 1 |
| Itori | 1 |
| Ifo | 1 |
| Ogbere | 1 |
| Ijebu-Igbo | 1 |
| Atan | 1 |
| Ijebu-Ode | 1 |
| Ikenne | 1 |
| Imeko | 1 |
| Ipokia | 1 |
| Mowe | 1 |
| Odeda | 1 |
| Odogbolu | 1 |
| Abigi | 1 |
| Isara-Remo | 1 |
| Sagamu | 1 |
| Ayetoro | 1 |
| Ilaro | 1 |
| Ikare-Akoko | 1 |
| Okeagbe | 1 |
| Isua-Akoko | 1 |
| Oka-Akoko | 1 |
| Iju-Itaogbolu | 1 |
| Akure | 1 |
| Igbekebo | 1 |
| Idanre | 1 |
| Igbara-Oke | 1 |
| Igbokoda | 1 |
| Ile-Oluji | 1 |
| Ode-Irele | 1 |
| Ore | 1 |
| Okitipupa | 1 |
| Bolorunduro | 1 |
| Ondo | 1 |
| Ifon | 1 |
| Owo | 1 |
| Gbongan | 1 |
| Ile Ogbo | 1 |
| Iperindo | 1 |
| Osu | 1 |
| Otan Aiyegbaju | 1 |
| Iragbiji | 1 |
| Awo | 1 |
| Ejigbo | 1 |
| Ile-Ife | 1 |
| Oke Ogbo | 1 |
| Ipetumodu | 1 |
| Ifetedo | 1 |
| Oke-Ila Orangun | 1 |
| Ikirun | 1 |
| Ila Orangun | 1 |
| Ilobu | 1 |
| Ikire | 1 |
| Apomu | 1 |
| Iwo | 1 |
| Ibokun | 1 |
| Okuku | 1 |
| Bode Osi | 1 |
| Igbona | 1 |
| Ijebu-Jesa | 1 |
| Ifon Osun | 1 |
| Osogbo | 1 |
| Jobele | 1 |
| Moniya | 1 |
| Ofa-Meta | 1 |
| Tede | 1 |
| Egbeda | 1 |
| Bodija | 1 |
| Iwo Road | 1 |
| Onireke | 1 |
| Mapo | 1 |
| Ring Road | 1 |
| Igbo-Ora | 1 |
| Eruwa | 1 |
| Ayete | 1 |
| Ido | 1 |
| Kishi | 1 |
| Iseyin | 1 |
| Otu | 1 |
| Iwere-Ile | 1 |
| Okeho | 1 |
| Iyana-Offa | 1 |
| Ogbomosho | 1 |
| Arowomole | 1 |
| Ajaawa | 1 |
| Igbeti | 1 |
| Oluyole | 1 |
| Akanran | 1 |
| Igboho | 1 |
| Ikoyi-Ile | 1 |
| Kosobo | 1 |
| Oyo | 1 |
| Ago-Amodu | 1 |
| Saki | 1 |
| Iresa-Adu | 1 |
| Barkin Ladi | 1 |
| Bassa | 1 |
| Bokkos | 1 |
| Angware | 1 |
| Jos | 1 |
| Bukuru | 1 |
| Dengi | 1 |
| Kwal | 1 |
| Langtang | 1 |
| Mabudi | 1 |
| Mangu | 1 |
| Tunkus | 1 |
| Pankshin | 1 |
| Namu | 1 |
| Riyom | 1 |
| Shendam | 1 |
| Wase | 1 |
| Abua | 1 |
| Ahoada | 1 |
| Akinima | 1 |
| Abonnema | 1 |
| Ngo | 1 |
| Buguma | 1 |
| Bonny | 1 |
| Degema | 1 |
| Nchia | 1 |
| Emohua | 1 |
| Okehi | 1 |
| Kpor | 1 |
| Isiokpo | 1 |
| Bori | 1 |
| Rumuodomaya | 1 |
| Omoku | 1 |
| Ogu | 1 |
| Okrika | 1 |
| Eberi | 1 |
| Opobo | 1 |
| Oyigbo | 1 |
| Port Harcourt | 1 |
| Sakpenwa | 1 |
| Binji town | 1 |
| Bodinga town | 1 |
| Dange town | 1 |
| Gada town | 1 |
| Goronyo town | 1 |
| Balle town | 1 |
| Gwadabawa town | 1 |
| Illela town | 1 |
| Isa town | 1 |
| Kebbe town | 1 |
| Kware town | 1 |
| Rabah town | 1 |
| Sabon Birni town | 1 |
| Shagari town | 1 |
| Silame town | 1 |
| Tambuwal town | 1 |
| Tangaza town | 1 |
| Tureta town | 1 |
| Wamakko town | 1 |
| Wurno town | 1 |
| Yabo town | 1 |
| Sunkani | 1 |
| Bali | 1 |
| Donga | 1 |
| Serti | 1 |
| Mutum Biyu | 1 |
| Ibi | 1 |
| Jalingo | 1 |
| Karim Lamido | 1 |
| Baissa | 1 |
| Lau | 1 |
| Gembu | 1 |
| Takum | 1 |
| Lissam | 1 |
| Wukari | 1 |
| Yorro | 1 |
| Zing | 1 |
| Gashua | 1 |
| Dapchi | 1 |
| Damaturu | 1 |
| Fika | 1 |
| Damagum | 1 |
| Geidam | 1 |
| Buni Yadi | 1 |
| Bara | 1 |
| Jakusko | 1 |
| Jajimaji | 1 |
| Machina | 1 |
| Nangere | 1 |
| Nguru | 1 |
| Potiskum | 1 |
| Babangida | 1 |
| Kanamma | 1 |
| Yusufari | 1 |
| Anka | 1 |
| Bakura | 1 |
| Birnin Magaji | 1 |
| Bukkuyum | 1 |
| Bungudu | 1 |
| Gummi | 1 |
| Gusau | 1 |
| Kaura Namoda | 1 |
| Maradun | 1 |
| Maru | 1 |
| Shinkafi | 1 |
| Talata Mafara | 1 |
| Tsafe | 1 |
| Zurmi | 1 |


---
## 7. Column Inventory

| Col Index | Column Name | Category (Row 1) | Data Type | Null Count |
|-----------|-------------|-------------------|-----------|------------|
| 0 | State | IDENTIFICATION | categorical/text | 0 |
| 1 | LGA Name | IDENTIFICATION | categorical/text | 0 |
| 2 | Colonial Era Region | IDENTIFICATION | categorical/text | 0 |
| 3 | Terrain Type | IDENTIFICATION | categorical/text | 0 |
| 4 | Estimated Population | DEMOGRAPHIC | numeric | 0 |
| 5 | Population Density per km2 | DEMOGRAPHIC | numeric | 0 |
| 6 | Median Age Estimate | DEMOGRAPHIC | numeric | 0 |
| 7 | % Population Under 30 | DEMOGRAPHIC | numeric | 0 |
| 8 | % Hausa | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 9 | % Fulani | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 10 | % Hausa Fulani Undiff | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 11 | % Yoruba | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 12 | % Igbo | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 13 | % Ijaw | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 14 | % Kanuri | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 15 | % Shuwa Arab | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 16 | % Tiv | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 17 | % Ibibio | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 18 | % Efik | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 19 | % Nupe | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 20 | % Edo Bini | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 21 | % Urhobo | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 22 | % Itsekiri | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 23 | % Isoko | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 24 | % Igala | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 25 | % Idoma | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 26 | % Berom | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 27 | % Angas | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 28 | % Jukun | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 29 | % Ebira | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 30 | % Gwari Gbagyi | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 31 | % Ogoni | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 32 | % Ekoi | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 33 | % Tarok Yergam | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 34 | % Bachama | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 35 | % Mumuye | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 36 | % Kuteb | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 37 | % Chamba | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 38 | % Kataf Atyap | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 39 | % Bajju | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 40 | % Ham Jaba | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 41 | % Marghi | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 42 | % Bura | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 43 | % Kilba Huba | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 44 | % Annang | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 45 | % Oron | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 46 | % Bolewa | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 47 | % Obolo | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 48 | % Koro | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 49 | % Eket | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 50 | % Karekare | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 51 | % Bassa | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 52 | % Gwandara | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 53 | % Yandang | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 54 | % Kamwe | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 55 | % Gade | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 56 | % Ngizim | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 57 | % Zabarmawa | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 58 | % Bariba | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 59 | % Bata | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 60 | % Ikwerre | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 61 | % Ngamo | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 62 | % Tuareg | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 63 | % Bade | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 64 | % Ichen | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 65 | % Yungur | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 66 | % Ganagana | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 67 | % Tangale | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 68 | % Agatu | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 69 | % Kamuku | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 70 | % Verre | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 71 | % Mboi | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 72 | % Lala | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 73 | % Gude | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 74 | % Waja | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 75 | % Tera | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 76 | % Kambari | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 77 | % Etche | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 78 | % Kona | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 79 | % Egun/Ogu | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 80 | % Koma | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 81 | % Pere | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 82 | % Lunguda | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 83 | % Fali | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 84 | % Pero | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 85 | % Kare-Kare | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 86 | % Duwai | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 87 | % Ndola | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 88 | % Samba | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 89 | % Wurkun | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 90 | % Igede | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 91 | % Pada | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 92 | % Naijin | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 93 | % Other | ETHNOLINGUISTIC COMPOSITION | numeric | 0 |
| 94 | % Muslim | RELIGIOUS COMPOSITION | numeric | 73 |
| 95 | % Christian | RELIGIOUS COMPOSITION | numeric | 0 |
| 96 | % Traditionalist | RELIGIOUS COMPOSITION | numeric | 0 |
| 97 | Religious Subtype Notes | RELIGIOUS COMPOSITION | categorical/text | 0 |
| 98 | Almajiri Prevalence | RELIGIOUS COMPOSITION | categorical/text | 308 |
| 99 | Major Urban Center | URBANIZATION | categorical/text | 1 |
| 100 | Urban Rural Split | URBANIZATION | categorical/text | 0 |
| 101 | Oil Producing | ECONOMIC | categorical/text | 0 |
| 102 | Dominant Livelihood | ECONOMIC | categorical/text | 0 |
| 103 | Resource Extraction Notes | ECONOMIC | categorical/text | 381 |
| 104 | Poverty Rate Pct | ECONOMIC | numeric | 0 |
| 105 | Unemployment Rate Pct | ECONOMIC | numeric | 0 |
| 106 | Youth Unemployment Rate Pct | ECONOMIC | numeric | 0 |
| 107 | Access Electricity Pct | ECONOMIC | numeric | 0 |
| 108 | Access Water Pct | ECONOMIC | numeric | 0 |
| 109 | Access Healthcare Pct | ECONOMIC | numeric | 0 |
| 110 | Road Infrastructure Quality | ECONOMIC | categorical/text | 0 |
| 111 | Market Access | ECONOMIC | categorical/text | 0 |
| 112 | Adult Literacy Rate Pct | EDUCATION | numeric | 0 |
| 113 | Male Literacy Rate Pct | EDUCATION | numeric | 0 |
| 114 | Female Literacy Rate Pct | EDUCATION | numeric | 0 |
| 115 | Primary Enrollment Pct | EDUCATION | numeric | 0 |
| 116 | Secondary Enrollment Pct | EDUCATION | numeric | 0 |
| 117 | Gender Parity Index | EDUCATION | numeric | 0 |
| 118 | Out of School Children Pct | EDUCATION | numeric | 0 |
| 119 | Num Secondary Schools | EDUCATION | numeric | 0 |
| 120 | Tertiary Institution Present | EDUCATION | categorical/text | 0 |
| 121 | Traditional Authority | POLITICAL STRUCTURE | categorical/text | 0 |
| 122 | Traditional Authority Influence | POLITICAL STRUCTURE | categorical/text | 0 |
| 123 | Predominant Land Tenure | POLITICAL STRUCTURE | categorical/text | 0 |
| 124 | Mobile Phone Penetration Pct | CONNECTIVITY | numeric | 0 |
| 125 | Internet Access Pct | CONNECTIVITY | numeric | 0 |
| 126 | Data Notes | DATA QUALITY | categorical/text | 0 |

---
## Summary

**Total issues found: 7**

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| WARNING | 3 |
| INFO | 3 |

### CRITICAL Issues

- **[Ethnicity Sums]** 318 of 774 rows (41.1%) have ethnicity percentages that do not sum to 100 (deviation > 1.0). Distribution: 215 rows sum under 99 (60 of those under 50%), 103 rows sum over 101 (56 of those over 105%). This indicates widespread missing or excess ethnic group allocations across many LGAs, particularly in the Middle Belt and ethnically fragmented states. **Action required: audit ethnic composition data for completeness before any downstream analysis.**

### WARNING Issues

- **[Religion Sums]** 73 rows with religion sum deviating >1.0 from 100. **Root cause: `% Muslim` column has 73 null values** concentrated in Oyo (33 LGAs), Rivers (23 LGAs), and Plateau (17 LGAs). The Christian + Traditionalist values are present but the missing Muslim percentage causes sums of 90-96%. These nulls likely represent intentional data gaps or failed imports.
- **[Numeric Validation]** Column "Median Age Estimate": 35 LGAs have values just below the 15.0 lower bound (values are 14.8-14.9). These are borderline and may be valid for very young populations in Northern Nigeria.
- **[Categorical]** Capitalization inconsistencies in `Dominant Livelihood` (8 variant pairs) and `Predominant Land Tenure` (5 variant pairs). Example: "Subsistence farming, pastoralism" vs "subsistence farming, pastoralism". **Action: normalize to consistent title case or lowercase.**

### INFO Issues

- **[Identification]** Dataset uses 4 Colonial Era Regions (Eastern, Mid-Western, Northern, Western) rather than 8 modern Administrative Zones. This is a design choice — the column is named "Colonial Era Region", not "Administrative Zone".
- **[Numeric Validation]** Column `% Muslim` has 73 null values (see Religion Sums above for details).
- **[Categorical]** Several columns from the audit checklist were not found in the dataset: Prestige Language, Housing Pressure, Net Migration Trend, Industrial Profile, Chinese Investment Presence, Automation Penetration, Rail Access, Planned City, BIC Activity Level, Al-Shahid Influence, Sharia Court Status. These may be planned for a later data phase or exist in a different sheet/file.

### Structural Health Summary

| Dimension | Status |
|-----------|--------|
| Row count (774 LGAs) | PASS |
| State coverage (36 + FCT) | PASS — all 37 match official counts exactly |
| No duplicate LGAs | PASS |
| ID columns non-null | PASS |
| Ethnicity sums = 100% | **FAIL** — 41% of rows deviate |
| Religion sums = 100% | **FAIL** — 73 rows (9.4%) have null Muslim % |
| Numeric ranges | PASS (35 borderline Median Age values) |
| No non-numeric contamination | PASS |
| Categorical consistency | Minor capitalization variants in 2 columns |
