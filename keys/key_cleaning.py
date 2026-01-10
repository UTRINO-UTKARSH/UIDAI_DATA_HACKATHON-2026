import pandas as pd
import re

# ======================================================
# Step 1: Load CSV
# ======================================================
file_path = "keys/district_master_key.csv"
df = pd.read_csv(file_path)

# ======================================================
# Step 2: Remove unnecessary columns
# ======================================================
df = df.drop(columns=["S No", "State Code"], errors="ignore")

# ======================================================
# Step 3: Rename columns (standard names)
# ======================================================
df = df.rename(columns={
    "State Name": "state",
    "District Name (In English)": "district_standard",
    "District LGD Code": "district_lgd_code"
})

# ======================================================
# Step 4: Text normalization functions
# ======================================================
def normalize_state(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"\(state\)", "", text)   # remove '(state)'
    text = re.sub(r"\bstate\b", "", text)   # remove 'state'
    text = re.sub(r"[^a-z\s]", " ", text)   # remove special chars
    text = re.sub(r"\s+", " ", text)        # collapse spaces
    return text.strip()

def normalize_district(text):
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ======================================================
# Step 5: Apply normalization
# ======================================================
df["state_norm"] = df["state"].apply(normalize_state)
df["district_standard"] = df["district_standard"].apply(normalize_district)

# ======================================================
# Step 6: Remove empty / invalid rows
# ======================================================
df = df[
    (df["state_norm"] != "") &
    (df["district_standard"] != "")
]

# ======================================================
# Step 7: Deduplicate (very important)
# ======================================================
df = df.drop_duplicates(
    subset=["state_norm", "district_standard"]
)

# ======================================================
# Step 8: Final selection of columns
# ======================================================
df_final = df[[
    "state_norm",
    "district_standard",
    "district_lgd_code"
]]

# ======================================================
# Step 9: Inspect result
# ======================================================
print("Final columns:", df_final.columns.tolist())
print("Total districts:", len(df_final))
print(df_final.head(10))

# ======================================================
# Step 10: Save canonical district master
# ======================================================
output_path = "keys/district_master.csv"
df_final.to_csv(output_path, index=False)

print(f"\nDistrict master saved to: {output_path}")
