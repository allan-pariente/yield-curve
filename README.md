# Yield Curve Analysis

## Overview

This project focuses on the **construction, cleaning, reconciliation, transformation and analysis of interest rate yield curves**, from raw public data to a reproducible dashboard.

The main objective is not to build a complex predictive model, but to demonstrate the importance of **high-quality financial data**, robust multi-source reconciliation, and clear visualization.

The project compares yield curves across developed markets (**United States and the Euro Area**) and emerging markets (**Mexico and India**), transforms par yields into **zero-coupon rates using bootstrapping**, and studies how the term structure evolves over time and across market regimes.

---

## Research Question

> How can we reconstruct clean and comparable zero-coupon yield curves from heterogeneous public data sources (US, EU, MX, IN), and what can their evolution tell us about market regimes, yield curve inversions, developed vs. emerging market spreads, and recession periods?

---
## Where the data work actually is

The raw rate series (FRED, US Treasury, ECB) are individually clean. The real data difficulty in this project is **not scrubbing dirty values, it is reconciling heterogeneous sources**. This reconciliation is the core contribution and is treated as a first-class part of the project, not as preprocessing.

Concretely, the project performs several non-trivial joins and harmonizations:

* **Maturity-grid alignment**: each source exposes a different set of maturities (for example DGS1MO to DGS30 on FRED, a distinct grid on the ECB side). Aligning them onto a common grid is a join on maturity plus interpolation.
* **Calendar and frequency alignment**: US and Euro Area trading calendars and public holidays differ. Furthermore, emerging market data is often published at a monthly frequency, requiring strict temporal alignment and resampling strategies to join seamlessly with daily US/EU series.
* **Convention harmonization**: day-count conventions differ, and the US/Emerging series are par yields while the ECB AAA spot rates are already zero-coupon. These must be handled differently before any comparison.
* **External macro join**: recession indicators (NBER for the US, CEPR for the Euro Area) and a market-stress index (VIX) are joined by date to the curves, to drive the regime and inversion analysis rather than leaving it descriptive.

---

## Data Sources

### United States Treasury
US Treasury par yield curve rates, including historical CSV archives available from the US Treasury. Source: `home.treasury.gov`.

### FRED
Constant maturity Treasury rates obtained through **FRED** using `pandas-datareader` (or direct API requests), from **1 month to 30 years** (DGS1MO to DGS30). Emerging market sovereign rates for **Mexico and India** (3-month and 10-year maturities) and the VIX series (VIXCLS) are also retrieved here.

### European Central Bank
Euro Area yield curves, including AAA spot rates, retrieved through the ECB **SDMX** data infrastructure. Source: `data.ecb.europa.eu`.

### Recession indicators (external join)
US recession dates (NBER, via FRED series USREC) and Euro Area recession dates (CEPR). At least one of these is retrieved by light web scraping, to cover the scraping component of the project.

---
## Data Challenges

Working with several sources introduces a number of data-quality and reconciliation issues, all treated as a core part of the project:

* Different data formats and shapes
* Non-matching maturity grids
* Different trading calendars and public holidays
* **Daily vs. Monthly frequency alignment (Developed vs. Emerging markets)**
* Missing observations and gaps in time series
* Different day-count conventions
* Par yields versus zero-coupon spot rates
* Potential outliers

---

## Methodology

### 1. Data Ingestion
Each source has its own connector based on an API, an SDMX interface, or programmatic access. No manual download is required. Each connector also **caches the raw pull into `data/raw/`**, so the full pipeline can be re-run and graded even if an API is temporarily unavailable. All sources are transformed into a common structure: `date | maturity | rate | country | source`.

### 2. Cleaning and Reconciliation
* Calendar, date, and frequency alignment across sources (handling daily and monthly data)
* Maturity-grid alignment onto a common grid
* Missing maturity and missing observation handling
* Outlier detection and data validation
* Explicit before/after quality reporting

### 3. Bootstrapping
Par yields (US Treasury, and FRED constant maturity rates for US, Mexico, and India) are transformed into **zero-coupon rates** by a custom bootstrapping algorithm; forward rates are then derived. Day-count conventions are documented and incorporated. ECB AAA spot rates are already zero-coupon and are handled accordingly (no double processing).

### 4. Curve Interpolation and Fitting
Core: linear interpolation, cubic spline, and the **Nelson-Siegel** model.
Stretch (bonus if time allows): **Svensson** model.

### 5. Yield Curve Analysis
* Level, slope and curvature
* Principal Component Analysis of the main factors driving curve movements
* Yield curve inversions and market regimes, using the recession and VIX join
* **US vs. Euro Area vs. Emerging Markets (MX/IN) spread analysis**

---
## Visualization

Core: yield curve charts, time-series views, temporal heatmaps, and an interactive **Streamlit** dashboard.
Stretch (bonus): 3D yield curve surfaces and animations.

---

## Team Organization

To keep the workload fair and make sure everyone learns the full pipeline, work is split **by source rather than by stage**:

* Each member owns one source end to end (US Treasury, FRED including EM extension, ECB): ingestion, cleaning, alignment and, where relevant, bootstrapping of that source.
* The **bootstrapping core** is written together once, since it is the key technical skill.
* Every change lands through a **pull request reviewed by another member**, so each person also learns the others' code.
* A short weekly sync where each member explains what they did.

This way all three members touch every stage of the pipeline.

---

## Tech Stack

Python, with: **pandas** (data manipulation), **NumPy** (numerical computation), **requests** (data collection and light scraping), **pandas-datareader** (FRED access), **SciPy** (interpolation and curve fitting), **Matplotlib** and **Plotly** (visualization), **Streamlit** (dashboard), **Git** (version control).

---
## Repository Structure

```text
yield-curve/
│
├── data/
│   ├── raw/          # cached raw pulls (reproducibility)
│   └── processed/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning_reconciliation.ipynb
│   ├── 03_bootstrapping.ipynb
│   ├── 04_curve_fitting.ipynb
│   ├── 05_analysis.ipynb
│   └── 06_visualization.ipynb
│
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── bootstrapping/
│   ├── fitting/
│   ├── analysis/
│   └── visualization/
│
├── tests/
│
├── dashboard/
│   └── app.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Reproducibility

Reproducibility is a key objective and a graded one. The full pipeline runs from data collection to final visualization without manually downloaded files, and raw pulls are cached in `data/raw/` so results stay consistent. **Running all notebook cells without error is a hard requirement.** Automated tests cover in particular the bootstrapping methodology.

A third party should be able to: install dependencies, run ingestion, reproduce the cleaning and reconciliation, reconstruct the zero-coupon curves, run the analysis, launch the dashboard, and obtain consistent results.

---

## Quality and Validation

The project makes data transformations visible:

* Raw data before cleaning and reconciled data after processing
* Visual evidence of data-quality and alignment improvements
* Validation checks and bootstrapping tests
* Explicit day-count conventions
* No use of future information in historical analysis
* Comparison of multiple curve construction methods

---

## Expected Deliverables

An open-source GitHub repository, reproducible notebooks and code, a documented zero-coupon yield curve dataset, a Streamlit dashboard, a final report, automated tests, and a complete reproducible environment.

---

## Roadmap

| Period     | Milestone                                                     |
| ---------- | ------------------------------------------------------------ |
| Week 1     | Project setup, repository, environment and scope             |
| Weeks 2-3  | Data ingestion and source connectors (with raw caching)      |
| Weeks 3-4  | Cleaning and multi-source reconciliation                     |
| Weeks 4-5  | Bootstrapping and forward rates                              |
| Weeks 5-6  | Interpolation and Nelson-Siegel (Svensson as stretch)        |
| Weeks 6-7  | Yield curve analysis, recession and VIX join, regimes        |
| Weeks 7-8  | Visualization and Streamlit dashboard                        |
| Weeks 8-9  | Reproducibility, testing and repository cleanup              |
| Weeks 9-10 | Final report and presentation                                |

---

## Key Principle

> **Data is the core of the project.**

The main value lies in the quality of the data pipeline: collecting heterogeneous financial data, reconciling it rigorously across sources, transforming it correctly, and presenting the resulting yield curves clearly. The modeling component is intentionally kept focused, while methodological transparency and reproducibility remain central.

---

## Project Theme

**Quantitative Finance: Interest Rate Term Structure / Yield Curve.** Multi-source financial data collection, cleaning and reconciliation, zero-coupon bootstrapping, curve-fitting, market-regime analysis, visualization, and a reproducible dashboard.
