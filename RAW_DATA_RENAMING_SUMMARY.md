# Raw Data Files Renaming Summary

## Overview
All raw data folders and files in `data/raw/` have been renamed to shorter, more meaningful names. All corresponding file paths in the code have been updated.

---

## Folder Renaming

| Old Folder Name | New Folder Name |
|-----------------|-----------------|
| `Aadhaar Biometric Update dataset` | `bio_raw` |
| `Aadhaar Demographic Update dataset` | `demo_raw` |
| `aadhar-enrollment-complete-dataset` | `enroll_raw` |

---

## Biometric Raw Files (`data/raw/bio_raw/`)

| Old Name | New Name | Row Range |
|----------|----------|-----------|
| `api_data_aadhar_biometric_0_500000.csv` | `bio_raw_0_500k.csv` | 0 - 500,000 |
| `api_data_aadhar_biometric_500000_1000000.csv` | `bio_raw_500k_1m.csv` | 500,000 - 1,000,000 |
| `api_data_aadhar_biometric_1000000_1500000.csv` | `bio_raw_1m_1.5m.csv` | 1,000,000 - 1,500,000 |
| `api_data_aadhar_biometric_1500000_1861108.csv` | `bio_raw_1.5m_end.csv` | 1,500,000 - 1,861,108 |

---

## Demographic Raw Files (`data/raw/demo_raw/`)

| Old Name | New Name | Row Range |
|----------|----------|-----------|
| `api_data_aadhar_demographic_0_500000.csv` | `demo_raw_0_500k.csv` | 0 - 500,000 |
| `api_data_aadhar_demographic_500000_1000000.csv` | `demo_raw_500k_1m.csv` | 500,000 - 1,000,000 |
| `api_data_aadhar_demographic_1000000_1500000.csv` | `demo_raw_1m_1.5m.csv` | 1,000,000 - 1,500,000 |
| `api_data_aadhar_demographic_1500000_2000000.csv` | `demo_raw_1.5m_2m.csv` | 1,500,000 - 2,000,000 |
| `api_data_aadhar_demographic_2000000_2071700.csv` | `demo_raw_2m_end.csv` | 2,000,000 - 2,071,700 |

---

## Enrollment Raw Files (`data/raw/enroll_raw/`)

| Old Name | New Name | Row Range |
|----------|----------|-----------|
| `api_data_aadhar_enrolment_0_500000.csv` | `enroll_raw_0_500k.csv` | 0 - 500,000 |
| `api_data_aadhar_enrolment_500000_1000000.csv` | `enroll_raw_500k_1m.csv` | 500,000 - 1,000,000 |
| `api_data_aadhar_enrolment_1000000_1006029.csv` | `enroll_raw_1m_end.csv` | 1,000,000 - 1,006,029 |

---

## Code Updates

All Python files that reference raw data have been updated:

### Active Code Files Updated:
- **bio-time-cleaning.py**: Updated to use `data/raw/bio_raw/bio_raw_*.csv`
- **demo-time-cleaned.py**: Updated to use `data/raw/demo_raw/demo_raw_*.csv`
- **enroll-time-cleaned.py**: Updated to use `data/raw/enroll_raw/enroll_raw_*.csv`
- **aadhar_demographic.py**: Updated commented paths to use `data/raw/demo_raw/demo_raw_*.csv`

### Commented-Out Code Also Updated:
- All commented-out raw file paths in time-based cleaning files have been updated for future reference

---

## Naming Convention

The new naming scheme follows this pattern:
- **`{data_type}_raw_{range}.csv`**

Where:
- **data_type**: `bio` (biometric), `demo` (demographic), `enroll` (enrollment)
- **range**: Indicates the row range of records in the file (e.g., `0_500k`, `500k_1m`, `1m_1.5m`)

This makes it immediately clear:
1. What type of data is in the file
2. That it's raw/unprocessed data
3. Which portion of the complete dataset it contains

---

## Verification

✅ All files successfully renamed
✅ All code file paths updated
✅ Both active and commented-out paths updated
✅ Raw data structure: 3 folders × 4-5 files each = 12 total files renamed
