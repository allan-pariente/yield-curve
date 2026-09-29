# Yield Curve Analysis

## Overview

This project focuses on the **construction, cleaning, transformation, and analysis of interest rate yield curves**, from raw public data to a reproducible dashboard.

The main objective is not to build a complex predictive model, but to demonstrate the importance of **high-quality financial data**, robust data processing, and clear visualization.

The project compares yield curves across the **United States and the Euro Area**, transforms par yields into **zero-coupon rates using bootstrapping**, and studies how the term structure evolves over time.

---

## Research Question

> How can we reconstruct clean and comparable zero-coupon yield curves from heterogeneous public data sources, and what can their evolution tell us about market regimes, yield curve steepening, inversions, and crisis periods?

---

## Project Objectives

The project follows a complete data pipeline:

1. **Collect** yield curve data from multiple public sources.
2. **Standardize** heterogeneous datasets into a common schema.
3. **Clean and validate** the data.
4. **Bootstrap** par yields into zero-coupon rates.
5. **Extract forward rates** from the resulting curves.
6. **Compare interpolation and curve-fitting methods.**
7. **Analyze** level, slope, and curvature factors.
8. **Compare** the US and Euro Area yield curves.
9. **Visualize** the evolution of the term structure.
10. **Provide** a reproducible Streamlit dashboard.

---

## Data Sources

The project relies on several public sources:

### United States Treasury

US Treasury par yield curve rates, including historical CSV archives available from the US Treasury.

**Source:** `home.treasury.gov`

### FRED

Constant maturity Treasury rates obtained through **FRED** using `pandas-datareader`.

The project considers maturities ranging from **1 month to 30 years** (DGS1MO to DGS30).

### European Central Bank

Euro Area yield curves, including AAA spot rates, retrieved through the ECB's **SDMX** data infrastructure.

**Source:** `data.ecb.europa.eu`

---

## Data Challenges

Working with several sources introduces a number of data-quality issues:

* Different data formats
* Non-matching maturities
* Different trading calendars
* Public holidays
* Missing observations
* Gaps in time series
* Different day-count conventions
* Potential outliers

These issues are treated as a core part of the project rather than as a secondary preprocessing step.

---

## Methodology

### 1. Data Ingestion

Each source has its own connector based on an API, SDMX interface, or programmatic data access.

All sources are transformed into a common structure:

```text
date | maturity | rate
```

No manual data download is required.

---

### 2. Data Cleaning and Quality Control

The cleaning pipeline includes:

* Calendar alignment
* Missing maturity handling
* Missing observation handling
* Outlier detection
* Data validation
* Before/after quality reporting

The objective is to make the cleaning process transparent and reproducible.

---

### 3. Bootstrapping

Par yields are transformed into **zero-coupon rates** using a bootstrapping procedure.

The resulting zero-coupon curve is then used to derive **forward rates**.

Day-count conventions are explicitly documented and incorporated into the transformation process.

---

### 4. Curve Interpolation and Fitting

Several approaches are compared:

* Linear interpolation
* Cubic spline interpolation
* Nelson-Siegel model
* Svensson model

The goal is to show how the choice of interpolation or fitting method affects the resulting yield curve.

---

### 5. Yield Curve Analysis

The project investigates:

* **Level**
* **Slope**
* **Curvature**
* Yield curve inversions
* Market regimes
* Relationship between yield curve movements and recession periods
* Differences between the US and Euro Area term structures

Principal Component Analysis (PCA) is used to study the main factors driving yield curve movements.

---

## Visualization

The project includes several visualization formats:

* Yield curve charts
* Time-series analysis
* Temporal heatmaps
* 3D yield curve surfaces
* Yield curve animations
* Interactive Streamlit dashboard

The visualizations are designed to make changes in the term structure easy to identify over time.

---

## Project Pipeline

```text
Public Data Sources
        │
        ▼
     Ingestion
        │
        ▼
 Data Standardization
        │
        ▼
 Cleaning & Quality Control
        │
        ▼
    Bootstrapping
        │
        ▼
 Zero-Coupon Curves
        │
        ├──────────────► Forward Rates
        │
        ▼
Interpolation & Curve Fitting
        │
        ├── Linear
        ├── Cubic Spline
        ├── Nelson-Siegel
        └── Svensson
        │
        ▼
     Analysis
        │
        ├── Level
        ├── Slope
        ├── Curvature
        ├── PCA
        └── Regime Analysis
        │
        ▼
 Visualization & Dashboard
```

---

## Tech Stack

The project is built with Python and uses:

* **Python**
* **pandas** — data manipulation
* **NumPy** — numerical computation
* **requests** — data collection
* **pandas-datareader** — FRED data access
* **SciPy** — interpolation and curve fitting
* **Matplotlib** — static visualizations
* **Plotly** — interactive visualizations
* **Streamlit** — interactive dashboard
* **Git** — version control

---

## Repository Structure

```text
yield-curve-analysis/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
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

Reproducibility is a key objective of the project.

The full pipeline should be executable from raw data collection to final visualization without relying on manually downloaded files.

A third party should be able to:

1. Install the required dependencies.
2. Run the data ingestion pipeline.
3. Reproduce the cleaning process.
4. Reconstruct the zero-coupon curves.
5. Run the analysis.
6. Launch the Streamlit dashboard.
7. Obtain consistent results.

Automated tests are also included, particularly for the bootstrapping methodology.

---

## Quality and Validation

A major focus of the project is making data transformations visible.

The project therefore aims to provide:

* Raw data before cleaning
* Cleaned data after processing
* Visual evidence of data-quality improvements
* Validation checks
* Bootstrapping tests
* Explicit day-count conventions
* No use of future information in historical analysis
* Comparison of multiple curve construction methods

---

## Expected Deliverables

The final project will include:

* An open-source GitHub repository
* Reproducible notebooks and code
* A documented zero-coupon yield curve dataset
* A Streamlit dashboard
* A final report
* Automated tests
* A complete reproducible environment

---

## Roadmap

| Period     | Milestone                                         |
| ---------- | ------------------------------------------------- |
| Week 1     | Project setup, repository, environment and scope  |
| Weeks 2–3  | Data ingestion and source connectors              |
| Weeks 3–4  | Data cleaning and quality control                 |
| Weeks 4–5  | Bootstrapping and forward rates                   |
| Weeks 5–6  | Interpolation and Nelson-Siegel / Svensson models |
| Weeks 6–7  | Yield curve analysis                              |
| Weeks 7–8  | Visualization and Streamlit dashboard             |
| Weeks 8–9  | Reproducibility, testing and repository cleanup   |
| Weeks 9–10 | Final report and presentation                     |

---

## Key Principle

> **Data is the core of the project.**

The main value of this project lies in the quality of the data pipeline: collecting heterogeneous financial data, cleaning it rigorously, transforming it correctly, and presenting the resulting yield curves clearly.

The modeling component is intentionally kept focused, while methodological transparency and reproducibility remain central.

---

## Project Theme

**Quantitative Finance — Interest Rate Term Structure / Yield Curve**

The project combines multi-source financial data collection, data cleaning, zero-coupon bootstrapping, curve-fitting methods, market-regime analysis, visualization, and a reproducible dashboard.
