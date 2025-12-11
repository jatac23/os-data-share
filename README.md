# Data Processing Instructions for OpenSolar

This document outlines the process for preparing and processing organization data before securely sharing it with OpenSolar.

## Part 1: Create CSV File

Use the same structure from `input_template.csv` to create your `input.csv` file. The template contains the following headers (keep the headers exactly as specified):

- **Org Name**
- **Org Address**
- **Zip**
- **State**
- **Locality**
- **Country**
- **Phone Number**
- **Company Email**
- **Company Website**

> **Note:** Copy `input_template.csv` and rename it to `input.csv`, then fill in your data. Ensure your CSV file contains data in these columns before proceeding to the next step.

## Part 2: Run Python Data Processing Script

### Prerequisites

Before running the script, install the required dependencies:

```bash
pip install -r requirements.txt
```

### Data Processing Operations

Run the Python hasher file found in this repository (`opensolar_hasher.py`). This script performs the following data cleaning and transformation operations:

#### 1. General Data Cleaning
- Remove multiple spaces
- Trim whitespace from all data fields
- Convert all characters to lowercase

#### 2. Org Name Processing
- Remove all text inside parentheses (e.g., "(PTY)", "(Ltd)")
- Remove common company suffixes (Ltd, Pty, Co., Inc, LLC, Corp, Corporation, Limited, Incorporated, Company, and variations)
  - Handles variations with/without parentheses, periods, and spaces
  - Processes suffixes twice to catch all variations
- Create two derived columns:
  - **Org Name First 5 Letters**: First 5 characters (including spaces)
  - **Org Name Last 5 Characters**: Last 5 characters

#### 3. Org Address Processing
- Remove street type suffixes (Street, St., Avenue, Ave., Road, Rd., and variations)
- Remove commas and periods
- Clean up extra spaces

#### 4. Phone Number Processing
- Remove all non-numerical characters
- Extract the last nine digits

#### 5. Data Normalization
- Replace NaN values with empty strings
- Replace 'nan' strings with empty strings

#### 6. Data Hashing
The following columns are hashed using SHA256 (replacing original values):
- Org Name
- Org Address
- Phone Number
- Company Email
- Company Website
- Org Name First 5 Letters
- Org Name Last 5 Characters

### Running the Script

```bash
python opensolar_hasher.py
```

The script will:
- Read data from `input.csv`
- Process and clean the data according to the operations above
- Save the processed and hashed data to `output-hashed.csv`

## Part 3: Share Data Securely

Share the processed data to OpenSolar using a secure method. Ensure that:

- Data transmission is encrypted
- Access is restricted to authorized personnel only
- Any sensitive information is handled according to your organization's data security policies

---

## Summary

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Create CSV file with required headers and save as `input.csv`
3. ✅ Run Python processing script: `python opensolar_hasher.py`
4. ✅ Share processed data securely to OpenSolar

