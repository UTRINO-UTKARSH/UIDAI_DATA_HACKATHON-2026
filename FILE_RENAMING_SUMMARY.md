# File Renaming Summary

## Overview
All data files in the `data/` folder have been renamed to shorter, more meaningful names for better usability and code clarity. All corresponding file paths in the code have been updated accordingly.

---

## File Naming Mapping

### Cleaned Dataset Files (`data/cleaned-dataset/`)
| Old Name | New Name | Purpose |
|----------|----------|---------|
| `aadhar_biometric_district_level_clean.csv` | `bio_clean.csv` | Cleaned biometric data at district level |
| `aadhar_demographic_cleaned.csv` | `demo_clean.csv` | Cleaned demographic data |
| `aadhar_enrollment_cleaned.csv` | `enroll_clean.csv` | Cleaned enrollment data |
| `aadhar_enrollment_final_aggregated.csv` | `enroll_agg.csv` | Aggregated enrollment data |
| `aadhar_enrollment_stage1_clean.csv` | `enroll_stage1.csv` | Enrollment data stage 1 cleaning |

### Final Cleaned Files (`data/final_cleaned/`)
| Old Name | New Name | Purpose |
|----------|----------|---------|
| `aadhar_biometric_district_level_FINAL_LGD_RESOLVED.csv` | `bio_final.csv` | Final biometric data (LGD resolved) |
| `aadhar_demographic_full.csv` | `demo_final.csv` | Final demographic data |
| `aadhar_enrollment_fully_resolved.csv` | `enroll_final.csv` | Final enrollment data (fully resolved) |

### Time Series Data - Biometric (`data/time_seperation/biometric/`)
| Old Name | New Name | Purpose |
|----------|----------|---------|
| `final_padded_bio_time_series.csv` | `bio_time_padded.csv` | Padded biometric time series |
| `final_time_bio_series_resolved.csv` | `bio_time_final.csv` | Final biometric time series (resolved) |

### Time Series Data - Demographic (`data/time_seperation/demographic/`)
| Old Name | New Name | Purpose |
|----------|----------|---------|
| `final_padded_demo_time_series.csv` | `demo_time_padded.csv` | Padded demographic time series |
| `final_time_demo_series_resolved.csv` | `demo_time_final.csv` | Final demographic time series (resolved) |

### Time Series Data - Enrollment (`data/time_seperation/enroll/`)
| Old Name | New Name | Purpose |
|----------|----------|---------|
| `final_padded_time_series.csv` | `enroll_time_padded.csv` | Padded enrollment time series |
| `final_time_series_resolved.csv` | `enroll_time_final.csv` | Final enrollment time series (resolved) |

---

## Code Updates

All Python files have been updated with the new file paths:

### Analysis Procedure Files
- **demographic_analysis.py**: Updated to use `demo_time_final.csv`
- **biometric_analysis.py**: Updated to use `bio_final.csv`
- **Aadhar_enrollement_analysis.py**: Updated to use `enroll_final.csv`

### Data Cleaning Files
- **biometric_cleaning.py**: Updated input to `bio_clean.csv`, output to `bio_final.csv`
- **aadhar_demographic.py**: Updated input to `demo_clean.csv`, output to `demo_final.csv`
- **Aadhar_enrollemnnt-cleaned.py**: Updated input/output to `enroll_final.csv`

### Time-Based Cleaning Files
- **bio-time-cleaning.py**: Updated to use `bio_time_padded.csv` and `bio_time_final.csv`
- **demo-time-cleaned.py**: Updated to use `demo_time_padded.csv` and `demo_time_final.csv`
- **enroll-time-cleaned.py**: Updated to use `enroll_time_padded.csv` and `enroll_time_final.csv`

---

## Naming Convention

The new naming scheme follows this pattern:
- **`{data_type}_{descriptor}.csv`**

Where:
- **data_type**: `bio` (biometric), `demo` (demographic), `enroll` (enrollment)
- **descriptor**: 
  - `clean` = cleaned data
  - `final` = final processed data
  - `agg` = aggregated data
  - `stage1` = stage 1 processing
  - `time_padded` = time series with padding
  - `time_final` = time series final version

This naming convention makes it immediately clear what each file contains and improves code readability.
