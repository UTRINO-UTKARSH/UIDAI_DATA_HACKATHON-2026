# UIDAI Data Hackathon 2026  
## Aadhaar Enrolment Analysis – Societal Trends & Insights

---

## 📌 Project Overview

This project is developed as part of the **UIDAI Data Hackathon 2026**.  
The objective of this study is to analyze **Aadhaar enrolment patterns across India** using age-wise data collected at the enrolment-centre (pincode) level and aggregated to district, state, and pan-India levels.

By studying enrolment trends across different age groups and geographies, the project aims to uncover **societal trends**, identify **regional variations**, and generate **actionable insights** that can support UIDAI’s planning, outreach, and infrastructure decisions.

---

## 🎯 Problem Statement

> To analyze age-wise Aadhaar enrolment patterns across India using district-level data aggregated to state and national levels, in order to identify societal trends and derive insights relevant to UIDAI’s operational and policy planning.

---

## 📊 Dataset Description

### Primary Dataset: Aadhaar Enrolment Data

The raw data contains Aadhaar enrolment counts recorded at enrolment centres (identified by **pincode**), along with associated **state**, **district**, and **date** information.

Each row represents:
- Enrolments at a specific Aadhaar centre (pincode)
- On a given date
- Split into age groups:
  - `age_0_5`
  - `age_5_17`
  - `age_18_greater`

Due to API size limits, the dataset is provided in **multiple CSV files**, which are combined during preprocessing.

---

## 🗂️ Project Structure

# Project Directory Structure

graph TD
    %% Root Directory
    UIDAI[UIDAI/]

    %% First Level
    UIDAI --> code[code/]
    UIDAI --> data[data/]
    UIDAI --> output[output/]
    UIDAI --> README[README.md]
    UIDAI --> ignore[.gitignore]

    %% Code Sub-folders
    code --> clean[cleaning-data/]
    code --> analysis[analysis_procedure/]
    code --> experiments[experiments/]
    
    %% Files in cleaning-data
    clean --> py[Aadhar-enrollment.py]

    %% Data Sub-folders
    data --> raw[raw/]
    data --> cleaned[cleaned-dataset/]

    %% Styling
    style UIDAI fill:#f9f,stroke:#333,stroke-width:2px
    style README fill:#fff,stroke-dasharray: 5 5
    style ignore fill:#fff,stroke-dasharray: 5 5


---

## 🔄 Methodology

1. **Data Loading**
   - Multiple Aadhaar enrolment CSV files are loaded and concatenated.

2. **Data Cleaning**
   - Standardization of column names
   - Handling missing or invalid values
   - Conversion of date fields
   - Removal of duplicate records where applicable

3. **Aggregation**
   - Pincode → District
   - District → State
   - State → Pan-India

4. **Analysis**
   - Age-group-wise enrolment distribution
   - State-level comparisons
   - Identification of enrolment trends and variations

5. **Visualization**
   - Bar charts and summary tables for clear interpretation

---

## 🧪 Tools & Technologies Used

- **Python**
- **Pandas** – data loading, cleaning, aggregation
- **Matplotlib / Seaborn** – visualizations (used during analysis)
- **Git & GitHub** – version control and collaboration

---

## ▶️ How to Run the Code

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd UIDAI

2. Install Necessary Modules of python
```bash
   pip install pandas matplotlib seaborn

