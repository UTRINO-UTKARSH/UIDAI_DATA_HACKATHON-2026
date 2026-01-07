import pandas as pd
df = pd.read_csv("data/aadhaar_data.csv")
# df = pd.read_json(file_path.json)
print(df)# this shows the overview of our file

print(df.to_string()) # DON'T RUN FOR LARHE FILES, it will give every thing
