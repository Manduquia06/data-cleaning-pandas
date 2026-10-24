# Shark incidents and protective surfwear

Data cleaning and exploratory analysis with Python and pandas.

This bootcamp project studies recorded surfing-related shark incidents to
identify locations and body-area mentions that could guide further research
into protective surfwear. It compares countries; state-level analysis is kept
as an exploratory table rather than an additional project scope.

## Questions

- Which countries have the most records in the selected sample?
- How do explicit fatal and no-injury labels differ from incident counts?
- Which body areas are mentioned, and does their distribution differ between
  the United States and Australia?

## Source and scope

The assignment identifies the source as the
[Global Shark Attack File incident log](https://www.sharkattackfile.net/incidentlog.htm).
The student's original Excel snapshot was named `GSAF5.xls`, with **7,125 rows
and 23 columns**. The supplied notebook does not record the download date.

The study selects **2006–2026 inclusive**, not the last five years. The saved
study was prepared in October 2026, so **2026 is incomplete**. A newer download
can produce different results. The exact Excel snapshot is not included in this
package; put it in `data/GSAF5.xls` to reproduce the analysis.

## Files

| File | Purpose |
|---|---|
| `shark_attack_analysis.ipynb` | Main notebook, explanations, tables and two plots |
| `cleaning.py` | Reusable cleaning functions and the main `clean_data` pipeline |
| `analysis.py` | Body-area summaries and plotting functions |
| `requirements.txt` | Runtime and notebook dependencies |
| `data/README.md` | Instructions for obtaining and placing the input snapshot |
| `figures/` | The two plots exported from the original notebook's saved outputs |

The notebook imports the `.py` files. Keep all three in the repository root.
Its saved outputs come from the original uploaded notebook; they were retained
as historical evidence, not presented as a fresh execution of the revised code.

## Run locally

Use Python 3.10 or newer and open a terminal in the repository root.

```bash
python -m pip install -r requirements.txt
python -m jupyterlab
```

Place the original Excel file at `data/GSAF5.xls`, open
`shark_attack_analysis.ipynb`, select the installed Python environment, then
restart the kernel and run all cells from top to bottom. In VS Code, select
that environment as the notebook kernel. A missing-file error means the source
snapshot still needs to be added; the notebook does not download data silently.

To use the complete cleaning pipeline independently:

```python
import pandas as pd
from cleaning import clean_data

raw = pd.read_excel("data/GSAF5.xls")
cleaned, audit = clean_data(raw, start_year=2006, end_year=2026)
print(audit)
```

## Cleaning decisions

1. **Select relevant columns.** Remove the eight columns after `Source`, then
   exclude `Location`, `Name`, `Fatal Y/N`, `Time`, `Species` and `Source` from
   the analytical table. Keep Date, Year, Type, Country, State, Activity, Sex,
   Age and Injury. Original data and intermediate copies preserve context.
2. **Inspect missing values.** Count nulls and percentages by column. The initial
   selected table has no entirely null rows. Missingness in one field is not
   treated as a reason to delete every incomplete row.
3. **Classify activity text.** Use lowercase, trimmed temporary strings and regex
   to identify likely board-surfing descriptions. Exclude other modalities and
   ambiguous descriptions using the original keyword rules. Keep original text.
   This is a heuristic selection, not a complete validated taxonomy.
4. **Convert and group ages.** Preserve `Age` and create `Age_numeric` with
   `pd.to_numeric(errors="coerce")`. Do not guess ages from ranges, decades or
   uncertain text. Use groups 0–12, 13–17, 18–29, 30–44, 45–59 and 60+.
   Missing and out-of-range values (outside the working 0–120 range) are flagged.
   The project excludes these records, including from geographical comparisons.
5. **Filter the period.** Convert Year to numbers and retain 2006–2026 inclusively.
   Date has mixed formats and is not fully parsed; no month or seasonal analysis
   is claimed.
6. **Normalize geography.** Trim text, standardize country case, expand NSW and
   WA within Australia, correct the reviewed Hawaii/Maui row to USA/Hawaii,
   unify Reunion Island with Reunion and Scotland with United Kingdom, and
   normalize reviewed Saint-Leu/Saint-Gilles spelling variants. Keep
   Saint-Gilles-les-Bains distinct. Country includes both countries and some
   separately reported territories; State includes mixed geographic levels.
7. **Flag injury descriptions provisionally.** Only the exact normalized text
   `fatal` is labeled `Fatal reported`. Explicit no-injury phrases are labeled
   `No injury reported`. All remaining records stay in `Review`.
8. **Extract body-area mentions.** Use keyword groups, exclude records flagged
   as reporting no injury, and allow multiple areas per record. Percentages use
   all selected records in each country, including records without an identified
   body area, as their denominator.

No duplicate removal, sex-category normalization, missing-age imputation or
complete clinical severity classification is claimed. The source uses recorded
incidents; multiple-person descriptions and duplicate reports have not been
systematically reconciled, so counts should be described as records, not unique
individuals or independently verified events.

## Recorded selection results

These figures are from the supplied notebook's saved outputs, not a new run.

| Selection stage | Records |
|---|---:|
| Original snapshot | 7,125 |
| Likely surfing | 1,222 |
| Usable age | 945 |
| Period 2006–2026 | 495 |

Of the surfing records, **277 (22.7%)** were excluded because their ages were
missing, unrecognized or flagged. Age-group frequencies from the 945-record
historical subset must not be presented as the profile of the 495 recent-period
records without recalculation. Age groups do not determine clothing sizes.

## Main findings

The United States has **286 records** and Australia **129**: together **83.8%**
of the 495 selected records. Exploratory locations include Florida (176),
New South Wales (77), Hawaii (38) and California (34). One record has no country.

The provisional injury classification contains **30 explicit fatal labels**,
**61 explicit no-injury descriptions**, and **404 records under review**.
Australia has 15 explicit fatal labels and the United States has 4. These are
not complete mortality estimates, and Review does not mean minor or nonfatal.

| Body area | Records mentioning the area |
|---|---:|
| Feet / ankles | 176 |
| Legs | 142 |
| Hands / wrists | 63 |
| Arms / shoulders | 44 |
| Torso | 13 |
| Head / neck | 5 |

| Country | Feet / ankles | Legs |
|---|---:|---:|
| USA | 137 (47.9%) | 64 (22.4%) |
| Australia | 24 (18.6%) | 45 (34.9%) |

These patterns motivate investigation of foot/ankle protection in the USA and
leg coverage in Australia. They do not establish individual risk, product
effectiveness, current market demand or sales potential.

The following plots are exported from the student's original saved outputs:

![Selected records by country](figures/country_counts.png)

![Body-area mention percentages](figures/body_area_comparison.png)

## Limitations and validation

- Age exclusion and heuristic activity selection can change country comparisons.
- The text rules can miss synonyms, negations and complex narratives; body-area
  mentions are not clinically confirmed injury or severity categories.
- Fatal labels are intentionally narrow and do not recover every fatal outcome.
  `Fatal Y/N` would need to be restored and checked for a mortality study.
- Countries have different recording coverage and surfing exposure. No exposure
  denominator or market-demand dataset is available.
- Small country samples do not support broad population conclusions.
- 2026 is incomplete, geographic levels are mixed, and dates remain heterogeneous.
- Code syntax, boundary cases and equivalence with the original workflow were
  checked on representative synthetic records. The revised notebook was also
  smoke-executed on a temporary synthetic Excel file. The original 495-row
  result could not be freshly reproduced because the source Excel was not
  supplied. Synthetic data are not included as project evidence.

## Presentation and submission

**Presentation URL: pending — add the actual slide link before submission.**

The repository is intended to be named `data-cleaning-pandas`. Include the
notebook, both `.py` modules and this README. Add the necessary input snapshot
or document how reviewers can obtain the exact version. The presentation and
its URL still need to be completed; this repository package is not a claim that
all course submission requirements have already been fulfilled.
